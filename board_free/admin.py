from django.contrib import admin

from .models import FreeBoard, AfterReview, BeforeReview


class FreeBoardAdmin(admin.ModelAdmin):
    list_display = ('id', 'sort', 'title', 'user', 'created', 'read', 'is_active', 'is_superuser')
    list_filter = ('is_active',)
    search_fields = ('title', 'user')
    prepopulated_fields = {'slug': ('title',)}


class AfterReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'freeboard', 'match', 'user', 'created', 'sort', 'player', 'point')


class BeforeReviewAdmin(admin.ModelAdmin):
    list_display = ('id', 'freeboard', 'match', 'user', 'created', 'sort', 'strategy', 'player')


admin.site.register(FreeBoard, FreeBoardAdmin)
admin.site.register(BeforeReview, BeforeReviewAdmin)
admin.site.register(AfterReview, AfterReviewAdmin)