from django.contrib import admin

from .models import Message


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('send_num', 'take_num', 'send_user', 'take_user', 'message', 'created', 'is_confirm', 'take_delete', 'send_delete', 'is_active')
    search_fields = ('send_user', 'take_user')
    ordering = ('-created',)
