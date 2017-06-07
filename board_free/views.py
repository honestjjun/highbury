from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils import timezone

from data.models import Team, Match, PlayerSeason
from lib.confirm_text import no_space_text

from tag.models import Action
from .models import FreeBoard, BeforeReview, AfterReview
from .forms import FreeBoardForm, SearchForm
from tag.models import Comment, Recommend
from lib.paginator import paginator
from lib.tag import tag
from lib.point import point
from lib.summernote import value



# 게시판 > 리스트
def list(request, value=None):
    search_boolean = False
    select_value = False
    search = None

    if value:
        categories = [('before', '경기 프리뷰'), ('after', '경기 후 리뷰'), ('player', '선수 리뷰')]

        if request.GET.get('category'):
            posts_list = FreeBoard.active.filter(sort=request.GET.get('category')).order_by('-created',)
        elif request.GET.get('id'):
            match_id = request.GET.get('id')
            if value == 'after':
                posts_list = FreeBoard.active.filter(after_game_review=match_id).order_by('-created',)
            elif value == 'before':
                posts_list = FreeBoard.active.filter(before_game_review=match_id).order_by('-created',)
            elif value == 'player':
                posts_list = FreeBoard.active.filter(player_review=match_id).order_by('-created',)
        else:
            posts_list = FreeBoard.active.filter(sort__in=['before', 'after', 'player']).order_by('-created', )
    else:
        posts_list = FreeBoard.objects.filter(is_superuser=False)
        notifies = FreeBoard.objects.filter(is_superuser=True)

    if request.method == 'POST':
        # search_value 가 있으면 검색
        forms = SearchForm(request.POST)
        if forms.is_valid():
            search_boolean = True
            if value:
                posts_list = FreeBoard.active.filter(sort__in=['before', 'after', 'player'])
            search = forms.cleaned_data['search_value']
            select_value = request.POST.get('searchSelect')
            if select_value == '0':
                posts_list = posts_list.filter(Q(title__icontains=search) | Q(body__icontains=search)).distinct()
            elif select_value == '1':
                posts_list = posts_list.filter(Q(title__icontains=search)).distinct()
            else:
                posts_list = posts_list.filter(Q(user__nickname__icontains=search)).distinct()

    if search_boolean:
        forms = SearchForm(initial={'search_value': search})
    else:
        forms = SearchForm()

    # paging 함수 (게시물 분리, 상품, request.GET, 'page', 처음 보여질 페이지, 한페이지에 보여질 수, 보여질 토탈 페이징)
    paging = paginator(posts_list, request.GET, 'page', 'first', 20, 10)

    if value:
        move_url = 'board/review_list.jinja'
        context = {'select_value': select_value, 'search_value': search, 'paging': paging, 'forms': forms,
                   'value': value, 'categories': categories}
    else:
        move_url = 'board/list.jinja'
        context = {'select_value': select_value, 'search_value': search, 'paging': paging, 'forms': forms,
                   'notifies': notifies}
    return render(request, move_url, context)


# 자유 게시판의 디테일 페이지
def detail(request, id, slug, comment_id=None):
    post = get_object_or_404(FreeBoard, id=id, slug=slug)
    if post.sort == 'before':
        post_before = BeforeReview.objects.filter(match=post.before_game_review).order_by('id')
    elif post.sort == 'after':
        post_after = AfterReview.objects.filter(match=post.after_game_review).order_by('id')
    # 댓글과 대댓글을 comments_list list 에 담음
    comments_list = []
    ct = ContentType.objects.get_for_model(post)
    comments = Comment.objects.filter(content_type=ct, object_id=post.id, comment__isnull=True, is_active=True).order_by('created',)
    for comment in comments:
        comments_list.append(comment)
        if comment.comment_set:
            for sub_comment in comment.comment_set.all().order_by('created',):
                comments_list.append(sub_comment)

    # 댓글과 대댓글 입력
    if request.method == 'POST':
        # comment_id 가 있다는 것은 대댓글
        if comment_id:
            comment_to = Comment.objects.get(id=comment_id)
            if comment_to.comment:
                post.comments.create(
                    user=request.user, sort='free-co', content=request.POST.get('content'), comment=comment_to.comment,
                    commenting_user=str(comment_to.user)
                )
            else:
                post.comments.create(
                    user=request.user, sort='free-co', content=request.POST.get('content'), comment=comment_to,
                    commenting_user=str(comment_to.user)
                )
            # 대댓글을 남긴 대상이 자신이 아닐 경우 and 댓글 user 과 post user 이 다르다면 댓글로 Action 생성
            if comment_to.user != request.user and comment_to.user != post.user:
                Action.objects.create(content_object=post, sort='comment', user=request.user, to_user=comment_to.user,
                                      comment = comment_to)
        else:
            post.comments.create(
                user=request.user, sort='free-co', content=request.POST.get('content')
            )
        #Action.objects.create(content_object=comment, sort='free-co', user=request.user) # action 은 아직 미구현

        # post 의 작가가 자신이 아니라면 Action 생성
        if post.user != request.user:
            Action.objects.create(content_object=post, sort='post', user=request.user, to_user=post.user)

        # 포인트 함수
        point(request.user, 'comment')
        return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))

    # paging 함수 (게시물 분리, 상품, request.GET, 'page', 처음 보여질 페이지, 한페이지에 보여질 수, 보여질 토탈 페이징)
    paging = paginator(comments_list, request.GET, 'page', 'last', 10, 10)

    is_action = Action.objects.filter(to_user=request.user, content_type=ct, object_id=post.id, is_confirm=False, created__gte=timezone.now()-relativedelta(days=7))
    if is_action:
        for action in is_action:
            action.is_confirm = True
            action.save(update_fields=['is_confirm'])

    if post.sort == 'before':
        context_dict = {'post_before': post_before, 'post': post, 'paging': paging}
    elif post.sort == 'after':
        context_dict = {'post_after': post_after, 'post': post, 'paging': paging}
    else:
        context_dict = {'post': post, 'paging': paging}
    return render(request, 'board/detail.jinja', context_dict)


# write 를 누르게 되었을 때 글작성 종류를 선택하게 된다.
@login_required()
def choice_write(request):
    return render(request, 'board/choice_write/choice_write.jinja', {})


# 무슨 글을 남길지에 대해서 선택을 하게 된다.
@login_required()
def choice_game(request, sort):
    after_game = None
    before_game = None
    player_review = None
    if sort == 'after':
        after_game = Match.recent.all()
    elif sort == 'before':
        before_game = Match.next.all()
    elif sort == 'player':
        player_review = PlayerSeason.objects.filter(team__name='Arsenal')
    return render(request, 'board/choice_write/choice_game.jinja', {'sort': sort, 'before_game': before_game, 'after_game': after_game, 'player_review': player_review})


# 게시글 > 쓰기
@login_required()
def write_free(request):
    if request.method == 'POST':
        post = FreeBoard.objects.create(
            sort='free', title=request.POST.get('title', ), body=value(request.POST.get('body', )), user=request.user
        )
        # 태그 함수 (object의 tag들, object, 요청한 유저, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
        tags = request.POST.get('tags', None)
        tag(tags, post, request.user, 'free', [])
        # 포인트 함수
        point(request.user, 'free')
        return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))
    else:
        forms = FreeBoardForm()
    return render(request, 'board/choice_write/write/write_free.jinja', {'forms': forms})


@login_required()
def write_before(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    gk_players = PlayerSeason.objects.filter(position='GK')
    df_players = PlayerSeason.objects.filter(position='DF')
    mf_players = PlayerSeason.objects.filter(position='MF')
    fw_players = PlayerSeason.objects.filter(position='FW')

    if request.method == 'POST':
        for a in range(12):
            if a == 0:
                if not request.POST.get('strategy'):
                    messages.error(request, '전술을 선택하셔야 합니다.')
                    return HttpResponseRedirect(reverse('board_free:write_before', args=[match.id]))
            elif a > 0:
                if not request.POST.get('player'+str(a)):
                    messages.error(request, '선수 11명을 전부 입력해주셔야 합니다.')
                    return HttpResponseRedirect(reverse('board_free:write_before', args=[match.id]))
        post = FreeBoard.objects.create(
            sort='before', title=request.POST.get('title',), body=value(request.POST.get('body',)),
            user=request.user, before_game_review=match
        )
        before_review_list = []
        for a in range(12):
            if a == 0:
                before_review_list.append(BeforeReview(
                    freeboard=post, match=match, user=request.user, sort=str(a), strategy=request.POST.get('strategy')
                ))
            elif a > 0:
                before_review_list.append(BeforeReview(
                    freeboard=post, match=match, user=request.user, sort=str(a), player=PlayerSeason.objects.get(id=request.POST.get('player'+str(a)))
                ))
        BeforeReview.objects.bulk_create(before_review_list)
        # 태그 함수 (object의 tag들, object, 요청한 유저, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
        tags = request.POST.get('tags', None)
        tag(tags, post, request.user, 'free', [])
        # 포인트 함수
        point(request.user, 'review')
        return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))
    forms = FreeBoardForm()
    return render(request, 'board/choice_write/write/write_before.jinja', {'match': match, 'forms': forms, 'gk_players': gk_players,
                                                                'df_players': df_players, 'mf_players': mf_players, 'fw_players': fw_players})


# 경기 후 리뷰 작성 폼
@login_required()
def write_after(request, match_id):
    match = get_object_or_404(Match, id=match_id)
    match_player = [
        match.player1, match.player2, match.player3, match.player4, match.player5, match.player6, match.player7, match.player8,
        match.player9, match.player10, match.player11, match.player12, match.player13, match.player14
    ]
    if request.method == 'POST':
        for a in range(1, 15):
            if match_player[a - 1]:
                string = request.POST.get('player' + str(a) + '_review')
                if no_space_text(string) <= 10:
                    messages.error(request, '모든 출천 선수에 대해 10글자 이상 리뷰를 입력해주셔야 합니다.')
                    return HttpResponseRedirect(reverse('board_free:write_after', args=[match.id]))
        post = FreeBoard.objects.create(
            sort='after', title=request.POST.get('title', ), body=value(request.POST.get('body', )),
            user=request.user, after_game_review=match
        )
        after_review_list = []
        for i in range(15):
            if i == 0:
                after_review_list.append(AfterReview(
                    freeboard=post, match=match, sort=str(i), point=request.POST.get('team_point'),
                    user=request.user, is_simple=False
                ))
            if i > 0:
                if match_player[i - 1]:
                    after_review_list.append(AfterReview(
                        freeboard=post, match=match, sort=str(i), player=match_player[i-1],
                        user=request.user, point=request.POST.get('player'+str(i)+'_point'),
                        review=request.POST.get('player'+str(i)+'_review'), is_simple=False
                    ))
                else:
                    after_review_list.append(AfterReview(
                        freeboard=post, match=match, sort=str(i), user=request.user, is_simple=False
                    ))
        AfterReview.objects.bulk_create(after_review_list)
        # 태그 함수 (object의 tag들, object, 요청한 유저, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
        tags = request.POST.get('tags', None)
        tag(tags, post, request.user, 'free', [])
        # 포인트 함수
        point(request.user, 'review', 'after')

        return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))

    forms = FreeBoardForm()
    return render(request, 'board/choice_write/write/write_after.jinja', {'match': match, 'match_player': match_player, 'forms': forms})


# 선수 리뷰 작성 폼
@login_required()
def write_player(request, id):
    player = PlayerSeason.objects.get(id=id)
    if request.method == 'POST':
        post = FreeBoard.objects.create(
            sort='player', title=request.POST.get('title', ), body=value(request.POST.get('body',)),
            user=request.user, player_review=player
        )

        # 태그 함수 (object의 tag들, object, 요청한 유저, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
        tags = request.POST.get('tags', None)
        tag(tags, post, request.user, 'free', [])
        # 포인트 함수
        point(request.user, 'review', 'player')
        return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))
    forms = FreeBoardForm()
    return render(request, 'board/choice_write/write/write_player.jinja', {'player': player, 'forms': forms})


# 게시글 > 수정
@login_required()
def change(request, id, slug, sort):
    after_game = None
    after_match = None
    before_game = None
    before_match = None

    post = FreeBoard.objects.get(id=id, slug=slug)
    if sort == 'after':
        after_game = AfterReview.objects.filter(freeboard=post, user=request.user).order_by('id')
        after_match = Match.objects.get(id = post.after_game_review.id)
    elif sort == 'before':
        before_game = BeforeReview.objects.filter(freeboard=post, user=request.user).order_by('id')
        before_match = Match.objects.get(id = post.before_game_review.id)
    post_tags = post.tags.all().values_list('tag__name', flat=True)
    recent_tags = ','.join(post_tags)

    if request.method == 'POST':
        if sort == 'free' or sort == 'before' or sort == 'player':
            FreeBoard.objects.filter(id=id, slug=slug).update(
                title=request.POST.get('title'),
                body=value(request.POST.get('body'))
            )
            if post_tags:
                # 태그 함수 (object의 tag들, object, 요청한 유저, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
                tags_list = [post for post in post_tags]
                tags = request.POST.get('tags', None)
                tag(tags, post, request.user, 'free', tags_list)

            return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))
        elif sort == 'after':
            for a in range(1, 15):
                if request.POST.get('player' + str(a)):
                    string = request.POST.get('player'+str(a)+'_review')
                    if no_space_text(string) <= 10:
                        messages.error(request, '모든 출천 선수에 대해 10글자 이상 리뷰를 입력해주셔야 합니다.')
                        return HttpResponseRedirect(reverse('board_free:change', args=[post.id, post.slug, 'after']))
            FreeBoard.objects.filter(id=id, slug=slug).update(
                title=request.POST.get('title'),
                body=value(request.POST.get('body'))
            )
            insert_list = []
            for a in range(1, 15):
                player = request.POST.get('player'+str(a))
                if player:
                    AfterReview.objects.filter(match=after_match, user=request.user, id=player).update(
                        review=request.POST.get('player'+str(a)+'_review')
                    )
            if post_tags:
                # 태그 함수 (object의 tag들, object, 요청한 유저, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
                tags_list = [post for post in post_tags]
                tags = request.POST.get('tags', None)
                tag(tags, post, request.user, 'free', tags_list)

            return HttpResponseRedirect(reverse('board_free:detail', args=[post.id, post.slug]))
    else:
        forms = FreeBoardForm(instance=post)
        if sort == 'free':
            return render(request, 'board/choice_write/change/change_free.jinja', {'tag': recent_tags, 'forms': forms, 'value': sort})
        elif sort == 'player':
            return render(request, 'board/choice_write/change/change_free.jinja', {'tag': recent_tags, 'forms': forms, 'value': sort, 'post': post})
        elif sort == 'after':
            return render(request, 'board/choice_write/change/change_after.jinja', {'match': after_match, 'team': after_game[0], 'players': after_game[1:], 'tag': recent_tags, 'forms': forms})
        elif sort == 'before':
            return render(request, 'board/choice_write/change/change_before.jinja', {'match': before_match, 'player': before_game, 'tag': recent_tags, 'forms': forms})



# 게시글 > 삭제
@login_required()
def article_delete(request, id, slug):
    article = get_object_or_404(FreeBoard, id=id, slug=slug)
    article.delete()
    return HttpResponseRedirect(reverse('board_free:list'))


# 게시글 > 추천
@login_required()
def article_recommend(request, id, slug):
    action = request.POST.get('action', None)
    post = get_object_or_404(FreeBoard, id=id, slug=slug)
    if request.method == 'POST':
        if action == '추천':
            Recommend.objects.create(
                user=request.user, content_object=post
            )
        else:
            ct = ContentType.objects.get_for_model(post)
            recommend = Recommend.objects.get(content_type=ct, object_id=post.id, user=request.user)
            recommend.delete()
        return JsonResponse({'status': 'ok'})
    else:
        return JsonResponse({'status': 'false'})


# 댓글 > 댓글 삭제
@login_required()
def comment_delete(request, id, slug, comment_id):
    comment = Comment.objects.get(id=comment_id)
    if comment.comment_set.all():
        Comment.objects.filter(id=comment_id).update(is_delete=True)
    else:
        comment.delete()
    return HttpResponseRedirect(reverse('board_free:detail', args=[id, slug]))
