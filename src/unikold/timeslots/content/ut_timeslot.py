# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.content import Container
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.supermodel import model
from unikold.timeslots import _
from zope import schema
from zope.component import getUtility
from zope.interface import implementer


class IUTTimeslot(model.Schema):

    startTime = schema.Timedelta(
        title=_('Start Time'),
        required=True
    )

    endTime = schema.Timedelta(
        title=_(u'End Time'),
        required=True
    )

    name = schema.TextLine(
        title=_(u'Name'),
        description=_(u'Optional name'),
        required=False
    )

    maxCapacity = schema.Int(
        title=_(u'Max capacity'),
        description=_(u'The max number of people'),
        required=True,
        default=1
    )

    allowWaitingList = schema.Bool(
        title=_(u'Allow Waiting List'),
        description=_(u'Check if you want to allow signups to waiting list once max capacity is reached')  # noqa: E501
    )


@implementer(IUTTimeslot)
class UTTimeslot(Container):

    def getLabel(self):
        parentDay = self.aq_parent
        signupSheet = parentDay.aq_parent
        if signupSheet.hideDateTime:
            return self.getName()
        else:
            return '{0} @ {1}'.format(parentDay.Title(), self.Title())

    def getIDLabel(self):
        parentDay = self.aq_parent
        return '{0} @ {1}'.format(parentDay.id, self.id)

    def getTimeRange(self):
        return '{0} - {1}'.format(str(self.startTime), str(self.endTime))

    def getNumberOfAvailableSlots(self):
        brains = self.getFolderContents()
        numberOfPeopleSignedUp = len(brains)
        return max(0, self.maxCapacity - numberOfPeopleSignedUp)

    def getCurrentUserSignUpState(self):
        username = api.user.get_current().getUserName()
        brains = api.content.find(
            context=self, portal_type='UTPerson', id=username)

        if len(brains) == 0:
            return False

        obj = brains[0].getObject()
        return api.content.get_state(obj)

    def isFull(self):
        return (self.getNumberOfAvailableSlots() == 0
                and not self.allowWaitingList)

    def isUserSignedUpForThisSlot(self, username):
        brains = api.content.find(
            context=self, portal_type='UTPerson',
            review_state='signedup', id=username)
        return len(brains) != 0


# set id & title on creation and change
def autoSetID(timeslot, event):
    if timeslot.startTime is None or timeslot.endTime is None:
        return

    title = timeslot.getTimeRange()
    normalizer = getUtility(IIDNormalizer)
    newId = normalizer.normalize(title)
    if title != timeslot.title or newId != timeslot.id:
        timeslot.title = title
        api.content.rename(obj=timeslot, new_id=newId, safe_id=True)
        timeslot.reindexObject()
