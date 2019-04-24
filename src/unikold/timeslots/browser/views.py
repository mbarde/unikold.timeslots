# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser.view import DefaultView


class UTSignupSheetView(DefaultView):

    def isCurrentUserLoggedIn(self):
        return not api.user.is_anonymous()

    def showEditLinks(self):
        return False
