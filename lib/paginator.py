from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage

import math


def paginator(posts, get_value, pages, value, post_num, total_page_num):

    paginator = Paginator(posts, post_num)

    if value == 'first':
        page = get_value.get(pages, 1)
    elif value == 'last':
        page = get_value.get(pages, paginator.num_pages)

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)

    pageRange = len(paginator.page_range)
    pageBlock = total_page_num
    math_range = math.ceil(posts.number / pageBlock)
    endPage = math_range * pageBlock
    startPage = (endPage - pageBlock) + 1
    prev = False if startPage == 1 else True
    nxt = False if endPage >= pageRange else True
    prevPage = startPage - pageBlock
    nxtPage = endPage + 1
    blockRange = paginator.page_range[startPage - 1: endPage]

    context = [posts, prev, nxt, prevPage, nxtPage, blockRange]

    return context
