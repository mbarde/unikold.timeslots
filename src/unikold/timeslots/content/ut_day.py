# -*- coding: utf-8 -*-
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
    """
    """
