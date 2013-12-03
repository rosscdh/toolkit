# -*- coding: utf-8 -*-
from collections import namedtuple


def get_namedtuple_choices(name, choices_tuple):
    """Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = get_namedtuple_choices('COLORS', (
                (0, 'BLACK', 'Black'),
                (1, 'WHITE', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)

        >>> MyModel.COLORS.BLACK
        0
        >>> MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'FR', 'Freshman'),
                ('SR', 'SR', 'Senior'),
            ))
            grade = models.CharField(max_length=2, choices=GRADES)

        >>> OtherModel.GRADES.FR
        'FR'
        >>> OtherModel.GRADES.get_choices()
        [('FR', 'Freshman'), ('SR', 'Senior')]

    """
    class Choices(namedtuple(name, [name for val,name,desc in choices_tuple])):
        __slots__ = ()
        _choices = tuple([desc for val,name,desc in choices_tuple])

        def get_choices(self):
            return zip(tuple(self), self._choices)

        def get_values(self):
            values = []
            for val,name,desc in choices_tuple:
                if isinstance(val, type([])):
                    values.extend(val)
                else:
                    values.append(val)
            return values

        def get_value_by_name(self, input_name):
            for val,name,desc in choices_tuple:
                if name == input_name:
                    return val
            return False

        def get_desc_by_value(self, input_value):
            for val,name,desc in choices_tuple:
                if val == input_value:
                    return desc
            return False

        def is_valid(self, selection):
            for val,name,desc in choices_tuple:
                if val == selection or name == selection or desc == selection:
                    return True
            return False

    return Choices._make([val for val,name,desc in choices_tuple])