from django.contrib import admin
from .models import Tag, Tagging, Action, Comment, Recommend


class TaggingStack(admin.StackedInline):
    model = Tagging
    extra = 4


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name',)

    inlines = [TaggingStack]


@admin.register(Tagging)
class TaggingAdmin(admin.ModelAdmin):
    list_display = ('tag', 'user', 'sort', 'created', 'content_type')
    search_fields = ('tag', 'user', 'sort')


@admin.register(Action)
class ActionAdmin(admin.ModelAdmin):
    list_display = ('user', 'sort', 'created', 'content_type', 'content_object')
    search_fields = ('user', 'sort', 'content_type')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('user', 'sort', 'created', 'comment', 'commenting_user', 'satisfaction', 'is_active', 'content_type')
    search_fields = ('user', 'sort')


@admin.register(Recommend)
class RecommendAdmin(admin.ModelAdmin):
    list_display = ('user', 'created', 'content_object')
