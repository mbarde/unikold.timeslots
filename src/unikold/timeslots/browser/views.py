# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.browser.view import DefaultView
from Products.CMFPlone.resources import add_resource_on_request
from Products.Five import BrowserView
from unikold.timeslots import _
from unikold.timeslots.utils import translateReviewState

import re


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
        portal = api.portal.get()

        form = self.context.extraFieldsForm
        if form is None:
            return ''
        formObj = form.to_object

        formPath = '/'.join(formObj.getPhysicalPath())
        formView = portal.restrictedTraverse(formPath + '/@@embedded')

        # remove form opening and closing tag, submit button and h-tags with content
        # (since we want to embed input fields into existing form)
        # also replace class 'blurrable' since this toggles inline_validation.js
        # which does not work here
        formHTML = formView()
        toRemove = ['<form.*?>', '</form.*?>', '<.*name="form_submit".*?>',
                    '<h[1-9]>.*</h[1-9]>', 'blurrable']
        formHTML = re.sub('|'.join(toRemove), '', formHTML)
        return formHTML


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


class ManagerSummaryView(DefaultView):

    def getReviewState(self, obj):
        return api.content.get_state(obj)

    def getReviewStateTitle(self, obj):
        state = api.content.get_state(obj)
        return translateReviewState(state)


class UTDayView(DefaultView):
    pass


class UTTimeslotView(DefaultView):
    pass


class UTPersonView(DefaultView):

    def getCurrentState(self):
        state = api.content.get_state(self.context)
        if state == 'signedup':
            return (_(u'Signed Up'), 'bg-success')
        elif state == 'unconfirmed':
            return (_(u'Waiting for confirmation'), 'bg-warning')
        elif state == 'signedoff':
            return (_(u'Signed off'), 'bg-danger')
        elif state == 'waiting':
            return (_(u'Waiting List'), 'bg-info')
