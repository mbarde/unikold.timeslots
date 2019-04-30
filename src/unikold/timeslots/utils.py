# -*- coding: utf-8 -*-
from collective.easyform.api import get_schema
from plone import api
from plone.i18n.normalizer.interfaces import IIDNormalizer
from unikold.timeslots import _
from zope.component import getUtility
from zope.schema.vocabulary import SimpleVocabulary


def getPersonTitleVocabulary():
    values = ('Frau', 'Frau Dr.', 'Frau Prof. Dr.', 'Frau apl. Prof. Dr.', 'Frau Jun.-Prof. Dr.',
              'Herr', 'Herr Dr.', 'Herr Prof. Dr.', 'Herr apl. Prof. Dr.', 'Herr Jun.-Prof. Dr.')
    return SimpleVocabulary.fromValues(values)


def replaceCustomMailPlaceholders(text, personName, signupSheetTitle,
                                  signupSheetURL, slotTitle, extraInfoStr):
    return text.replace('$$name$$', personName) \
               .replace('$$title$$', signupSheetTitle) \
               .replace('$$url$$', signupSheetURL) \
               .replace('$$slot$$', slotTitle) \
               .replace('$$data$$', extraInfoStr)


def getAllExtraFields(signupSheet):
    result = []

    extraFormReference = signupSheet.extraFieldsForm
    if extraFormReference is None:
        return result

    formObj = extraFormReference.to_object
    if formObj is None:
        return result

    schema = get_schema(formObj)
    for fieldName in schema:
        widget = schema.get(fieldName)
        item = {}
        item['name'] = fieldName
        item['label'] = widget.title
        item['description'] = widget.description
        item['required'] = widget.required
        result.append(item)

    return result


# ID of UTPerson objects is based on persons email
def emailToPersonId(email):
    normalizer = getUtility(IIDNormalizer)
    return normalizer.normalize(email)


# plone user to personId
def ploneUserToPersonId(user):
    if api.portal.get_registry_record('plone.use_email_as_login'):
        # case: email = username
        email = user.getUserName()
    else:
        try:
            email = user.getProperty('email')
        except ValueError:
            # in case property `email` does not exist
            email = ''
    return emailToPersonId(email)


def translateReviewState(state):
    mappings = {
        'signedup': _(u'Signed Up'),
        'signedoff': _(u'Signed Off'),
        'unconfirmed': _(u'Waiting for confirmation'),
        'waiting': _(u'Waiting List'),
    }
    if state not in mappings:
        return state
    return mappings[state]
