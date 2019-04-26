# -*- coding: utf-8 -*-
from collective.easyform.api import get_schema
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

    formObj = signupSheet.extraFieldsForm.to_object
    if formObj:
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
