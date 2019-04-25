# -*- coding: utf-8 -*-
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.timeslots import _
from unikold.timeslots.utils import getPersonTitleVocabulary
from zope import schema
from zope.interface import implementer


class IUTPerson(model.Schema):

    personTitle = schema.Choice(
        title=_('Salutation'),
        source=getPersonTitleVocabulary(),
        required=False
    )

    email = schema.TextLine(
        title=_(u'E-Mail'),
        required=True
    )

    prename = schema.TextLine(
        title=_(u'Prename'),
        required=True
    )

    surname = schema.TextLine(
        title=_(u'Surname'),
        required=True
    )

    note = schema.TextLine(
        title=_(u'Note'),
        required=False
    )


@implementer(IUTPerson)
class UTPerson(Item):
    """
    """
