from django.contrib import admin

from .models import Charge


@admin.register(Charge)
class ChargeAdmin(admin.ModelAdmin):
    list_display = ('sort', 'is_charge', 'content_object', 'charge_reason', 'charge_from', 'charge_date', 'result_now',
                    'result', 'result_date', 'result_who')
    search_fields = ('sort', 'content_object')
