# -*- coding: utf-8 -*-
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
