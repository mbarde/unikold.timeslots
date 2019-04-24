# -*- coding: utf-8 -*-
from DateTime import DateTime
from plone import api
from plone.dexterity.content import Container
from plone.supermodel import model
from unikold.timeslots import _
from zope import schema
from zope.interface import implementer


class IUTDay(model.Schema):

    date = schema.Date(
        title=_(u'Date'),
        required=True
    )


@implementer(IUTDay)
class UTDay(Container):

    def getTimeSlots(self):
        brains = api.content.find(context=self, portal_type='UTTimeSlot', depth=1)

        timeSlots = []
        now = DateTime()
        for brain in brains:
            obj = brain.getObject()
            obj.expired = (not brain.expires > now)
            timeSlots.append(obj)

        timeSlots = sorted(timeSlots, key=lambda slot: int(slot.startTime))

        return timeSlots
