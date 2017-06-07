from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render
from django.utils import timezone

from board_free.models import FreeBoard
from account.models import MyUser
from collections import Counter
from dateutil.relativedelta import relativedelta
from lib.confirm_text import no_space_text
from tag.models import Tag, Tagging

import operator

from pointshop.models import Product


def search(request, data=None):
    if data:
        if no_space_text(data) == 1:
            messages.error(request, '한 글자 이상 검색어를 입력하셔야 합니다.')
        else:
            data = no_space_text(data, 'hi')
    else:
        data = request.GET.get('search_total_value', None)
        if no_space_text(data) == 1:
            messages.error(request, '한 글자 이상 검색어를 입력하셔야 합니다.')
        else:
            data = no_space_text(data, 'hi')

    # user nickname 검색
    users = MyUser.objects.filter(nickname__icontains=data, is_red=False)
    # post 제목으로 검색
    post_lists = FreeBoard.objects.filter(title__icontains=data, is_active=True)
    # product 제목으로 검색
    point_lists = Product.objects.filter(title__icontains=data)
    # Tag 로 검색
    tags_value = Tag.objects.filter(name__icontains=data).prefetch_related('tagging_set')

    post_tag_lists = [] # free 에 포함된 tag 일 때
    point_tag_lists = [] # pointshop 에 포함된 tag 일 때
    for tag_value in tags_value:
        for tag in tag_value.tagging_set.all():
            if tag.sort == 'free':
                post_tag_lists.append(tag.content_object)
            elif tag.sort == 'point':
                point_tag_lists.append(tag.content_object)
    # 인기 tag 구함 - 현재로 일주일간 구함
    popular_tags = Tagging.objects.filter(created__gt=timezone.now() - relativedelta(days=7)).values('tag',)
    popular_tags = Counter([Tag.objects.get(id=popular_tag['tag']) for popular_tag in popular_tags])
    popular_tags = sorted(popular_tags.items(), key=lambda x:x[1], reverse=True)[:5]

    return render(request, 'search/main.jinja', {'data': data, 'users': users, 'posts': post_lists, 'posts_tag': post_tag_lists,
                                                 'points': point_lists, 'points_tag': point_tag_lists, 'popular_tags': popular_tags})
