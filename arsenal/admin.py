from django.contrib import admin

from .models import EventVote, VoteQuestion, VoteAnswer, VoteUser


@admin.register(EventVote)
class EventVoteAdmin(admin.ModelAdmin):
    list_display = ('event_round', 'user', 'match', 'home_score', 'away_score', 'vote_date', 'is_result')


class VoteAnswerTable(admin.StackedInline):
    model = VoteAnswer
    extra = 3


@admin.register(VoteQuestion)
class VoteQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'choice_num', 'created', 'start_vote', 'end_vote', 'is_sort', 'is_active')
    list_filter = ('question',)
    search_fields = ('question',)

    inlines = [VoteAnswerTable]


@admin.register(VoteAnswer)
class VoteAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'question', 'answer', 'vote', 'is_transform')


@admin.register(VoteUser)
class VoteUserAdmin(admin.ModelAdmin):
    list_display = ('question', 'user', 'created', 'is_sort')
    list_filter = ('question',)
    search_fields = ('question',)
