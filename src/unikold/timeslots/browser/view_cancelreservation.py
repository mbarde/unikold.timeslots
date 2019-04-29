# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import ILanguage
from Products.Five import BrowserView
from Products.validation import validation
from unikold.timeslots import _
from unikold.timeslots.utils import ploneUserToPersonId
from z3c.caching.purge import Purge
from zope.event import notify
from zope.i18n import translate


class CancelReservation(BrowserView):

    def __init__(self, context, request):
        self.context = context
        self.request = request

    # notification for manager at this point (and not in subscribers.py)
    # since we only want to inform the manager if user signed off on his own
    def sendCancellationNotification(self, timeSlot, email, fullname,
                                     extraInfoStr, isOnWaitingList):
        day = timeSlot.aq_parent
        signupSheet = day.aq_parent

        contactInfo = signupSheet.contactInfo
        isEmail = validation.validatorFor('isEmail')
        if not signupSheet.notifyContactInfo or \
           not isEmail(contactInfo) or len(contactInfo) < 1:
            return

        lang = ILanguage(signupSheet).get_language()
        if len(lang) == 0:
            lang = 'de'

        toEmail = contactInfo
        fromEmail = signupSheet.contactInfo
        subject = signupSheet.Title() + ' - ' \
            + translate(_(u'Cancellation Notification'), target_language=lang)

        message = translate(_(u'Hello'), target_language=lang) + ',\n\n'

        if isOnWaitingList:
            message += translate(_(u'A signup has been cancelled from the waiting list of following slot:'), target_language=lang) + '\n'  # noqa: E501
        else:
            message += translate(
                _(u'Following slot has been cancelled:'), target_language=lang) + '\n'
        message += timeSlot.getLabel() + '\n\n'

        message += translate(_(u'Name'), target_language=lang) + ': ' + fullname + '\n'
        message += translate(_(u'E-Mail'), target_language=lang) + ': ' + email + '\n\n'

        if len(extraInfoStr) > 0:
            message += translate(_(u'timeslot_label_extraInformation'), target_language=lang) + '\n'
            message += extraInfoStr + '\n\n'

        api.portal.send_email(recipient=toEmail, sender=fromEmail,
                              subject=subject, body=message)

    def cancelReservation(self):
        selectedSlots = self.request.get('selectedSlot', None)
        if type(selectedSlots) != list:
            selectedSlots = [selectedSlots]

        if selectedSlots != [None]:
            for slot in selectedSlots:
                self.signOffCurrentUserFromSlot(slot)

        # purge request to refresh view for everyone
        notify(Purge(self.context))

        self.request.response.redirect(self.context.absolute_url() + '/@@show-reservations')

    def signOffCurrentUserFromSlot(self, slot):
        curUser = api.user.get_current()
        personId = ploneUserToPersonId(curUser)

        (date, time) = slot.split(' @ ')
        day = self.context.getDay(date)
        timeSlot = day.getTimeSlot(time)

        # get person object brain to check if he/she is on waiting list or not
        # to be able to include this infromation in the mail to the manager
        timeSlotPath = '/'.join(timeSlot.getPhysicalPath())
        brains = self.context.portal_catalog.unrestrictedSearchResults(
            portal_type='UTPerson', id=personId, path=timeSlotPath)
        person = brains[0].unrestrictedTraverse(brains[0].getPath())

        extraInfoStr = person.getExtraInfoAsString()

        state = api.content.get_state(obj=person)

        if state == 'signedoff':
            return  # user is already signedoff

        isOnWaitingList = False
        if state == 'waiting':
            isOnWaitingList = True

        api.content.transition(obj=person, transition='signoff')
        person.reindexObject()

        self.sendCancellationNotification(
            timeSlot, person.email, person.Title(), extraInfoStr, isOnWaitingList)
