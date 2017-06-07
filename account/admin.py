from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import MyUser, RegistEmail


class MyUserAdmin(UserAdmin):
    list_display = ('email', 'nickname', 'sex', 'date_of_birth', 'created', 'updated', 'tel',
                    'is_active', 'is_yellow', 'is_red', 'is_input_game_result', 'is_superuser')
    list_filter = ('is_active', 'is_yellow', 'is_red', 'is_superuser')
    search_fields = ('email', 'nickname')
    fieldsets = (
        (None, {'fields': ('email', 'nickname', 'password')}),
        ('basic info', {'fields': ('sex', 'date_of_birth')}),
        ('high info', {'fields': ('photo', 'tel', 'address')}),
        ('active info', {'fields': ('created', 'updated', 'is_active', 'is_yellow', 'is_red', 'is_input_game_result', 'is_superuser')}),
        ('recommend', {'fields': ('recommend_free_board',)}),
        ('Permission', {'fields': ('groups', 'user_permissions')})
    )
    add_fieldsets = (
        (None,{'classes': ('wide',),
               'fields': ('email', 'nickname', 'sex', 'date_of_birth', 'password1', 'password2')})
    )
    ordering = ('-created',)


class RegistEmailAdmin(admin.ModelAdmin):
    list_display = ('email', 'barcode')
    search_fields = ('email',)


class SendMessageAdmin(admin.ModelAdmin):
    list_display = ('num', 'send_user', 'take_user', 'created', 'is_confirm')
    search_fields = ('send_user', 'take_user')


class TakeMessageAdmin(admin.ModelAdmin):
    list_display = ('num', 'send_user', 'take_user', 'created', 'is_confirm')
    search_fields = ('send_user', 'take_user')


admin.site.register(MyUser, MyUserAdmin)
admin.site.register(RegistEmail, RegistEmailAdmin)