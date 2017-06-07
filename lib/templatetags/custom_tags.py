#!/usr/bin/python
#-*- coding: utf-8 -*-
import datetime

from data.models import Team
from django import template
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from board_free.models import AfterReview
from administrator.models import Charge
from tag.models import Comment

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary[key]


@register.filter
def order_by(user, value):
    return user.order_by(str(value),)


@register.filter
def delete_comment(user, value):
    return "{% url 'football_board:comment_delete' value %}"


@register.filter
def make_list_df(user, num):
    df_list = []
    i = int(user)
    while i < num+int(user) :
        df_list.append('player_'+str(i))
        i += 1
    return df_list


@register.filter
def make_list_mf(user, num):
    mf_list = []
    i = int(user)
    while i < num+int(user):
        mf_list.append('player_'+str(i))
        i += 1
    return mf_list


@register.filter
def make_list_fw(user, num):
    fw_list = []
    i = int(user)
    while i < num+int(user):
        fw_list.append('player_'+str(i))
        i += 1
    return fw_list


@register.filter
def png(user, value):
    if value == 'search':
        return 'http://127.0.0.1:8000/media/etc/search_16x16.png'
    elif value == 'main-poster':
        return 'http://127.0.0.1:8000/media/etc/'+user


@register.filter
def experience_ratio(user, value):
    if user == 0:
        return 0
    else:
        return round((value-user)/value*100)


@register.filter
def give_point(user):
    if user == 1:
        return "http://127.0.0.1:8000/media/star_rating/1.jpg"
    elif user == 2:
        return "http://127.0.0.1:8000/media/star_rating/2.jpg"
    elif user == 3:
        return "http://127.0.0.1:8000/media/star_rating/3.jpg"
    elif user == 4:
        return "http://127.0.0.1:8000/media/star_rating/4.jpg"
    elif user == 5:
        return "http://127.0.0.1:8000/media/star_rating/5.jpg"
    elif user == 6:
        return "http://127.0.0.1:8000/media/star_rating/6.jpg"
    elif user == 7:
        return "http://127.0.0.1:8000/media/star_rating/7.jpg"
    elif user == 8:
        return "http://127.0.0.1:8000/media/star_rating/8.jpg"
    elif user == 9:
        return "http://127.0.0.1:8000/media/star_rating/9.jpg"
    elif user == 10:
        return "http://127.0.0.1:8000/media/star_rating/10.jpg"


'''
Gooner 메뉴에서 해당 경기로 afterreview 를 남겼는지 여부 파악
'''
@register.filter
def game_value(obj):
    match = AfterReview.objects.filter(match=obj)
    if match:
        return True
    else:
        return False


@register.filter
def average_point(user, value):
    return round(user/value)


@register.filter # 설문지에서 유저가 설문을 했는지에 대한 여부 따짐
def check_in(user, value):
    for hi in user:
        if hi.user == value:
            return True
        else:
            return False


@register.filter # 설문지에서 비율 구할 때 만듬
def ratio_value(obj, total):
    return round((obj/total)*100,1)


@register.filter
def vote_num(user):
    num = 0
    for vote in user:
        num += vote.vote
    return num


@register.filter
def discount_ratio(user, value):
    return round(user-(user*value/100))


'''
게임 리뷰 선택하는 곳에서 유저가 게임 리뷰를 작성했는지 여부 파악
자유 게시판 리스트에서 추천했는지 여부 파악
'''
@register.filter
def find_user(obj, user):
    if obj:
        for object in obj:
            if user == object.user:
                return True
    return False


'''
유저 mypage main menu 에 사용
'''
@register.filter
def acquire_num(user, value):
    return len(user.filter(sort=value))


@register.filter # user_point 에서 만족도 구할 때 사용
def is_satisfaction(obj, user):
    ct = ContentType.objects.get_for_model(obj)
    try:
        product = Comment.objects.get(content_type=ct, object_id=obj.id, user=user, sort='point-re')
    except Comment.DoesNotExist:
        return False
    else:
        return product.satisfaction


@register.filter # profile page 에서 strategy 표시 되는 곳에 사용
def modify_strategy(obj):
    if obj == 'strategy_4-2-3-1':
        return '4-2-3-1'
    elif obj == 'strategy_3-5-1':
        return '3-5-1'


@register.filter # gooner 부분에서 스코어 맞추기 당첨자 보여줄때 나옴
def cut(obj, num):
    return obj[:num]


'''
input_pointshop_tags.jinja 에 queryset 을 list 로 변환 시켜 버림
'''
@register.filter
def to_list(obj, value):
    obj = obj.values_list(value, flat=True)
    return ','.join(obj)


'''
review-detail 에서 arsenal 팀을 불러옴
'''
@register.filter
def find_team(value):
    team = Team.objects.get(name=value)
    return team.photo.url