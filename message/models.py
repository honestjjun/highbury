from django.conf import settings
from django.db import models
from django.utils import timezone


class Message(models.Model):
    send_num = models.IntegerField(default=0)
    take_num = models.IntegerField(default=0)
    send_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='send_message', blank=True)
    take_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='take_message')
    message = models.TextField(max_length=500)
    created = models.DateTimeField(default=timezone.now)
    is_confirm = models.BooleanField(default=False) # 수신 확인
    take_delete = models.BooleanField(default=False) # 받은 사람이 삭제 하였을 경우
    send_delete = models.BooleanField(default=False) # 보낸 사람이 삭제 하였을 경우
    is_active = models.BooleanField(default=True) # 관리자가 삭제 하였을 경우
    class Meta:
        ordering = ('-created', '-id')

    def __str__(self):
        return '{} send {}'.format(self.send_user, self.take_user)

    def save(self, *args, **kwargs):
        sends = Message.objects.filter(send_user=self.send_user).order_by('-send_num')
        takes = Message.objects.filter(take_user=self.take_user).order_by('-take_num')
        if not sends:
            self.send_num = 1
        else:
            for send in sends:
                self.send_num = send.send_num + 1
                break

        if not takes:
            self.take_num = 1
        else:
            for take in takes:
                self.take_num = take.take_num + 1
                break
        super(Message, self).save(*args, **kwargs)
