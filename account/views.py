from django.contrib.auth import authenticate, login as django_login, logout as django_logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage
from django.db.models import Avg
from django.http.response import HttpResponseRedirect, JsonResponse, HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.utils import timezone
from random import randint

from dateutil.relativedelta import relativedelta
from collections import Counter

from data.models import Match, PlayerSeason, TeamSeason, Team, UserPoint
from arsenal.models import EventVote, VoteQuestion
from advertise.models import Advertise
from board_free.models import FreeBoard, BeforeReview, AfterReview
from lib.confirm_text import confirm_text_length
from pointshop.models import UsePoint, Category
from lib.paginator import paginator
from tag.models import Tag, Tagging, Action

from .models import MyUser, RegistEmail
from .forms import MyUserForm, MyUserRegisterForm, MyUserProfileForm, NicknameForm, PasswordChangeForm, PasswordResetForm


def main(request):
    # 변수 선언
    recent_match_review = None
    next_match_review = None
    user_preview = {}

    # 아스날 로고를 받기 위해서 따로 불러와줌. 여긴 아스날 팬 카페이니...
    arsenal = Team.objects.get(name='Arsenal')

    # 1~4위 랭킹을 불러오고 만일 그 안에 아스날이 없으면 가장 마지막에 아스날을 순위에 붙임
    ranking = TeamSeason.objects.filter(league='england').values_list('team__name',flat=True).order_by('ranking', '-benefit', '-goal_benefit')[:4]
    if not 'Arsenal' in ranking:
        ranking = [TeamSeason.objects.get(team__name=team) for team in ranking]
        ranking.append(TeamSeason.objects.get(team__name='Arsenal'))

    # 각각 최근 글을 검색해옴
    recent_article = FreeBoard.active.filter(sort='free').order_by('-created')[:10]
    recent_review = FreeBoard.active.filter(sort__in=['after', 'before', 'player']).order_by('-created')[:10]

    # 최근 한달 동안 가장 많이 언급된 플레이어 리뷰 수를 구함 - created__gte=timezone.now()-relativedelta(days=30) filter에 들어가야 함
    player_reviews = FreeBoard.active.filter(sort='player').values_list('player_review__name__name', flat=True)
    player_reviews = Counter(player_reviews)
    player_sort = sorted(player_reviews.items(), key=lambda x:x[1], reverse=True)[:4]
    player_sort = [[PlayerSeason.objects.get(name__name=player[0]), round(player[1]/len(player_reviews)*100,1)] for player in player_sort]

    # 오늘을 기준으로 최근 경기과 다음 경기를 불러옴
    recent_match = Match.recent.all()[0]
    next_match = Match.next.all()[0]

    # 최근 경기 간단 평점/다음 경기 스코어 맞추기/설문지 조사 참여 여부를 확인함
    if request.user.is_authenticated:
        # 최근 경기 평점 남겼는지에 대한 여부
        try:
            AfterReview.objects.get(match=recent_match, user=request.user, sort='0')
        except AfterReview.DoesNotExist:
            user_preview['simple_point'] = False
        else:
            user_preview['simple_point'] = True
        # 다음 경기 스코어 맞추기 참여 여부
        try:
            EventVote.objects.get(match=next_match, user=request.user)
        except EventVote.DoesNotExist:
            user_preview['score_correct'] = False
        else:
            user_preview['score_correct'] = True
        # 현재 진행중인 설문지 참여 여부
        user = 0
        votes = VoteQuestion.active.prefetch_related('vote_user_question')
        for vote in votes:
            for vote_user in vote.vote_user_question.all():
                if vote_user.user == request.user:
                    user += 1
        user_preview['question'] = round((user/len(votes))*100)

    # 구너 랭킹을 검색함
    user_ranking = UserPoint.objects.all().order_by('-point')[:6]

    by_all = []
    if recent_match:
        recent_match_review = FreeBoard.active.filter(sort='after', after_game_review=recent_match).order_by('-created',)[:5]
        is_after = AfterReview.objects.filter(match=recent_match)
        if is_after:
            team_point = AfterReview.objects.filter(sort='0', match=recent_match).aggregate(Avg('point'))
            team_point = round(team_point['point__avg'],1)
            # 최근 경기에서 팀 평점과 best_player, worst_player 를 구함
            match_player = [recent_match.player1, recent_match.player2, recent_match.player3, recent_match.player4, recent_match.player5,
                            recent_match.player6, recent_match.player7, recent_match.player8, recent_match.player9, recent_match.player10,
                            recent_match.player11, recent_match.player12, recent_match.player13, recent_match.player14]
            for player in match_player:
                if player:
                    player_point = player.afterreview_player.filter(match=recent_match).aggregate(Avg('point'))
                    by_all.append([player, round(player_point['point__avg'],1)])
            player_point_sort = sorted(by_all, key=lambda x:x[1], reverse=True)
            result_point = [[team_point, len(is_after)], player_point_sort[0], player_point_sort.pop()]
        else:
            result_point = None

    if next_match:
        next_match_review = FreeBoard.active.filter(sort='before', before_game_review=next_match).order_by('-created',)[:5]

    return render(request, 'main/main.jinja', {'arsenal': arsenal, 'ranking': ranking, 'recent_match': recent_match,
                                          'next_match': next_match, 'recent_match_review': recent_match_review, 'next_match_review': next_match_review,
                                          'result_point': result_point, 'user_ranking': user_ranking, 'recent_article': recent_article,
                                          'recent_review': recent_review, 'player_sort': player_sort, 'user_preview': user_preview})


def login(request):
    if request.method == 'POST':
        forms = MyUserForm(request.POST)
        if forms.is_valid():
            clean = forms.cleaned_data
            user = authenticate(email=clean['email'], password=clean['password'])
            if user is not None:
                if user.is_active:
                    django_login(request, user)

                    point = UserPoint.objects.get(user=request.user.id)
                    point.sort = 'login'
                    point.save()

                    return HttpResponseRedirect(reverse('account:main'))
                else:
                    messages.error(request, 'Your active is false, so please ask to admin@popcon.com')
            else:
                messages.error(request, 'You insert wrong information. Please Try again')
    else:
        forms = MyUserForm()
    return render(request, 'main/login/login.jinja', {'forms': forms})


@login_required
def logout(request):
    django_logout(request)
    return HttpResponseRedirect(reverse('account:main'))


def register_terms(request):
    if request.method == 'POST':
        agree = request.POST.get('terms_agree', None)
        if not agree:
            messages.error(request, '약관 동의를 선택하셔야 합니다.')
        else:
            if agree == '1':
                return HttpResponseRedirect(reverse('account:register_email'))
            elif agree == '2':
                messages.error(request, '동의를 하지 않을 경우 다음 단계로 넘어갈수 없습니다.')

    return render(request, 'main/register/register_terms.jinja', {})


def register_email(request):
    if request.method == 'POST':
        random_number = randint(100000,999999)
        try:
            email = request.POST.get('email-confirm', None)
        except ValueError:
            messages.error(request, '이메일이 존재하지 않습니다.')
        else:
            highbury_user = RegistEmail(email = email)
            highbury_user.save()
            subject = '{} 님에게 보내는 hightbury 인증 메일입니다.'.format(email)
            message = "인증 번호이며 아래 해당 번호를 입력해주시면 됩니다. \n {} \n 감사합니다. :D".format(random_number)
            send_mail(subject, message, 'ionman83@gmail.com', [email])
            return render(request, 'register/register_email_number.jinja', {'random_number': random_number, 'email': highbury_user})
    return render(request, 'main/register/register_email.jinja', {})


def register_email_check(request, value):
    if request.method == 'POST':
        email = request.POST.get('id', None)
        if value == 'register':
            if not email:
                return JsonResponse({'result':'none'})
            else:
                try:
                    MyUser.objects.get(email=email)
                except MyUser.DoesNotExist:
                    if check_email(email) == 'no_email':
                        return JsonResponse({'result':'no_email'})
                    else:
                        return JsonResponse({'result':'true'})
                else:
                    return JsonResponse({'result':'false'})
        elif value == 'password':
            if not email:
                return JsonResponse({'result':'none'})
            else:
                try:
                    MyUser.objects.get(email=email)
                except MyUser.DoesNotExist:
                    if check_email(email) == 'no_email':
                        return JsonResponse({'result': 'no_email'})
                    else:
                        return JsonResponse({'result':'false'})
                else:
                    return JsonResponse({'result':'true'})


def check_email(a):
    try:
        a.index('@') and a.index('.')
    except ValueError:
        return 'no_email'
    else:
        if a.split('@')[0].count('') < 5:
            return 'no_email'
        else:
            return 'good'


def register(request, email_barcode):
    user_photo = None
    user = get_object_or_404(RegistEmail, barcode=email_barcode)
    if request.method == 'POST':
        email = request.POST.get('user_email', None)
        if email:
            forms = MyUserRegisterForm(initial={'email': user})
            return render(request, 'main/register/register_user.jinja', {'forms': forms, 'email': user})
        else:
            year = request.POST.get('birth_year', None)
            month = request.POST.get('birth_month', None)
            day = request.POST.get('birth_day', None)
            if not year or not month or not day:
                messages.error(request, '생일 입력이 되지 않았습니다.',)
            elif len(year) != 4 or len(month) > 2 or len(day) > 2 or int(year) > 2017 or int(year) < 1940 or int(month) > 12 or int(day) > 31:
                messages.error(request, '생일 입력이 완전하지 않습니다.')
            else:
                forms = MyUserRegisterForm(data=request.POST)
                password1 = request.POST.get('password1')
                password2 = request.POST.get('password2')
                if password1 != password2:
                    messages.error(request, '비밀번호가 같지 않습니다.')
                else:
                    if not validation_password(password1):
                        messages.error(request, '비밀번호 형식이 맞지 않습니다.')
                    else:
                        try:
                            request.FILES['photo']
                        except KeyError:
                            pass
                        else:
                            user_photo = request.FILES['photo']
                        if forms.is_valid():
                            user = forms.save(commit=False)
                            user.date_of_birth = str(year)+'-'+str(month)+'-'+str(day)
                            user.set_password(forms.cleaned_data['password1'])
                            user.updated = timezone.now().date()+relativedelta(months=6)
                            user.save()
                            if user_photo:
                                forms2 = MyUserProfileForm(instance=user, files=request.FILES)
                                if forms2.is_valid():
                                    user_photo = forms2.save(commit=False)
                                    user_photo.pre_save()
                            point=UserPoint.objects.create(user=user)
                            return HttpResponseRedirect(reverse('account:register_done'))

    forms = MyUserRegisterForm(initial={'email':user})
    return render(request, 'main/register/register_user.jinja', {'forms': forms, 'email':user})


def validation_password(string):
    string_length = len(string)
    if string_length >= 10 or string_length <= 20:
        result = True if set("1234567890").intersection(string) else False
        if result:
            result_2 = True if set("!@#$%^&*()_-+=|{}[]:;,./<>?").intersection(string) else False
            if result_2:
                result_3 = True if set("QWERTYUIOPASDFGHJKLZXCVBNM").intersection(string) else False
                if result_3:
                    result_4 = True if set("qwertyuioplkjhgfdsazxcvbnm").intersection(string) else False
                    if result_4:
                        return True
                    else:
                        return False
                else:
                    return False
            else:
                return False
        else:
            return False
    else:
        return False


def register_done(request):
    arsenal = Team.objects.get(name='Arsenal')
    return render(request, 'main/register/register_done.jinja', {'arsenal': arsenal})


def password_email(request):
    if request.method == 'POST':
        random_number = randint(100000, 999999)
        try:
            email = request.POST.get('email-confirm', None)
        except ValueError:
            messages.error(request, '이메일이 존재하지 않습니다.')
        else:
            subject = '{} 님에게 보내는 hightbury 인증 메일입니다.'.format(email)
            message = "비밀번호 인증 번호이며 아래 해당 번호를 입력해주시면 됩니다. \n {}{} \n 감사합니다. :D".format('password',random_number)
            send_mail(subject, message, 'ionman83@gmail.com', [email])
            user = get_object_or_404(MyUser, email=email)
            return render(request, 'main/register/register_email_number.jinja', {'random_number': random_number, 'user':user.nickname})
    return render(request, 'main/login/password_email.jinja', {})


def password_change(request, nickname):
    user = MyUser.objects.get(nickname=nickname)

    if request.method == 'POST':
        forms = PasswordChangeForm(instance=user, data=request.POST)
        try:
            request.POST.get('password1', None) and request.POST.get('password2', None)
        except ValueError:
            messages.error(request, '비밀번호가 입력되지 않았습니다.')
        else:
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            if password1 != password2:
                messages.error(request, '비밀번호가 같지 않습니다.')
            else:
                if not validation_password(password1):
                    messages.error(request, '비밀번호 형식이 맞지 않습니다.')
                else:
                    if forms.is_valid():
                        user = forms.save(commit=False)
                        user.set_password(forms.cleaned_data['password1'])
                        user.save()
                        return HttpResponseRedirect(reverse('account:main'))

    forms = PasswordChangeForm(instance=user)
    return render(request, 'main/login/password_change.jinja', {'forms': forms, 'user': user})


def mypage(request):
    post_date = request.user.updated
    if post_date < timezone.now().date():
        update = True
    else:
        update = False
    if request.method == 'POST':
        forms = MyUserProfileForm(instance=request.user, data=request.POST)
        if forms.is_valid():
            user_profile = forms.save(commit=False)
            user_profile.save()
            return HttpResponseRedirect(reverse('account:profile'))
    else:
        forms = MyUserProfileForm(instance=request.user)
    profile_top_advertisements = Advertise.objects.filter(is_active=True, event_end__gt=timezone.now(), event_start__lt=timezone.now(), sort='profile_top')
    nickname_change = NicknameForm()
    return render(request, 'main/mypage/mypage.jinja', {'select':'my_info', 'forms': forms, 'nickname_change': nickname_change, 'update': update,
                                                     'profile_top_advertisements': profile_top_advertisements})


def input_picture(request):
    if request.method == 'POST':
        try:
            request.FILES['photo']
        except KeyError:
            return HttpResponseRedirect(reverse('account:mypage'))
        forms = MyUserProfileForm(instance=request.user, files={'photo': request.FILES['photo']})
        if forms.is_valid():
            user_profile = forms.save(commit=False)
            user_profile.update()
            return HttpResponseRedirect(reverse('account:mypage'))
        else:
            return HttpResponseRedirect(reverse('account:main'))


def same_nickname(request):
    if request.method == 'POST':
        nickname_value = request.POST.get('id', None)
        if confirm_string(nickname_value):
            try:
                MyUser.objects.get(nickname=nickname_value)
            except MyUser.DoesNotExist:
                return JsonResponse({'result': 'true'})
            else:
                return JsonResponse({'result': 'false'})
        else:
            return JsonResponse({'result': 'none'})


def confirm_string(string):
    if None:
        return False
    # lib 에 있는 confirm_text_length 를 구해와서 글자의 길이를 구함 (endcode를 통해 한글이랑 영어 글자 길이를 다르게 구해야함)
    string_value = confirm_text_length(string)
    if string_value >= 4 and string_value <= 15:
        result = False if set("`~!@#$%^&*()_+|-=\{[}]:;\"'>.<,?/ㅂㅈㄷㄱㅅㅁㄴㅇㄹㅎㅋㅌㅊㅍ"
                                "ㅛㅕㅑㅐㅔㅗㅓㅏㅣㅠㅜㅡㅃㅉㄸㄲㅆㅒㅖㅀㅄㄳㅢㅙㅘㅚㅟㅝ").intersection(string) else True
        if result:
            return string, True
        else:
            return False
    else:
        return False


def nickname_input(request):
    if request.method == 'POST':
        nickname_value = request.POST.get('id')
        user = request.user
        user.nickname = nickname_value
        user.updated = timezone.now().date()+relativedelta(months=6)
        user.save()
        return JsonResponse({'result': 'ok'})


def profile(request, user):
    try:
        users = MyUser.objects.get(nickname=user, is_active=True)
    except MyUser.DoesNotExist:
        messages.error(request, '현재 등록되어있지 않은 유저 입니다.')
        return HttpResponseRedirect(reverse('account:main'))
    else:
        pass

    # arsenal 로고
    arsenal = Team.objects.get(name='Arsenal')

    # 이벤트에 등록되었는지 확인
    event_num = EventVote.objects.filter(user=users)
    if not event_num:
        event = {}
    else:
        event_result = event_num.filter(is_result=True)
        event = {'event_num': len(event_num), 'event_result': len(event_result), 'event_ratio': round(len(event_result)/len(event_num)*100,0)}

    # 유저가 가장 많이 사용한 tag 를 구함
    user_tags = Tagging.objects.filter(user=users, created__gt=timezone.now() - relativedelta(days=30)).values('tag',)
    total_tags = len(user_tags)
    most_tags = Counter([Tag.objects.get(id=tag['tag']) for tag in user_tags])
    most_tags = [(tag[0], round((tag[1]/total_tags)*100, 1)) for tag in most_tags.items()]
    tags = sorted(most_tags, key=lambda x:x[1], reverse=True)[:5]

    # 경기 후 리뷰에서 유저가 준 점수
    after_list=[]
    team_point_ratio = AfterReview.objects.filter(user=users, sort='0').aggregate(Avg('point'))
    if team_point_ratio['point__avg']:
        players = PlayerSeason.objects.all()
        for player in players:
            player_point = player.afterreview_player.filter(user=users).aggregate(Avg('point'))
            if player_point['point__avg']:
                avg_point = round((player_point['point__avg'])/int(len(player.afterreview_player.filter(user=users))),1)
                after_list.append([player, avg_point])
        after_sorted = sorted(after_list, key=lambda x:x[1], reverse=True)
        after = [round(team_point_ratio['point__avg'],1), after_sorted[0], after_sorted.pop()]
    else:
        after = None

    # 경기 프리뷰에서 유저가 준 점수
    before = []
    if BeforeReview.objects.filter(user=users):
        a = 0
        while a <= 11:
            if a == 0:
                before_strategies = BeforeReview.objects.filter(user=users, sort=str(a)).values('strategy',)
                before_strategies = Counter([strategy['strategy'] for strategy in before_strategies])
                before.append(sorted(before_strategies.items(), key=lambda x:x[1], reverse=True)[:1])
            else:
                before_players = BeforeReview.objects.filter(user=users, sort=str(a), player__isnull=False).values('player',)
                before_players = Counter([PlayerSeason.objects.get(id=player['player']) for player in before_players])
                before.append(sorted(before_players.items(), key=lambda x:x[1], reverse=True)[:1])
            a += 1
    else:
        pass
    return render(request, 'main/profile/profile_main.jinja', {'user': users, 'tags': tags, 'before': before, 'after': after,
                                                          'arsenal': arsenal, 'profile': '1', 'event': event})


def profile_write(request, user):
    posts = FreeBoard.active.filter(is_active=True, user__nickname=user)
    try:
        users = MyUser.objects.get(nickname=user, is_active=True)
    except MyUser.DoesNotExist:
        messages.error(request, '현재 등록되어있지 않거나 탈퇴된 유저입니다.')
        return HttpResponseRedirect(reverse('account:main'))
    else:
        pass
    # paging 함수 (게시물 분리, 상품, 현재 페이지, 보여질 토탈 페이징)
    paging = paginator(posts, request.GET, 'page', 'first', 20, 10)
    return render(request, 'main/profile/profile_write.jinja', {'user': users, 'profile': '2', 'paging': paging})


def profile_achievements(request, user, sort):
    complete = 0
    total = 0
    try:
        users = MyUser.objects.get(nickname=user, is_active=True)
    except MyUser.DoesNotExist:
        messages.error(request, '현재 등록되어있지 않거나 탈퇴된 유저입니다.')
        return HttpResponseRedirect(reverse('account:main'))
    else:
        pass

    categories = Category.objects.all().order_by('id').prefetch_related('sub_category__product')
    now_category = categories.get(id=sort)
    for category in now_category.sub_category.all():
        for product in category.product.all():
            total += 1
            if users in product.buyer.all():
                complete += 1
    if complete == 0:
        get = [complete, total, 0]
    else:
        get = [complete, total, round(complete / total*100,0)]
    return render(request, 'main/profile/profile_achievements.jinja', {'profile': '3', 'user':users, 'categories': categories,
                                                                  'now_category': now_category, 'get': get, 'sort': int(sort)})


def point(request):
    self_user = UserPoint.objects.get(user=request.user)
    max_user = UserPoint.objects.all()[:1000]
    if self_user in max_user:
        value = True
        i=0
        while i<1000:
            i+=1
            if self_user == max_user[i-1]:
                break
            else:
                continue
        user_ranking = i
    else:
        value = None

    return render(request, 'main/mypage/point/point.jinja', {'select': 'point', 'self_user': self_user, 'value': value, 'user_ranking': user_ranking})


def mypage_password_change(request):
    if request.method == 'POST':
        forms = PasswordResetForm(instance=request.user, data=request.POST)
        if forms.is_valid():
            word = forms.cleaned_data
            try:
                authenticate(email=request.user, password=word['old_password'])
            except ValueError:
                return JsonResponse({'status': 'wrong_old_password'})
            else:
                password1 = word['new_password1']
                password2 = word['new_password2']
                if not validation_password(password1):
                    return JsonResponse({'status': 'wrong_password1'})
                else:
                    if password1 != password2:
                        return JsonResponse({'status': 'wrong_both'})
                    else:
                        user = forms.save(commit=False)
                        user.set_password(forms.cleaned_data['new_password1'])
                        user.save()

                        return JsonResponse({'status': 'success_change'})
        else:
            return JsonResponse({'status':'wrong_data'})


def notify(request):
    actions = Action.objects.filter(to_user=request.user, created__gte=timezone.now()-relativedelta(days=7)).order_by('-created')

    paginator = Paginator(actions, 30)
    page = request.GET.get('page', 1)
    try:
        actions = paginator.page(page)
    except EmptyPage:
        if request.is_ajax():
            return HttpResponse('')
        actions = paginator.page(paginator.num_pages)

    end_page = paginator.num_pages

    if request.is_ajax():
        return render(request, 'main/mypage/notify/notify_ajax.jinja', {'actions': actions})

    return render(request, "main/mypage/notify/notify.jinja", {'select':'notify', 'actions': actions, 'end_page': end_page})


def use_point(request):
    products = UsePoint.objects.select_related('product').filter(user=request.user).order_by('-buy_date')
    len_products = len(products)

    # paging 함수 (게시물 분리, 상품, 현재 페이지, 보여질 토탈 페이징)
    paging = paginator(products, request.GET, 'page', 'first', 10, 10)

    return render(request, "main/mypage/point/use_point.jinja", {'select':'user_point', 'products': paging[0], 'len_products': len_products,
                                                             'prev': paging[1], 'nxt': paging[2], 'prevPage': paging[3], 'nxtPage': paging[4],
                                                             'blockRange': paging[5]})


def achievement(request, sort):
    product_all = 0
    product_complete = 0
    categories = Category.objects.all().order_by('id').prefetch_related('sub_category__product')
    now_category = categories.get(id=sort)
    for category in now_category.sub_category.all():
        if category.product.all():
            for product in category.product.all():
                product_all += 1
                if request.user in product.buyer.all():
                    product_complete += 1
    product_ratio = [product_all, product_complete, round((product_complete / product_all) * 100, 1)]
    return render(request, "main/mypage/achievements/achievements.jinja", {'select':'achievement', 'categories': categories, 'now_category': now_category,
                                                                      'product_ratio': product_ratio, 'sort': int(sort)})
