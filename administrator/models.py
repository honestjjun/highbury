from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.conf import settings
from django.utils import timezone

from board_free.models import FreeBoard
from message.models import Message
from tag.models import Comment

SORT_CHOICES = (
    ('free', '게시글'),
    ('comment', '댓글'),
    ('message', '쪽지'),
    ('etc', '기타')
)

REPORT_CHOICES = (
    ('0', '욕설, 비방, 반말'),
    ('1', '지역 비하 발언'),
    ('2', '일베'),
    ('9', '기타'),
)

CHARGE_CHOICES = (
    ('0', '욕설, 비방, 반말'),
    ('1', '지역 비하 발언'),
    ('2', '일베'),
    ('9', '기타'),
)

RESULT_NOW_CHOICES = (
    ('yes', '완료'),
    ('no', '대기'),
)

RESULT_CHOICES = (
    ('yellow', '경고(삭제)'),
    ('delete', '삭제'),
    ('maintain', '유지'),
)


class Charge(models.Model):
    sort = models.CharField(max_length=10, choices=SORT_CHOICES)
    charge = models.ForeignKey('self', related_name='charge_set', blank=True, null=True) # 중복 신고 하게 될 경우 생성
    is_charge = models.BooleanField(default=False) # 중복 신고 여부

    charge_reason = models.CharField(max_length=20, choices=CHARGE_CHOICES)
    content = models.TextField(blank=True, null=True)
    charge_from = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='charge_from_user')
    charge_date = models.DateTimeField(auto_now_add=True)

    result_now = models.CharField(max_length=10, choices=RESULT_NOW_CHOICES, default='no')
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, blank=True, null=True)
    result_date = models.DateTimeField(blank=True, null=True)
    result_who = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True, related_name='result_who_user')

    content_type = models.ForeignKey(ContentType, related_name='charge_content_type', on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return '{} charge {}'.format(self.charge_from, self.content_object)

    def set_sort(self):
        if self.sort == 'comment':
            if self.content_object.sort == 'point-re':
                return '포인트 리뷰'
        return self.get_sort_display()

    def set_charge_reason(self):
        return self.get_charge_reason_display()

    def set_result_now(self):
        return self.get_result_now_display()

    def set_result(self):
        return self.get_result_display()
