# -*- coding: utf-8 -*-
from z3c.form.converter import TimedeltaDataConverter
from z3c.form.interfaces import ITextWidget
from zope.component import adapter
from zope.component import provideAdapter
from zope.schema.interfaces import ITimedelta


@adapter(ITimedelta, ITextWidget)
class DayTimeDataConverter(TimedeltaDataConverter):

    # inputs from timepicker can have a strange format (i.e. 10:00 00:00)
    # we need to format it in a datetime compatible way
    def toFieldValue(self, value):
        if ' ' in value:
            splitted = value.split(' ')
            value = splitted[0]
        return super(DayTimeDataConverter, self).toFieldValue(value)


provideAdapter(DayTimeDataConverter)
