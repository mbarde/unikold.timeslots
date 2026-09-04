# -*- coding: utf-8 -*-
"""Setup tests for this package."""
from plone import api
from plone.app.testing import setRoles
from plone.app.testing import TEST_USER_ID
from plone.base.utils import get_installer
from unikold.timeslots.testing import UNIKOLD_TIMESLOTS_INTEGRATION_TESTING  # noqa

import unittest


class TestSetup(unittest.TestCase):
    """Test that unikold.timeslots is properly installed."""

    layer = UNIKOLD_TIMESLOTS_INTEGRATION_TESTING

    def setUp(self):
        """Custom shared utility setup for tests."""
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])

    def test_product_installed(self):
        """Test if unikold.timeslots is installed."""
        self.assertTrue(self.installer.is_product_installed(
            'unikold.timeslots'))

    def test_browserlayer(self):
        """Test that IUnikoldTimeslotsLayer is registered."""
        from unikold.timeslots.interfaces import (
            IUnikoldTimeslotsLayer)
        from plone.browserlayer import utils
        self.assertIn(
            IUnikoldTimeslotsLayer,
            utils.registered_layers())


class TestUninstall(unittest.TestCase):

    layer = UNIKOLD_TIMESLOTS_INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.installer = get_installer(self.portal, self.layer['request'])
        roles_before = api.user.get_roles(TEST_USER_ID)
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.installer.uninstall_product('unikold.timeslots')
        setRoles(self.portal, TEST_USER_ID, roles_before)

    def test_product_uninstalled(self):
        """Test if unikold.timeslots is cleanly uninstalled."""
        self.assertFalse(self.installer.is_product_installed(
            'unikold.timeslots'))

    def test_browserlayer_removed(self):
        """Test that IUnikoldTimeslotsLayer is removed."""
        from unikold.timeslots.interfaces import \
            IUnikoldTimeslotsLayer
        from plone.browserlayer import utils
        self.assertNotIn(
            IUnikoldTimeslotsLayer,
            utils.registered_layers())
