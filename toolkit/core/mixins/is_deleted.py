# -*- coding: utf-8 -*-


class IsDeletedMixin(object):
    def delete(self, *args, **kwargs):
        """
        override delete and set is_deleted = True if we have that attrib
        """
        if hasattr(self, 'is_deleted'):
            self.is_deleted = True
            self.save(update_fields=['is_deleted'])
        else:
            super(IsDeletedMixin, self).delete(*args, **kwargs)