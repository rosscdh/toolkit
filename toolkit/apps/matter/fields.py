from django.forms import ModelChoiceField


class MatterModelChoiceField(ModelChoiceField):
    def label_from_instance(self, obj):
        return u'%s: %s' % (obj.client, obj.name)
