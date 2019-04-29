# -*- coding: utf-8 -*-
from unikold.timeslots.content.ut_timeslot import IUTTimeslot  # NOQA E501
from unikold.timeslots.testing import UNIKOLD_TIMESLOTS_INTEGRATION_TESTING  # noqa
from plone import api
from plone.api.exc import InvalidParameterError
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


class UTTimeslotIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_TIMESLOTS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'UTDay',
            self.portal,
            'ut_timeslot',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_ut_timeslot_schema(self):
        fti = queryUtility(IDexterityFTI, name='UTTimeslot')
        schema = fti.lookupSchema()
        self.assertEqual(IUTTimeslot, schema)

    def test_ct_ut_timeslot_fti(self):
        fti = queryUtility(IDexterityFTI, name='UTTimeslot')
        self.assertTrue(fti)

    def test_ct_ut_timeslot_factory(self):
        fti = queryUtility(IDexterityFTI, name='UTTimeslot')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IUTTimeslot.providedBy(obj),
            u'IUTTimeslot not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_ut_timeslot_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        maxCapacity = 42
        obj = api.content.create(
            container=self.parent,
            type='UTTimeslot',
            id='ut_timeslot',
            **{
                'maxCapacity': maxCapacity
            }
        )

        self.assertEqual(obj.getNumberOfAvailableSlots(), maxCapacity)
        self.assertFalse(obj.isFull())

        self.assertTrue(
            IUTTimeslot.providedBy(obj),
            u'IUTTimeslot not provided by {0}!'.format(
                obj.id,
            ),
        )

    def test_ct_ut_timeslot_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UTTimeslot')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_ut_timeslot_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UTTimeslot')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'ut_timeslot_id',
            title='UTTimeslot container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
