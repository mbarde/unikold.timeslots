# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import INonInstallable
from zope.interface import implementer


@implementer(INonInstallable)
class HiddenProfiles(object):

    def getNonInstallableProfiles(self):
        """Hide uninstall profile from site-creation and quickinstaller."""
        return [
            'unikold.timeslots:uninstall',
        ]


def post_install(context):
    # which types to display in navigation?
    typesInNav = list(api.portal.get_registry_record('plone.displayed_types'))

    whitelist = ['UTSignupSheet']
    for typeName in whitelist:
        if typeName not in typesInNav:
            typesInNav.append(typeName)

    blacklist = ['UTDay', 'UTTimeslot', 'UTPerson']
    for typeName in blacklist:
        if typeName in typesInNav:
            typesInNav.remove(typeName)

    api.portal.set_registry_record('plone.displayed_types', tuple(typesInNav))


def uninstall(context):
    """Uninstall script"""
    # Do something at the end of the uninstallation of this package.
