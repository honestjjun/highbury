from django.contrib import admin

from .models import Team, TeamSeason, Player, PlayerSeason, Match, UserPoint


class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'stadium', 'league')
    search_fields = ('name',)


class TeamSeasonAdmin(admin.ModelAdmin):
    list_display = ('league', 'team', 'ranking', 'ranking', 'win', 'draw', 'lose', 'benefit', 'goal_benefit')
    search_fields = ('league', 'team')


class PlayerAdmin(admin.ModelAdmin):
    list_display = ('name', 'birth', 'nation')
    search_fields = ('name',)


class PlayerSeasonAdmin(admin.ModelAdmin):
    list_display = ('league', 'name', 'team', 'back_number', 'position_number', 'position', 'goal', 'assist', 'game', 'point', 'ratio')
    search_fields = ('league', 'name')


class MatchAdmin(admin.ModelAdmin):
    list_display = ('round', 'league', 'home_team', 'away_team', 'match_date', 'result', 'home_score', 'away_score')
    search_fields = ('league', 'home_team', 'away_team')


class UserPointAdmin(admin.ModelAdmin):
    list_display = ('user', 'point', 'total_experience', 'point_name', 'daily_check', 'daily_review', 'daily_free', 'daily_comment', 'level', 'experience', 'max_experience', 'recent_update')
    search_fields = ('user', 'level')


admin.site.register(UserPoint, UserPointAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(TeamSeason, TeamSeasonAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(PlayerSeason, PlayerSeasonAdmin)
admin.site.register(Match, MatchAdmin)
