from django.contrib import admin


class SimpleTabularInline(admin.TabularInline):
    template = 'admin/edit_inline/simple_tabular.html'
    extra = 0