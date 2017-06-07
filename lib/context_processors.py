from django.utils import timezone

from dateutil.relativedelta import relativedelta

from message.models import Message
from tag.models import Action


def message_count(request):
    if request.user.is_authenticated:
        messages_count = Message.objects.filter(take_user=request.user, take_delete=False, is_confirm=False).count()
    else:
        messages_count = False
    return {'messages_count': messages_count}


def notify_count(request):
    if request.user.is_authenticated:
        notify_count = Action.objects.filter(created__gte=timezone.now()-relativedelta(days=7), is_confirm=False, to_user=request.user).order_by('-created')[:10]
    else:
        notify_count = False
    return {'notify_count': notify_count}