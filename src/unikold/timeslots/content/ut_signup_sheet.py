# -*- coding: utf-8 -*-
from plone.app.textfield import RichText
from plone.app.vocabularies.catalog import CatalogSource
from plone.dexterity.content import Container
from plone.supermodel import model
from unikold.timeslots import _
from z3c.relationfield.schema import RelationChoice
from zope import schema
from zope.interface import implementer


class IUTSignupSheet(model.Schema):

    text = RichText(
        title=_(u'Text'),
        description=_(u'This (formatted) text will be displayed above the form'),
        required=False
    )

    contactInfo = schema.TextLine(
        title=_(u'Contact Information'),
        description=_(u'Contact information for the manager of the signup sheet.'),
        required=True
    )

    notifyContactInfo = schema.Bool(
        title=_(u'Send notification mails to contact info'),
        description=_(u'Send notifications to the mail address provided in the contact info field on new signups or cancellations'),  # noqa: E501
        default=True
    )

    signupsRequireConfirmation = schema.Bool(
        title=_(u'Manager has to confirm signups'),
        description=_(u'Signups have to be confirmed by the manager (can also be rejected).')
    )

    allowSignupForExternals = schema.Bool(
        title=_(u'Allow Signup For External User'),
        description=_(u'Allow signup for users which do not have an university account')
    )

    allowSignupForMultipleSlots = schema.Bool(
        title=_(u'Allow Signup For Multiple Slots'),
        description=_(u'Allow the user to signup for more than one slot.')
    )

    enableAutoMovingUpFromWaitingList = schema.Bool(
        title=_(u'Automatic move up from waiting list'),
        description=_(u'If a signup is cancelled, the first person on the waiting list (sorted by date) is automatically signed up.'),  # noqa: E501
        default=True
    )

    showSlotNames = schema.Bool(
        title=_(u'Show Individual Time Slot Names'),
        description=_(u'Whether or not to show individual slot names.'),
        default=True
    )

    hideAvailability = schema.Bool(
        title=_(u'Hide availability'),
        description=_(u'Hide how many persons can sign up for a slot')
    )

    hideDateTime = schema.Bool(
        title=_(u'Hide date and time'),
        description=_(u'For signups that are not bound to a certain time slot')
    )

    askForPersonTitle = schema.Bool(
        title=_(u'Ask for person title'),
        description=_(u'Additionally to name and mail address a field for the persons title will be displayed.')  # noqa: E501
    )

    extraFieldsForm = RelationChoice(
        title=_(u'Additional form'),
        description=_(u'Additional form to be filled in for registration.'),
        source=CatalogSource(portal_type=['EasyForm']),
        required=False
    )

    model.fieldset(
        'mailsettings',
        label=_(u'Mail settings'),
        description=_(u"Following placeholders can be used:<br/>$$name$$ -> Full name of user<br/>$$title$$ -> Title of the signup sheet<br/>$$url$$ -> URL of the signup sheet<br/>$$slot$$ -> Date and time of slot (name of slot if date and time hid)<br/>$$data$$ -> Additional data (see 'additional form')"),  # noqa: E501
        fields=['emailConfirmationSubject', 'emailConfirmationContent',
                'emailWaitForConfirmationSubject', 'emailWaitForConfirmationContent',
                'emailWaitinglistSubject', 'emailWaitinglistContent']
    )

    # confirmation email
    emailConfirmationSubject = schema.TextLine(
        title=_(u'Confirmation Email Subject'),
        description=_(u'This email will be send on successful registration.'),
        required=False
    )

    emailConfirmationContent = schema.Text(
        title=_(u'Confirmation Email Content'),
        required=False
    )

    # wait for confirmation email
    emailWaitForConfirmationSubject = schema.TextLine(
        title=_(u'Wait For Confirmation Email Subject'),
        description=_(u'This email will be send when user registered for a timeslot and a confirmation is required (if field "Manager has to confirm signups" is set).'),  # noqa: E501
        required=False
    )

    emailWaitForConfirmationContent = schema.Text(
        title=_(u'Wait For Confirmation Email Content'),
        required=False
    )

    # waiting list email
    emailWaitinglistSubject = schema.TextLine(
        title=_(u'Waitinglist Email Subject'),
        description=_(u'This email will be send on registration for the waitinglist.'),
        required=False
    )

    emailWaitinglistContent = schema.Text(
        title=_(u'Waitinglist Email Content'),
        required=False
    )

    # cancellation email
    emailCancelSubject = schema.TextLine(
        title=_(u'Cancellation Email Subject'),
        description=_(u'This email will be send on a registration cancellation.'),
        required=False
    )

    emailCancelContent = schema.Text(
        title=_(u'Cancellation Email Content'),
        required=False
    )


@implementer(IUTSignupSheet)
class UTSignupSheet(Container):
    """
    """
