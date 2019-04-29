# -*- coding: utf-8 -*-
from plone import api
from plone.dexterity.content import Item
from plone.supermodel import model
from unikold.timeslots import _
from unikold.timeslots.utils import emailToPersonId
from unikold.timeslots.utils import getAllExtraFields
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

    # extra infos depend on additional form specified in SignupSheet (`extraFieldsForm`)
    # and get stored as attributes of UTPerson object
    def getExtraInfo(self):
        extraInfo = []
        fields = getAllExtraFields(self)
        for field in fields:
            value = getattr(self, field['name'], '')
            extraInfo.append((_(field['label']), value))
        return extraInfo

    def getExtraInfoAsString(self):
        extraInfo = []
        fields = getAllExtraFields(self)
        for field in fields:
            value = getattr(self, field['name'], False)
            if value:
                extraInfo.append(_(field['label']) + ': ' + value)
        return '\n'.join(extraInfo)


# set id & title on creation and modification
def autoSetID(person, event):
    title = '{0} {1}'.format(person.prename, person.surname)
    newId = emailToPersonId(person.email)
    if title != person.title or newId != person.id:
        person.title = title
        api.content.rename(obj=person, new_id=newId, safe_id=True)
        person.reindexObject()
