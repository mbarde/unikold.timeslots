# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.timeslots import _
from zope import schema
from zope.interface import implementer


class IUTPerson(model.Schema):

    email = schema.TextLine(
        title=_('E-Mail')
    )

    prename = schema.TextLine(
        title=_('Prename')
    )

    surname = schema.TextLine(
        title=_('Surname')
    )

    note = schema.TextLine(
        title=_('Note')
    )


@implementer(IUTPerson)
class UTPerson(Item):
    """
    """
