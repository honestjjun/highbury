from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Avg
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import reverse

from lib.paginator import paginator
from tag.models import Comment, Recommend

from .models import Product, UsePoint, Category
from .forms import UsePointForm


def point_list(request, category_id=None):
    category = None
    products = Product.objects.all()
    categories = Category.objects.filter(is_active=True).order_by('-created')

    if category_id:
        category = categories.get(id=category_id)
        if request.GET.get('sub_category'):
            products = products.filter(main_category=category_id, category=request.GET.get('sub_category'))
        else:
            products = products.filter(main_category=category_id)

    paginator = Paginator(products, 12)
    page = request.GET.get('page',1)
    try:
        products = paginator.page(page)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        products = paginator.page(paginator.num_pages)

    end_page = paginator.num_pages

    if request.is_ajax():
        return render(request, 'pointshop/list_ajax.jinja', {'products': products})

    return render(request, 'pointshop/list.jinja', {'products': products, 'end_page': end_page, 'categories': categories, 'select_menu': category})


@login_required
def point_detail(request, id, slug):
    point_ratio = None
    is_write = False

    # 상품의 리뷰와 댓글을 구함
    product = Product.objects.get(id=id, slug=slug)
    comments=product.comments.filter(sort='point-co').order_by('created',)
    reviews =product.comments.filter(sort='point-re').order_by('created',)
    sort_num = [len(reviews), len(comments)]
    # 평균 만족도를 구함
    if reviews:
        if request.user.nickname in reviews.values_list('user__nickname', flat=True):
            is_write = True
        point_ratio = reviews.aggregate(avg=Avg('satisfaction'))
    # paging 함수 (게시물 분리, 상품, 현재 페이지, 보여질 토탈 페이징)
    paging = paginator(reviews, request.GET, 'page', 'last', 3, 10)
    paging2 = paginator(comments, request.GET, 'sub_page', 'last', 20, 10)

    if request.method == 'POST':
        sort = request.POST.get('sort', None)
        if sort == 'buy_product':
            forms = UsePointForm(request.POST)
            if forms.is_valid():
                buy = forms.save(commit=False)
                product.buyer.add(request.user)
                buy.save()

                request.user.point.sort = 'spend'
                request.user.point.value = int(request.POST.get('use_point', None))
                request.user.point.save(update_fields=['sort', 'value', 'point'])

                return HttpResponseRedirect(reverse('pointshop:buy_complete', args=[product.id, product.slug, buy.order_number]))
        elif sort == 'write_comment':
            if not request.POST.get('content'):
                messages.error(request, '댓글에 아무것도 작성되어 있지 않습니다.')
                return HttpResponseRedirect(reverse('pointshop:detail', args=[product.id, product.slug]))
            else:
                Comment.objects.create(
                    content_object=product, user=request.user, sort='point-co', content=request.POST.get('content')
                )
                return HttpResponseRedirect(reverse('pointshop:detail', args=[product.id, product.slug]))
        else:
            review = request.POST.get('content')
            if not review:
                messages.error(request, '리뷰에 아무것도 작성되어 있지 않습니다.')
            if len(review) > 100:
                messages.error(request, '리뷰는 100글자 이하로 작성해주셔야 합니다.')
            elif not request.POST.get('satisfaction'):
                messages.error(request, '리뷰에는 만족도를 표시 해야 합니다.')
            else:
                Comment.objects.create(
                    user=request.user, sort='point-re', content=request.POST.get('content'),
                    satisfaction=request.POST.get('satisfaction'), content_object=product
                )
            return HttpResponseRedirect(reverse('pointshop:detail', args=[product.id, product.slug]))

    return render(request, 'pointshop/detail.jinja', {'product': product, 'point_ratio': point_ratio, 'reviews': paging, 'comments': paging2,
                                            'is_write': is_write, 'sort_num': sort_num})


def product_recommend(request, id, slug):
    if request.method == 'POST':
        action = request.POST.get('action', None)
        product = Product.objects.get(id=id, slug=slug)
        if action == '추천':
            Recommend.objects.create(
                user=request.user, content_object=product
            )
        else:
            ct = ContentType.objects.get_for_model(product)
            recommend = Recommend.objects.get(content_type=ct, object_id=product.id, user=request.user)
            recommend.delete()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'false'})


def buy_complete(request, id, slug, order_num):
    order = UsePoint.objects.get(order_number=order_num)
    return render(request, 'pointshop/buy_complete.jinja', {'order': order})


def delete(request, product_id, id, sort):
    product = Product.objects.get(id=product_id)
    if sort == 'comment':
        try:
            comment = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            messages.error(request, '댓글이 삭제 된 상태입니다.')
        else:
            comment.delete()
    elif sort == 'review':
        try:
            review = Comment.objects.get(id=id)
        except Comment.DoesNotExist:
            messages.error(request, '리뷰가 삭제된 상태입니다.')
        else:
            review.delete()
    return HttpResponseRedirect(reverse('pointshop:detail', args=[product.id, product.slug]))
