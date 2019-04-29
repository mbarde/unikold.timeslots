# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.dexterity.content import Container
from plone.i18n.normalizer.interfaces import IIDNormalizer
from plone.locking.interfaces import ILockable
from plone.supermodel import model
from unikold.timeslots import _
from unikold.timeslots.utils import emailToPersonId
from unikold.timeslots.utils import ploneUserToPersonId
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
            return u'{0} @ {1}'.format(parentDay.Title(), self.Title())

    def getIDLabel(self):
        parentDay = self.aq_parent
        return u'{0} @ {1}'.format(parentDay.id, self.id)

    def getTimeRange(self):
        return u'{0} - {1}'.format(str(self.startTime), str(self.endTime))

    def getPersons(self):
        brains = self.portal_catalog.unrestrictedSearchResults(
            portal_type='UTPerson', path=self.getPath())
        return map(lambda x: x.getObject(), brains)

    def getNumberOfAvailableSlots(self):
        brains = self.portal_catalog.unrestrictedSearchResults(
            portal_type='UTPerson', review_state='signedup', path=self.getPath())
        numberOfPeopleSignedUp = len(brains)
        return max(0, self.maxCapacity - numberOfPeopleSignedUp)

    def getCurrentUserSignUpState(self):
        curUser = api.user.get_current()
        personId = ploneUserToPersonId(curUser)

        # no need to make use of unrestrictedSearchResults since owner
        # should be allowed to access his own person object
        if not hasattr(self, personId):
            return False

        person = getattr(self, personId)
        return api.content.get_state(person)

    def isFull(self):
        return (self.getNumberOfAvailableSlots() == 0
                and not self.allowWaitingList)

    def isUserSignedUpForThisSlot(self, email):
        personId = emailToPersonId(email)
        brains = self.portal_catalog.unrestrictedSearchResults(
            portal_type='UTPerson', review_state='signedup',
            id=personId, path=self.getPath())
        return len(brains) != 0

    def isRegistrationExpired(self):
        now = DateTime()
        return (self.expires <= now)

    def getPath(self):
        return '/'.join(self.getPhysicalPath())


# set id & title on creation and modification
def autoSetID(timeslot, event):
    if timeslot.startTime is None or timeslot.endTime is None:
        return

    title = timeslot.getTimeRange()
    normalizer = getUtility(IIDNormalizer)
    newId = normalizer.normalize(title)
    if title != timeslot.title or newId != timeslot.id:
        lockable = ILockable(timeslot)
        if lockable.locked():
            if not lockable.can_safely_unlock():
                # can not modify locked object
                return
            lockable.unlock()
        timeslot.title = title
        api.content.rename(obj=timeslot, new_id=newId, safe_id=True)
        timeslot.reindexObject()
