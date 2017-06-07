from django.contrib import admin

from .models import Advertise

import os


def real_delete(modeladmin, request, queryset):
    for single_queryset in queryset:
        if os.path.exists(single_queryset.banner.path):
            os.remove(single_queryset.banner.path)
        single_queryset.delete()

real_delete.short_description = 'real_delete'


class AdvertiseAdmin(admin.ModelAdmin):
    actions = [real_delete]

    list_display = ('num', 'sort', 'title', 'event_start', 'event_end', 'created', 'is_active', 'link', 'banner')
    search_fields = ('sort', 'title')


admin.site.register(Advertise, AdvertiseAdmin)
