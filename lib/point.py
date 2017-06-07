from django.conf import settings

from data.models import UserPoint


def point(user, data, data2=None):
    point = UserPoint.objects.get(user=user.id)
    point.sort = data
    if data == 'login':
        point.value = settings.DAILY_LOGIN_POINT
    elif data == 'review':
        point.value = settings.DAILY_REVIEW_POINT
        if data2:
            point.value += settings.AFTER_GAME_GIVE_POINT
    elif data == 'free':
        point.value = settings.DAILY_BOARD_POINT
    elif data == 'comment':
        point.value = settings.DAILY_COMMENT_POINT
    elif data == 'vote':
        point.value = settings.NEXT_GAME_VOTE_RESULT
    elif data == 'correct_vote':
        point.value = settings.NEXT_GAME_VOTE_CORRECT
    elif data == 'easy_point':
        point.value = settings.AFTER_GAME_GIVE_POINT
    point.save()
