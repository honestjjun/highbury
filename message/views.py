from django.http.response import HttpResponseRedirect, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.urls.base import reverse
from django.contrib import messages

from account.models import MyUser
from lib.confirm_text import no_space_text
from lib.paginator import paginator

from .models import Message
from .forms import MessageForm


def take_message_box(request):
    my_messages = Message.objects.filter(take_user=request.user, take_delete=False).order_by('-created')
    message_count = len(my_messages)
    confirm_count = Message.objects.filter(take_user=request.user, take_delete=False, is_confirm=False).count()

    # paging 함수 (게시물 분리, 상품, request.GET, 'page', 처음 보여질 페이지, 한페이지에 보여질 수, 보여질 토탈 페이징)
    paging = paginator(my_messages, request.GET, 'page', 'first', 20, 10)

    return render(request, 'main/message/take_message_box.jinja', {'select':'take_message_box', 'confirm_count': confirm_count,
                                                              'paging': paging, 'message_count': message_count})


def send_message(request, reply=None):
    if reply == 'true':
        if request.method == 'POST':
            forms = MessageForm(request.POST)
            if forms.is_valid():
                forms.save()
                return HttpResponseRedirect(reverse('message:send_message_box'))
    else:
        if request.method == 'POST':
            forms = MessageForm(request.POST)
            if forms.is_valid():
                user = forms.save(commit=False)
                user.send_user = request.user
                user.save()
                return HttpResponseRedirect(reverse('message:send_message_box'))
        else:
            forms = MessageForm()
        return render(request, 'main/message/send_message.jinja', {'select':'send_message', 'forms': forms})


def detail(request, message_id, value):
    message_detail = get_object_or_404(Message, id=message_id)

    if value == 'take':
        if message_detail.is_confirm == False:
            message_detail.is_confirm = True
            message_detail.save()
        return render(request, 'main/message/detail.jinja',
                      {'select': 'take_message_box', 'message_detail': message_detail, 'value': value})
    return render(request, 'main/message/detail.jinja',
                  {'select': 'send_message_box', 'message_detail': message_detail, 'value': value})


def send_message_box(request):
    my_messages = Message.objects.filter(send_user=request.user, send_delete=False).order_by('-created')
    message_count = len(my_messages)
    confirm_count = Message.objects.filter(send_user=request.user, send_delete=False, is_confirm=False).count()

    # paging 함수 (게시물 분리, 상품, request.GET, 'page', 처음 보여질 페이지, 한페이지에 보여질 수, 보여질 토탈 페이징)
    paging = paginator(my_messages, request.GET, 'page', 'first', 20, 10)

    return render(request, 'main/message/send_message_box.jinja', {'select':'send_message_box', 'confirm_count': confirm_count,
                                                              'paging': paging, 'message_count': message_count})


def message_ajax(request):
    if request.method == 'POST':
        string = request.POST.get('message')
        if no_space_text(string) == 0:
            return JsonResponse({'status': 'message_empty'})
        elif no_space_text(string) < 10:
            return JsonResponse({'status': 'message_short'})
        else:
            take_user = MyUser.objects.get(nickname=request.POST.get('take_user'))
            Message.objects.create(
                send_user=request.user, take_user=take_user, message=request.POST.get('message')
            )
            return JsonResponse({'status': 'message_success'})


def same_nickname(request):
    if request.method == 'POST':
        value = request.POST.get('id', None)
        if value:
            try:
                MyUser.objects.get(nickname=value)
            except MyUser.DoesNotExist:
                return JsonResponse({'result':'false'})
            else:
                return JsonResponse({'result':'true'})
        else:
            return JsonResponse({'result':'none'})


def delete_message(request, id, which):
    try:
        message = Message.objects.get(id=id)
    except Message.DoesNotExist:
        messages.error(request, '메세지가 존재하지 않습니다.')
        if which == 'send':
            return HttpResponseRedirect(reverse('message:send_message_box'))
        else:
            return HttpResponseRedirect(reverse('message:take_message_box'))
    else:
        if which == 'send':
            message.send_delete = True
        elif which == 'take':
            message.take_delete = True
        message.save()
        if message.take_delete == True and message.send_delete == True:
            message.delete()
        return HttpResponseRedirect(reverse('message:send_message_box'))

