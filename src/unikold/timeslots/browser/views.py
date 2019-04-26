# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser.view import DefaultView
from Products.CMFPlone.resources import add_resource_on_request
from Products.Five import BrowserView


class UTSignupSheetView(DefaultView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        # load JS resources
        add_resource_on_request(self.request, 'unikold.timeslots')
        return super(UTSignupSheetView, self).__call__()

    def showEditLinks(self):
        return api.user.has_permission('unikold.timeslots: Manage Schedule')

    def renderExtraForm(self):
        return ''


class ShowReservationsView(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def __call__(self):
        if api.user.is_anonymous():
            self.request.response.redirect(
                self.context.absolute_url()
                + '/login_form?came_from=./@@show-reservations')
        else:
            # load JS resources
            add_resource_on_request(self.request, 'unikold.timeslots')
            return super(ShowReservationsView, self).__call__()


class UTDayView(DefaultView):
    pass


class UTTimeslotView(DefaultView):
    pass
