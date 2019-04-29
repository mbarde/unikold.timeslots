# -*- coding: utf-8 -*-
from plone import api
from Products.CMFPlone.interfaces import ILanguage
from Products.validation import validation
from unikold.timeslots import _
from unikold.timeslots.utils import replaceCustomMailPlaceholders
from zope.i18n import translate


# send notification to user and manager (if `notifyContactInfo` is set)
def sendSignupNotificationEmail(person):
    isEmail = validation.validatorFor('isEmail')

    timeSlot = person.aq_parent
    day = timeSlot.aq_parent
    signupSheet = day.aq_parent

    lang = ILanguage(signupSheet).get_language()
    if len(lang) == 0:
        lang = 'de'

    contactInfo = signupSheet.contactInfo
    extraInfoStr = person.getExtraInfoAsString()
    fromEmail = signupSheet.contactInfo

    # mail to person who signed up
    if isEmail(person.email) != 1:
        return

    url = signupSheet.absolute_url()
    toEmail = person.email

    subject = signupSheet.emailConfirmationSubject
    if subject is None or len(subject) == 0:
        subject = signupSheet.Title() + ' - ' \
                  + translate(_(u'Registration Confirmation'),
                              target_language=lang)
    else:
        subject = replaceCustomMailPlaceholders(
            subject, person.Title(), signupSheet.Title(), url,
            timeSlot.getLabel(), extraInfoStr)

    content = signupSheet.emailConfirmationContent
    if content is not None and len(content) > 0:
        message = replaceCustomMailPlaceholders(
            content, person.Title(), signupSheet.Title(), url,
            timeSlot.getLabel(), extraInfoStr)
    else:
        # default message if no content has been specified
        message = translate(_(u'Hello'), target_language=lang) + ' ' + person.Title() + ',\n\n'
        message += translate(_(u'This message is to confirm that you have been signed up for:'),
                             target_language=lang) + '\n'
        message += timeSlot.getLabel() + '\n\n'

        if len(extraInfoStr) > 0:
            message += translate(_(u'timeslot_label_extraInformation'),
                                 target_language=lang) + '\n'
            message += extraInfoStr + '\n\n'

        if len(contactInfo) > 0:
            message += translate(_('If you have any questions please contact:'),
                                 target_language=lang) + ' ' + contactInfo + '\n\n'

        message += url + '\n\n'

    api.portal.send_email(recipient=toEmail, sender=fromEmail,
                          subject=subject, body=message)

    # mail to contact person of the signup sheet
    if signupSheet.notifyContactInfo and len(contactInfo) > 0 and isEmail(contactInfo):
        url = signupSheet.absolute_url()
        toEmail = contactInfo
        subject = signupSheet.Title() + ' - ' \
            + translate(_(u'Registration Notification'), target_language=lang)

        message = translate(_(u'Hello'), target_language=lang) + ',\n\n'
        message += translate(_(u'This message is to notify you that someone signed up for:'),
                             target_language=lang) + '\n'
        message += timeSlot.getLabel() + '\n\n'

        message += translate(_(u'Name'), target_language=lang) + ': ' + person.Title() + '\n'
        message += translate(_(u'E-Mail'), target_language=lang) + ': ' + person.email + '\n\n'

        if len(extraInfoStr) > 0:
            message += translate(_(u'timeslot_label_extraInformation'), target_language=lang) + '\n'
            message += extraInfoStr + '\n\n'

        message += '\nURL: ' + person.absolute_url() + '\n\n'

        api.portal.send_email(recipient=toEmail, sender=fromEmail,
                              subject=subject, body=message)


# send notification to user and manager (if `notifyContactInfo` is set)
def sendWaitingListConfirmationEmail(person):
    isEmail = validation.validatorFor('isEmail')

    timeSlot = person.aq_parent
    day = timeSlot.aq_parent
    signupSheet = day.aq_parent

    lang = ILanguage(signupSheet).get_language()
    if len(lang) == 0:
        lang = 'de'

    extraInfoStr = person.getExtraInfoAsString()
    contactInfo = signupSheet.contactInfo
    fromEmail = signupSheet.contactInfo

    if isEmail(person.email) != 1:
        return

    url = signupSheet.absolute_url()
    toEmail = person.email

    subject = signupSheet.emailWaitinglistSubject
    if subject is None or len(subject) == 0:
        subject = signupSheet.Title() + ' - ' \
            + translate(_('Waiting List Confirmation'), target_language=lang)
    else:
        subject = replaceCustomMailPlaceholders(
            subject, person.Title(), signupSheet.Title(), url,
            timeSlot.getLabel(), extraInfoStr)

    content = signupSheet.emailWaitinglistContent
    if content is not None and len(content) > 0:
        message = replaceCustomMailPlaceholders(
            content, person.Title(), signupSheet.Title(), url,
            timeSlot.getLabel(), extraInfoStr)
    else:
        # default message if no content has been specified
        message = translate(_('Hello'), target_language=lang) + ' ' + person.Title() + ',\n\n'
        message += translate(_('This message is to confirm that you have been added to the waiting list for:'), target_language=lang) + '\n'  # noqa: E501
        message += timeSlot.getLabel() + '\n\n'

        if len(extraInfoStr) > 0:
            message += translate(_(u'timeslot_label_extraInformation'),
                                 target_language=lang) + '\n'
            message += extraInfoStr + '\n\n'

        if len(contactInfo) > 0:
            message += translate(_('If you have any questions please contact:'),
                                 target_language=lang) + ' ' + contactInfo + '\n\n'

        message += url + '\n\n'

    api.portal.send_email(recipient=toEmail, sender=fromEmail,
                          subject=subject, body=message)

    # mail to contact person of the signup sheet
    if signupSheet.notifyContactInfo and len(contactInfo) > 0 and isEmail(contactInfo):
        toEmail = contactInfo
        subject = signupSheet.Title() + ' - ' \
            + translate(_('Waiting List Notification'), target_language=lang)

        message = translate(_('Hello'), target_language=lang) + ',\n\n'
        message += translate(_('A new signup has been added to the waiting list for:'),
                             target_language=lang) + '\n'
        message += timeSlot.getLabel() + '\n\n'

        message += translate(_(u'Name'), target_language=lang) + ': ' + person.Title() + '\n'
        message += translate(_(u'E-Mail'), target_language=lang) + ': ' + person.email + '\n\n'

        if len(extraInfoStr) > 0:
            message += translate(_(u'timeslot_label_extraInformation'), target_language=lang) + '\n'
            message += extraInfoStr + '\n\n'

        message += '\nURL: ' + person.absolute_url() + '\n\n'

        api.portal.send_email(recipient=toEmail, sender=fromEmail,
                              subject=subject, body=message)


# send notification to user
def sendSignOffNotification(person):
    isEmail = validation.validatorFor('isEmail')
    timeSlot = person.aq_parent
    day = timeSlot.aq_parent
    signupSheet = day.aq_parent

    lang = ILanguage(signupSheet).get_language()
    if len(lang) == 0:
        lang = 'de'

    contactInfo = signupSheet.contactInfo
    extraInfoStr = person.getExtraInfoAsString()
    fromEmail = signupSheet.contactInfo

    # mail to person who signed up
    if isEmail(person.email) != 1:
        return

    url = signupSheet.absolute_url()
    toEmail = person.email

    subject = signupSheet.emailCancelSubject
    if subject is None or len(subject) == 0:
        subject = signupSheet.Title() + ' - ' \
                  + translate(_(u'Cancellation Notification'),
                              target_language=lang)
    else:
        subject = replaceCustomMailPlaceholders(
            subject, person.Title(), signupSheet.Title(), url,
            timeSlot.getLabel(), extraInfoStr)

    content = signupSheet.emailCancelContent
    if content is not None and len(content) > 0:
        message = replaceCustomMailPlaceholders(
            content, person.Title(), signupSheet.Title(), url,
            timeSlot.getLabel(), extraInfoStr)
    else:
        # default message if no content has been specified
        message = translate(_(u'Hello'), target_language=lang) + ' ' + person.Title() + ',\n\n'
        message += translate(_(u'Following slot has been cancelled:'),
                             target_language=lang) + '\n'
        message += timeSlot.getLabel() + '\n\n'

        if len(extraInfoStr) > 0:
            message += translate(_(u'timeslot_label_extraInformation'),
                                 target_language=lang) + '\n'
            message += extraInfoStr + '\n\n'

        if len(contactInfo) > 0:
            message += translate(_('If you have any questions please contact:'),
                                 target_language=lang) + ' ' + contactInfo + '\n\n'

        message += url + '\n\n'

    api.portal.send_email(recipient=toEmail, sender=fromEmail,
                          subject=subject, body=message)


def attemptToFillEmptySpot(obj):
    timeSlot = obj.aq_parent
    day = timeSlot.aq_parent
    signupSheet = day.aq_parent

    if signupSheet.enableAutoMovingUpFromWaitingList:
        # to make sure timeslot.getNumberOfAvailableSlots() returns current value
        obj.reindexObject()

        if timeSlot.getNumberOfAvailableSlots() > 0:
            portal_catalog = api.portal.get_tool('portal_catalog')
            query = {'portal_type': 'UTPerson', 'review_state': 'waiting',
                     'sort_on': 'Date', 'sort_order': 'ascending'}
            brains = portal_catalog.unrestrictedSearchResults(query, path=timeSlot.getPath())
            if len(brains) > 0:
                person = brains[0]._unrestrictedGetObject()
                api.content.transition(obj=person, transition='signup')
                person.reindexObject()


# send out a notification based on workflow transition event
def sendNotification(obj, event):
    if event.transition and event.transition.id == 'signup':
        sendSignupNotificationEmail(obj)

    if event.transition and event.transition.id == 'putOnWaitingList':
        sendWaitingListConfirmationEmail(obj)

    if event.transition and event.transition.id == 'signoff':
        sendSignOffNotification(obj)
        if event.old_state.id == 'signedup':
            attemptToFillEmptySpot(obj)
