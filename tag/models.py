from django.db import models

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.text import slugify


SELECT_CHOICES = (
    ('free', 'freeboard'),
    ('point', 'pointshop'),
)

ACTION_CHOICES = (
    ('post', '댓글을'),
    ('comment', '댓글을')
)

COMMENT_CHOICES = (
    ('free-co', 'freeboard comment'),
    ('point-co', 'pointshop comment'),
    ('point-re', 'pointshop review'),
)

SATISFACTION_CHOICES = [(str(i),str(i)) for i in range(1,6)]


class Tag(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(allow_unicode=True, blank=True, null=True)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super(Tag, self).save(*args, **kwargs)

# tagging이 전부 삭제 되어 tag에 남아있는 녀석이 없다면 tag를 나중에 정리해줄 것들이 필요하다.
class Tagging(models.Model):
    tag = models.ForeignKey(Tag)
    user = models.ForeignKey(settings.AUTH_USER_MODEL) # tag 를 남긴 유저
    sort = models.CharField(max_length=10, choices=SELECT_CHOICES)
    created = models.DateTimeField(auto_now_add=True) # tag 가 작성된 날짜

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return '{} tagged by {}'.format(self.user, self.tag)


class Comment(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    sort = models.CharField(max_length=10, choices=COMMENT_CHOICES)
    content = models.TextField(null=True)
    created = models.DateTimeField(auto_now_add=True)

    satisfaction = models.CharField(max_length=2, choices=SATISFACTION_CHOICES, blank=True, null=True)
    comment = models.ForeignKey('self', related_name='comment_set', null=True, blank=True)
    commenting_user = models.CharField(max_length=100, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    id_delete = models.BooleanField(default=False) # 댓글 밑에 대댓글이 달리게 되면 사용자가 댓글을 삭제해도 완전 삭제가 되는 것이 아니게 됨

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return '{}'.format(self.content)


class Recommend(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='user_recommend')
    created = models.DateTimeField(auto_now_add=True, db_index=True)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    class Meta:
        ordering=('-created',)

    def __str__(self):
        return '{} recommend {}'.format(self.user, self.content_type)


# 아직 미 구현
class Action(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='action_from')
    sort = models.CharField(max_length=10, choices=ACTION_CHOICES)
    created = models.DateTimeField(auto_now_add=True)
    to_user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='action_to', null=True)

    comment = models.ForeignKey(Comment, blank=True, null=True)
    is_confirm = models.BooleanField(default=False)

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey()

    def __str__(self):
        return '{} {} to {}'.format(self.user, self.sort, self.content_type)

    def set_sort(self):
        return self.get_sort_display()
