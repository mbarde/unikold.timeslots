# -*- coding: utf-8 -*-
from unikold.timeslots.content.ut_person import IUTPerson  # NOQA E501
from unikold.timeslots.testing import UNIKOLD_TIMESLOTS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from zope.component import createObject
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class UTPersonIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_TIMESLOTS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'UTTimeslot',
            self.portal,
            'ut_person',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

        self.emailManager = 'manager@plone.org'
        self.users = [
            {'email': 'peter@lustig.org', 'prename': 'Peter', 'surname': 'Lustig'},
            {'email': 'rick@c137.org', 'prename': 'Rick', 'surname': 'Sanchez'}
        ]

    def test_ct_ut_person_schema(self):
        fti = queryUtility(IDexterityFTI, name='UTPerson')
        schema = fti.lookupSchema()
        self.assertEqual(IUTPerson, schema)

    def test_ct_ut_person_fti(self):
        fti = queryUtility(IDexterityFTI, name='UTPerson')
        self.assertTrue(fti)

    def test_ct_ut_person_factory(self):
        fti = queryUtility(IDexterityFTI, name='UTPerson')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IUTPerson.providedBy(obj),
            u'IUTPerson not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_ut_person_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        obj = api.content.create(
            container=self.parent,
            type='UTPerson',
            id='ut_person',
        )

        self.assertTrue(
            IUTPerson.providedBy(obj),
            u'IUTPerson not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_notifications(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        (signupsheet, day, timeslot, person) = self.createFullStack()

        self.assertEqual(len(self.portal.MailHost.messages), 0)
        self.assertWfState('unconfirmed', person)
        api.content.transition(obj=person, transition='signoff')
        self.assertNewMailContains(self.users[0]['email'], ['Cancellation', 'Notification'])
        self.assertEqual(timeslot.getNumberOfAvailableSlots(), 1)

        self.assertWfState('signedoff', person)
        api.content.transition(obj=person, transition='putOnWaitingList')
        self.assertEqual(len(self.portal.MailHost.messages), 2)
        self.assertNewMailContains(
            self.users[0]['email'], ['Waiting', 'List', 'Confirmation'],
            self.portal.MailHost.messages[0])
        self.assertNewMailContains(
            self.emailManager, ['Waiting', 'List', 'Notification'],
            self.portal.MailHost.messages[1])
        self.portal.MailHost.messages = []
        self.assertEqual(timeslot.getNumberOfAvailableSlots(), 1)

        self.assertWfState('waiting', person)
        api.content.transition(obj=person, transition='signup')
        self.assertEqual(len(self.portal.MailHost.messages), 2)
        self.assertNewMailContains(
            self.users[0]['email'], ['Registration', 'Confirmation'],
            self.portal.MailHost.messages[0])
        self.assertNewMailContains(
            self.emailManager, ['Registration', 'Notification'],
            self.portal.MailHost.messages[1])
        self.portal.MailHost.messages = []
        self.assertEqual(timeslot.getNumberOfAvailableSlots(), 0)

        self.assertWfState('signedup', person)

    def test_waiting_list(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        (signupsheet, day, timeslot, person) = self.createFullStack()
        self.assertTrue(signupsheet.enableAutoMovingUpFromWaitingList)
        self.assertEqual(timeslot.maxCapacity, 1)

        person2 = api.content.create(
            container=timeslot,
            type='UTPerson',
            id='ut_person',
            safe_id=True,
            **{
                'email': self.users[1]['email'],
                'prename': self.users[1]['prename'],
                'surname': self.users[1]['surname']
            }
        )

        api.content.transition(obj=person, transition='signup')
        api.content.transition(obj=person2, transition='putOnWaitingList')
        self.assertEqual(timeslot.getNumberOfAvailableSlots(), 0)

        self.assertWfState('signedup', person)
        self.assertWfState('waiting', person2)

        #  signedup person gets signed off -> person from waiting list
        #                                     should become signed up
        api.content.transition(obj=person, transition='signoff')
        self.assertWfState('signedoff', person)
        self.assertWfState('signedup', person2)

    def test_ct_ut_person_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UTPerson')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def assertNewMailContains(self, recipient, contents, message=False):
        clearAll = False
        if not message:
            self.assertEqual(len(self.portal.MailHost.messages), 1)
            message = self.portal.MailHost.messages[0]
            clearAll = True

        self.assertIn('To: {0}'.format(recipient), message)

        for content in contents:
            self.assertIn(content, message)

        if clearAll:
            self.portal.MailHost.messages = []

    # create full `stack`: [Signup Sheet] -> [Day] -> [Timeslot] -> [Person]
    def createFullStack(self, container=False):
        if container is False:
            container = self.portal

        signupsheet = api.content.create(
            container=container,
            type='UTSignupSheet',
            id='ut_signup_sheet',
            **{
                'contactInfo': self.emailManager,
                'notifyContactInfo': True
            }
        )
        day = api.content.create(
            container=signupsheet,
            type='UTDay',
            id='ut_day',
        )
        timeslot = api.content.create(
            container=day,
            type='UTTimeslot',
            id='ut_timeslot'
        )
        person = api.content.create(
            container=timeslot,
            type='UTPerson',
            id='ut_person',
            **{
                'email': self.users[0]['email'],
                'prename': self.users[0]['prename'],
                'surname': self.users[0]['surname']
            }
        )
        return (signupsheet, day, timeslot, person)

    def assertWfState(self, state, object):
        actualState = api.content.get_state(object)
        self.assertEqual(state, actualState)
