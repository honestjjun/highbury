from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django_summernote.models import Attachment
from django.utils import timezone
from django.contrib import messages

from data.models import Match, PlayerSeason
from data.forms import MatchForm
from board_free.models import FreeBoard
from account.models import MyUser
from lib.confirm_text import no_space_text
from lib.tag import tag
from pointshop.models import Product
from tag.models import Comment

from .models import Charge
from .forms import ChatForm
from arsenal.models import EventVote
from message.models import Message
from lib.summernote import find_src
from lib.point import point

import os


def delete_trash_picture(request):
    # posts 에 있는 모든 src list 에 수집하기
    posts = FreeBoard.objects.all()
    post_body = []
    find_src(posts, post_body)

    # summernote model 의 Attachment 에 있는 모든 picture 을 list 에 수집하기
    summernote_all = Attachment.objects.all()
    summernote_list = []
    for summernote in summernote_all :
        summernote_list.append(summernote.file.name)

    # 모든 유저들의 프로필 사진의 리스트
    users = MyUser.objects.all()
    user_profile_picture_list = []
    for user in users:
        user_photo_name = user.photo.name.replace('profile_photo/','')
        user_profile_picture_list.append(user_photo_name)

    # media/profile_photo/ 에 등록된 파일 수
    profile_photo_list = os.listdir(os.path.join(settings.MEDIA_ROOT,'profile_photo'))

    # 위에서 만든 것을 집합으로 변환 후 차집합을 구함
    a1, a2, s1, s2 = set(post_body), set(summernote_list), set(user_profile_picture_list), set(profile_photo_list)
    trash_summernote_pictures = a2.difference(a1)
    trash_profile_pictures = s2.difference(s1)

    if request.method == 'POST':
        # trash_summernote 파일 삭제
        for trash_summernote_picture in trash_summernote_pictures:
            os.remove(os.path.join(settings.MEDIA_ROOT, trash_summernote_picture))
            remove_file = Attachment.objects.filter(file=trash_summernote_picture)
            remove_file.delete()
        # trash_profile_photo 파일 삭제
        for trash_profile_picture in trash_profile_pictures:
            os.remove(os.path.join(settings.MEDIA_ROOT,'profile_photo/'+trash_profile_picture))

        return HttpResponseRedirect(reverse('administrator:delete_trash_picture'))

    return render(request, 'admin/sub_main/delete_trash_picture.jinja', {'a1': a1, 'a2': a2, 'trash_summernote_pictures': trash_summernote_pictures,
                                                                        's1': s1, 's2': s2, 'trash_profile_pictures': trash_profile_pictures})


def input_game_select(request):
    games = Match.objects.filter(match_date__lte=timezone.now(), result__isnull=True)
    return render(request, 'admin/sub_main/input_game_select.jinja', {'games': games})


# 경기 결과 입력
def input_game_result(request, match_id):
    match_game = Match.objects.get(id=match_id)
    players = PlayerSeason.ing.filter(team__name='Arsenal')
    field_players = {'gk_players': players.filter(position='GK'), 'df_players': players.filter(position='DF'),
                     'mf_players': players.filter(position='MF'), 'fw_players': players.filter(position='FW')}

    # match_id 가 있다는 것은 관리자가 경기 결과를 입력하였다는 것이다.
    if request.method == 'POST':
        if match_game.result:
            messages.error(request, '현재 결과가 등록 되어있는 경기 입니다.')
            return HttpResponseRedirect(reverse('administrator:input_game_result'))
        else:
            aa = 0
            while aa < 11:
                aa += 1
                player = request.POST.get('player'+str(aa), None)
                if not player:
                    messages.error(request, '선발 라인업을 다시 구성해주시기 바랍니다.')
                    return HttpResponseRedirect(reverse('administrator:input_game_result'))

            forms = MatchForm(instance=match_game, data=request.POST)
            if forms.is_valid():
                game_result = forms.save(commit=False)
                if game_result.result == 'win':
                    if game_result.home_score > game_result.away_score:
                        game_result.save()
                        try:
                            users = EventVote.objects.filter(match=match_id, home_score=game_result.home_score, away_score=game_result.away_score)
                        except EventVote.DoesNotExist:
                            pass
                        else:
                            for user in users:
                                # 포인트 함수
                                point(user, 'correct_vote')
                                user.is_result = True
                                user.save(update_fields='is_result')
                    else:
                        messages.error(request, '스코어가 잘못 입력되었습니다. 다시 한번 확인부탁드립니다.')
                        return HttpResponseRedirect(reverse('administrator:input_game_result'))
                elif game_result.result == 'draw':
                    if game_result.home_score == game_result.away_score:
                        game_result.save()
                    else:
                        messages.error(request, '스코어가 잘못 입력되었습니다. 다시 한번 확인부탁드립니다.')
                        return HttpResponseRedirect(reverse('administrator:input_game_result'))
                elif game_result.result == 'lose':
                    if game_result.home_score < game_result.away_score:
                        game_result.save()
                    else:
                        messages.error(request, '스코어가 잘못 입력되었습니다. 다시 한번 확인부탁드립니다.')
                        return HttpResponseRedirect(reverse('administrator:input_game_result'))

                    return HttpResponseRedirect(reverse('administrator:input_game_result'))
    forms = MatchForm()
    return render(request, 'admin/sub_main/input_game_result.jinja', {'match': match_game, 'forms': forms, 'players': players, 'gk_players': field_players['gk_players'],
                                                                     'df_players': field_players['df_players'], 'mf_players': field_players['mf_players'],
                                                                     'fw_players': field_players['fw_players']})


def charge(request):
    charges = Charge.objects.prefetch_related('content_object')
    charges_list = []
    for charge in charges:
        if charge.content_object:
            if not charge.charge:
                charges_list.append(charge)
        else:
            charge.delete()
    return render(request, 'admin/sub_main/charge_table.jinja', {'charges': charges_list})


def ajax_charge_save(obj, obj_id, result, user):
    obj.content_object.is_active = False
    obj.content_object.save(update_fields=['is_active'])

    Charge.objects.filter(id=obj_id).update(result_now='yes', result=result, result_date=timezone.now(), result_who=user)
    return JsonResponse({'status': 'success'})


def charge_result_ajax(request):
    if request.method == 'POST':
        charge_id = request.POST.get('id', None)
        result = request.POST.get('result', None)

        charge = Charge.objects.get(id=charge_id)
        if charge.sort == 'free' or charge.sort == 'comment':
            user = charge.content_object.user
        elif charge.sort == 'message':
            user = charge.content_object.send_user
        elif charge.sort == 'etc':
            user = charge.content_object

        if charge.result_now == 'no':
            if result == 'yellow':
                if user.is_yellow:
                    if user.is_red:
                        pass
                    else:
                        user.is_red = True
                        user.save(update_fields=['is_red'])
                else:
                    user.is_yellow = True
                    user.save(update_fields=['is_yellow'])

                if not charge.sort == 'etc':
                    return_result = ajax_charge_save(charge, charge_id, result, request.user)
                    return return_result

            elif result == 'delete':
                return_result = ajax_charge_save(charge, charge_id, 'delete', request.user)
                return return_result

            elif result == 'maintain':
                Charge.objects.filter(id=charge_id).update(result_now='yes', result='maintain', result_date=timezone.now(), result_who=request.user)
                return JsonResponse({'status': 'success'})
        else:
            return JsonResponse({'status': 'already_result'})


'''
    넘어오는 변수 - sort, charge_reason, charge_to, content

    신고의 경우의 수
    1. 내가 신고를 하였는데 내가 신고한게 없음 - charge_success
    2. 내가 신고를 하였는데 내가 신고한게 있음 - charge_already
    3. 내가 신고를 하였는데 다른 사람이 신고한게 있음(result_now=no) - charge_success (대신 기존꺼에 is_charge 진행이 됨)
    4. 내가 신고를 하였는데 다른 사람이 신고하게 있음(result_now=yes) - charge_already_done
'''
def charge_ajax(request):
    if request.method == 'POST':
        sort = request.POST.get('sort', None)
        object_value = request.POST.get('charge_to', None)
        charge_reason = request.POST.get('charge_reason', None)
        content = request.POST.get('content', None)
        print(request.POST.get('charge_reason'))
        if no_space_text(content) == 0:
            return JsonResponse({'status': 'charge_empty'})
        elif no_space_text(content) <= 10:
            return JsonResponse({'status': 'charge_short'})

        if sort == 'free':
            post = FreeBoard.objects.get(id=int(object_value))
            # 중복되는 부분 아래 쪽에 빼놓고 함수 만듬
            result = input_charge(sort, post, charge_reason, content, request.user)
            return JsonResponse({'status': result})

        elif sort == 'comment':
            comment = Comment.objects.get(id=int(object_value))
            # 중복되는 부분 아래 쪽에 빼놓고 함수 만듬
            result = input_charge(sort, comment, charge_reason, content, request.user)
            return JsonResponse({'status': result})

        elif sort == 'message':
            message = Message.objects.get(id=int(object_value))
            # 중복되는 부분 아래 쪽에 빼놓고 함수 만듬
            result = input_charge(sort, message, charge_reason, content, request.user)
            return JsonResponse({'status': result})

        elif sort == 'etc':
            user = MyUser.objects.get(id=int(object_value))
            if request.user == user:
                return JsonResponse({'status': 'charge_same'})
            elif user.is_red:
                return JsonResponse({'status': 'charge_red'})
            else:
                # 중복되는 부분 아래 쪽에 빼놓고 함수 만듬
                result = input_charge(sort, user, charge_reason, content, request.user)
                return JsonResponse({'status': result})


# 반복되는 신고 코딩
def input_charge(sort, contents, charge_reason, content, user):
    ct = ContentType.objects.get_for_model(contents)

    charges = Charge.objects.filter(sort=sort, content_type=ct, object_id=contents.id)
    if charges:
        if charges.filter(charge_from=user, result_now='no'):
            return 'charge_already'
        elif charges.filter(result_now='no'):
            charge_num = charges.filter(result_now='no')
            if len(charge_num) == 1:
                charge_num[0].is_charge = True
                charge_num[0].save(update_fields=['is_charge'])
                Charge.objects.create(
                    sort=sort, content_type=ct, object_id=contents.id, charge_reason=charge_reason,
                    content=content, charge_from=user, charge=charge_num[0]
                )
                return 'charge_success'
            else:
                Charge.objects.create(
                    sort=sort, content_type=ct, object_id=contents.id, charge_reason=charge_reason,
                    content=content, charge_from=user, charge=charge_num.get(is_charge=True)
                )
                return 'charge_success'
        elif charges.filter(result_now='yes'):
            if sort == 'etc':
                Charge.objects.create(
                    sort=sort, content_type=ct, object_id=contents.id, charge_reason=charge_reason,
                    content=content, charge_from=user
                )
                return 'charge_success'
            else:
                return 'charge_already_done'
    else:
        Charge.objects.create(
            sort=sort, content_type=ct, object_id=contents.id, charge_reason=charge_reason,
            content=content, charge_from=user
        )
        return 'charge_success'


# pointshop의 tag 를 입력하는 부분 (추후 공부 해서 tag를 admin에서 입력할 수 있게끔 하여야 함-taggit)
def input_pointshop_tags(request, id=None, slug=None):
    products = Product.objects.all()
    if request.method == 'POST':
        product = Product.objects.get(id=id, slug=slug)
        product_tags = product.tags.all()

        # 태그 함수 (object의 tag들, object, 요청한 유저, sort 종류, raw_data(없으면 빈 list)- queryset 도 순수 list 로 변환해주어야 함)
        product_tags = [product.tag.name for product in product_tags]
        tags = request.POST.get('tags', None)
        tag(tags, product, request.user, 'point', product_tags)
        return HttpResponseRedirect(reverse('administrator:input_pointshop_tags'))

    return render(request, 'admin/sub_main/input_pointshop_tags.jinja', {'products': products})


# 연습
def chat(request):
    if request.method == 'POST':
        message = request.POST.get('val', None)
        print(message)
        if message:
            return JsonResponse({'photo':request.user.photo.url, 'user':request.user.nickname, 'result': message})
        else:
            pass
    forms  = ChatForm()
    return render(request, 'admin/sub_main/chat.jinja', {'forms': forms})
