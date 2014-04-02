# -*- coding: utf-8 -*-
from django.conf import settings
from collections import namedtuple, OrderedDict
from django.contrib.sites.models import Site


def _class_importer(name):
    """
    func used to import the bunch classes from string
    """
    try:
        components = name.split('.')
        module_path = components[:-1]
        klass = components[-1:]
        mod = __import__('.'.join(module_path), fromlist=klass)  # import the class and module
        klass = getattr(mod, klass[0])
    except AttributeError:
        klass = None
    return klass


def get_namedtuple_choices(name, choices_tuple):
    """Factory function for quickly making a namedtuple suitable for use in a
    Django model as a choices attribute on a field. It will preserve order.

    Usage::

        class MyModel(models.Model):
            COLORS = get_namedtuple_choices('COLORS', (
                (0, 'black', 'Black'),
                (1, 'white', 'White'),
            ))
            colors = models.PositiveIntegerField(choices=COLORS)

        >>> MyModel.COLORS.black
        0
        >>> MyModel.COLORS.get_choices()
        [(0, 'Black'), (1, 'White')]

        class OtherModel(models.Model):
            GRADES = get_namedtuple_choices('GRADES', (
                ('FR', 'fr', 'Freshman'),
                ('SR', 'sr', 'Senior'),
            ))
            grade = models.CharField(max_length=2, choices=GRADES)

        >>> OtherModel.GRADES.fr
        'FR'
        >>> OtherModel.GRADES.get_choices()
        [('fr', 'Freshman'), ('sr', 'Senior')]

    """
    class Choices(namedtuple(name, [name for val, name, desc in choices_tuple])):
        __slots__ = ()
        _choices = tuple([desc for val, name, desc in choices_tuple])

        def get_choices(self):
            return zip(tuple(self), self._choices)

        def get_choices_dict(self):
            """
            Return an ordered dict of key and their values
            must be ordered correctly as there are items that depend on the key
            order
            """
            choices = OrderedDict()
            for k, v in self.get_choices():
                choices[k] = v
            return choices

        def get_all(self):
            for val, name, desc in choices_tuple:
                yield val, name, desc

        def get_values(self):
            values = []
            for val, name, desc in choices_tuple:
                if isinstance(val, type([])):
                    values.extend(val)
                else:
                    values.append(val)
            return values

        def get_value_by_name(self, input_name):
            for val, name, desc in choices_tuple:
                if name == input_name:
                    return val
            return False

        def get_desc_by_value(self, input_value):
            for val, name, desc in choices_tuple:
                if val == input_value:
                    return desc
            return False

        def get_name_by_value(self, input_value):
            for val, name, desc in choices_tuple:
                if val == input_value:
                    return name
            return False

        def is_valid(self, selection):
            for val, name, desc in choices_tuple:
                if val == selection or name == selection or desc == selection:
                    return True
            return False

    return Choices._make([val for val, name, desc in choices_tuple])


def CURRENT_SITE():
    return Site.objects.get(pk=settings.SITE_ID)
