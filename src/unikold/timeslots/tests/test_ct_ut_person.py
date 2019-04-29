# -*- coding: utf-8 -*-
from datetime import date
from unikold.timeslots.content.ut_person import IUTPerson  # NOQA E501
from unikold.timeslots.testing import UNIKOLD_TIMESLOTS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.app.testing import login
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer.interfaces import IIDNormalizer
from unikold.timeslots.utils import emailToPersonId
from zope.component import createObject
from zope.component import getUtility
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
            {'username': 'plustig', 'email': 'peter@lustig.org',
             'prename': 'Peter', 'surname': 'Lustig'},
            {'username': 'rsanchez', 'email': 'rick@c137.org',
             'prename': 'Rick', 'surname': 'Sanchez'}
        ]

        for user in self.users:
            api.user.create(
                email=user['email'], username=user['username'])

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
        obj = self.createPerson(self.parent, self.users[0])

        self.assertEqual(obj.id, emailToPersonId(self.users[0]['email']))
        title = self.users[0]['prename'] + ' ' + self.users[0]['surname']
        self.assertEqual(obj.Title(), title)

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

        self.assertEqual(
            signupsheet.countSlotsByEmail(self.users[0]['email']),
            1)
        self.assertEqual(
            signupsheet.countSlotsByEmail(self.users[0]['email'], 'signedup'),
            1)
        self.assertEqual(
            signupsheet.countSlotsByEmail(self.users[0]['email'], 'signedoff'),
            0)

    def test_waiting_list(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        (signupsheet, day, timeslot, person) = self.createFullStack()
        self.assertTrue(signupsheet.enableAutoMovingUpFromWaitingList)
        self.assertEqual(timeslot.maxCapacity, 1)

        person2 = self.createPerson(timeslot, self.users[1])

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

        self.assertEqual(signupsheet.getSlotsOfCurrentUser(), [])
        self.assertEqual(timeslot.getCurrentUserSignUpState(), False)

        login(self.portal, self.users[0]['username'])
        self.assertEqual(len(signupsheet.getSlotsOfCurrentUser()), 1)
        self.assertEqual(timeslot.getCurrentUserSignUpState(), 'signedoff')
        self.assertFalse(timeslot.isUserSignedUpForThisSlot(self.users[0]['email']))

        login(self.portal, self.users[1]['username'])
        self.assertEqual(len(signupsheet.getSlotsOfCurrentUser()), 1)
        self.assertEqual(timeslot.getCurrentUserSignUpState(), 'signedup')
        self.assertTrue(timeslot.isUserSignedUpForThisSlot(self.users[1]['email']))

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
        today = date.today()
        try:
            day = api.content.create(
                container=signupsheet,
                type='UTDay',
                id='ut_day',
                **{
                    'date': today
                }
            )
        except AttributeError:
            # strange behavior caused by autoSetID
            # object is created but AttributeError is raised
            title = today.strftime('%d.%m.%Y')
            normalizer = getUtility(IIDNormalizer)
            newId = normalizer.normalize(title)
            day = getattr(signupsheet, newId)

        timeslot = api.content.create(
            container=day,
            type='UTTimeslot',
            id='ut_timeslot'
        )
        person = self.createPerson(timeslot, self.users[0])
        return (signupsheet, day, timeslot, person)

    def createPerson(self, container, data):
        try:
            obj = api.content.create(
                container=container,
                type='UTPerson',
                id=data['email'],
                **data
            )
        except AttributeError:
            # strange behavior caused by autoSetID
            # object is created but AttributeError is raised
            obj = getattr(container, emailToPersonId(data['email']))

        return obj

    def assertWfState(self, state, object):
        actualState = api.content.get_state(object)
        self.assertEqual(state, actualState)
