# -*- coding: utf-8 -*-
from plone.dexterity.content import Container
from plone.supermodel import model
from unikold.timeslots import _
from zope import schema
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
    """
    """
