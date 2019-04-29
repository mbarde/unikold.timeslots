# -*- coding: utf-8 -*-
from datetime import date
from plone import api
from plone.api.exc import InvalidParameterError
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.dexterity.interfaces import IDexterityFTI
from plone.i18n.normalizer.interfaces import IIDNormalizer
from unikold.timeslots.content.ut_day import IUTDay  # NOQA E501
from unikold.timeslots.testing import UNIKOLD_TIMESLOTS_INTEGRATION_TESTING  # noqa
from zope.component import createObject
from zope.component import getUtility
from zope.component import queryUtility

import unittest


try:
    from plone.dexterity.schema import portalTypeToSchemaName
except ImportError:
    # Plone < 5
    from plone.dexterity.utils import portalTypeToSchemaName  # noqa: F401


class UTDayIntegrationTest(unittest.TestCase):

    layer = UNIKOLD_TIMESLOTS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            'UTSignupSheet',
            self.portal,
            'ut_day',
            title='Parent container',
        )
        self.parent = self.portal[parent_id]

    def test_ct_ut_day_schema(self):
        fti = queryUtility(IDexterityFTI, name='UTDay')
        schema = fti.lookupSchema()
        self.assertEqual(IUTDay, schema)

    def test_ct_ut_day_fti(self):
        fti = queryUtility(IDexterityFTI, name='UTDay')
        self.assertTrue(fti)

    def test_ct_ut_day_factory(self):
        fti = queryUtility(IDexterityFTI, name='UTDay')
        factory = fti.factory
        obj = createObject(factory)

        self.assertTrue(
            IUTDay.providedBy(obj),
            u'IUTDay not provided by {0}!'.format(
                obj,
            ),
        )

    def test_ct_ut_day_adding(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        today = date.today()
        try:
            obj = api.content.create(
                container=self.parent,
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
            obj = getattr(self.parent, newId)

        self.assertTrue(
            IUTDay.providedBy(obj),
            u'IUTDay not provided by {0}!'.format(
                obj.id,
            ),
        )

        self.assertEqual(obj.getTimeSlots(), [])

    def test_ct_ut_day_globally_not_addable(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UTDay')
        self.assertFalse(
            fti.global_allow,
            u'{0} is globally addable!'.format(fti.id)
        )

    def test_ct_ut_day_filter_content_type_true(self):
        setRoles(self.portal, TEST_USER_ID, ['Contributor'])
        fti = queryUtility(IDexterityFTI, name='UTDay')
        portal_types = self.portal.portal_types
        parent_id = portal_types.constructContent(
            fti.id,
            self.portal,
            'ut_day_id',
            title='UTDay container',
         )
        self.parent = self.portal[parent_id]
        with self.assertRaises(InvalidParameterError):
            api.content.create(
                container=self.parent,
                type='Document',
                title='My Content',
            )
