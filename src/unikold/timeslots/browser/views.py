# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser.view import DefaultView


class UTSignupSheetView(DefaultView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def showEditLinks(self):
        return api.user.has_permission('unikold.timeslots: Manage Schedule')

    def renderExtraForm(self):
        return ''


class UTDayView(DefaultView):
    pass


class UTTimeslotView(DefaultView):
    pass
