from collections import Counter

from data.models import Team
from django import template
from django.db.models import Count

from advertise.models import Advertise
from board_free.models import FreeBoard
from pointshop.models import Discount, Product
from tag.models import Tagging, Tag
from arsenal.models import VoteQuestion


register = template.Library()


@register.assignment_tag
def main_advertisements():
    return Advertise.active.filter(sort='main_advertise')


@register.assignment_tag
def sub_top_advertisements():
    return Advertise.active.filter(sort='sub_top')


@register.assignment_tag
def community_right_advertisements():
    return Advertise.active.filter(sort='community_right')


@register.assignment_tag
def popular_posts():
    posts = FreeBoard.active.filter(sort='free')
    #posts = FreeBoard.active.filter(sort='free', created__gt=timezone.now() - relativedelta(days=7))
    posts = posts.annotate(recommend_num=Count('recommends')).order_by('-recommend_num', '-read', '-created')[:5]
    return posts


@register.assignment_tag
def popular_reviews():
    posts = FreeBoard.active.filter(sort__in=['after', 'before', 'player'])
    #posts = FreeBoard.active.filter(sort__in=['after', 'before', 'player'], created__gt=timezone.now() - relativedelta(days=7))
    posts = posts.annotate(recommend_num=Count('recommends')).order_by('-recommend_num', '-read', '-created')[:5]
    return posts


@register.assignment_tag
def popular_tags():
    popular_tags = Tagging.objects.all().values('tag', )
    #popular_tags = Tagging.objects.filter(created__gt=timezone.now() - relativedelta(days=7)).values('tag', )
    popular_tags = Counter([Tag.objects.get(id=popular_tag['tag']) for popular_tag in popular_tags])
    popular_tags = sorted(popular_tags.items(), key=lambda x:x[1], reverse=True)[:10]
    return popular_tags


@register.assignment_tag
def active_survey():
    return VoteQuestion.active.all()[:5]


'''
point shop - list page & detail page
'''
@register.assignment_tag
def discount_confirm(): # 할인율 계산
    events = Discount.active.all()
    if not events:
        return None
    elif len(events) == 1:
        return events[0].discount_point
    else:
        return sum(int(event.discount_point) for event in events)


'''
point shop - list page & detail page
'''
@register.assignment_tag
def popular_product(): # 인기 상품
    return Product.objects.annotate(recommend_num=Count('recommends')).order_by('-recommend_num','-created')[:5]


'''
point shop - list page & detail page
'''
@register.assignment_tag
def max_product(): # 최대 판매 상품
    return Product.objects.annotate(most_buy=Count('buyer')).order_by('-most_buy')[:5]
