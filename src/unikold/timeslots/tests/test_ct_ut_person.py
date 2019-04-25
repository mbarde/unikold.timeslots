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

        # build full `stack`: [Signup Sheet] -> [Day] -> [Timeslot] -> [Person]
        signupsheet = api.content.create(
            container=self.portal,
            type='UTSignupSheet',
            id='ut_signup_sheet',
            **{
                'contactInfo': 'manager@test.com',
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
            id='ut_timeslot',
        )
        obj = api.content.create(
            container=timeslot,
            type='UTPerson',
            id='ut_person',
            **{
                'email': 'user@test.com',
                'prename': 'Peter',
                'surname': 'Lustig'
            }
        )

        self.assertEqual(len(self.portal.MailHost.messages), 0)
        actualState = api.content.get_state(obj)
        self.assertEqual('unconfirmed', actualState)
        api.content.transition(obj=obj, transition='signoff')
        self.assertEqual(len(self.portal.MailHost.messages), 1)

        actualState = api.content.get_state(obj)
        self.assertEqual('signedoff', actualState)
        api.content.transition(obj=obj, transition='putOnWaitingList')
        self.assertEqual(len(self.portal.MailHost.messages), 3)

        actualState = api.content.get_state(obj)
        self.assertEqual('waiting', actualState)
        api.content.transition(obj=obj, transition='signup')
        self.assertEqual(len(self.portal.MailHost.messages), 5)

        actualState = api.content.get_state(obj)
        self.assertEqual('signedup', actualState)

    def test_ct_ut_person_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UTPerson')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )
