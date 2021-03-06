# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.app.z3cform.widget import DatetimeWidget
from plone.autoform import directives
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

    directives.widget(
        'startTime', DatetimeWidget, pattern_options={'date': 'false'})
    startTime = schema.Timedelta(
        title=_('Start Time'),
        required=True
    )

    directives.widget(
        'endTime', DatetimeWidget, pattern_options={'date': 'false'})
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
        return u'{0} - {1}'.format(
            str(self.getStartTime()), str(self.getEndTime()))

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

    def getPeople(self, sortByStatus=False, filterByStatus=False):
        if filterByStatus:
            brains = api.content.find(
                context=self, portal_type='UTPerson',
                review_state=filterByStatus, depth=1)
        else:
            brains = api.content.find(
                context=self, portal_type='UTPerson', depth=1)

        people = [brain.getObject() for brain in brains]
        if sortByStatus:
            sortOrder = {'signedoff': 3, 'waiting': 2,
                         'unconfirmed': 1, 'signedup': 0}
            people.sort(key=lambda p: sortOrder[api.content.get_state(obj=p)])

        return people

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

    def timeDeltaToHoursMinutes(self, delta):
        hours, remainder = divmod(delta.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        hours = str(int(hours)).zfill(2)
        minutes = str(int(minutes)).zfill(2)
        return '{0}:{1}'.format(hours, minutes)

    def getStartTime(self):
        if self.startTime is None:
            return '00:00'
        return self.timeDeltaToHoursMinutes(self.startTime)

    def getEndTime(self):
        if self.endTime is None:
            return '00:00'
        return self.timeDeltaToHoursMinutes(self.endTime)


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
