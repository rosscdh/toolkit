# -*- coding: utf-8 -*-


class StatusLabelsMixin(object):
    """
    Mixin to allow the model to store customized status in its json data
    """
    @property
    def status(self):
        return int(self.data.get('status', self.item.matter.default_status_index))

    @status.setter
    def status(self, value):
        self.data['status'] = int(value)

    @property
    def display_status(self):
        status_labels = self.item.matter.status_labels
        try:
            return status_labels[self.status]
        except KeyError:
            #
            # sometimes the dict key is a string and not an int
            #
            return status_labels[str(self.status)]
        else:
            return None  #status_labels[self.default_status]