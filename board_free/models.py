from __future__ import unicode_literals

from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.utils.text import slugify
from django.utils import timezone

from data.models import PlayerSeason, Match
from tag.models import Tagging, Comment, Recommend, Action

REVIEW_CHOICES = (
    ('free', '자유'),
    ('before', '프리뷰'),
    ('after', '경기후'),
    ('player', '선수'),
)

POINT_CHOICES = [(i,i) for i in range(1, 11)]

AFTERREVIEW_CHOICES = (
    ('0', 'team'), ('1', 'player1'), ('2', 'player2'), ('3', 'player3'),
    ('4', 'player4'), ('5', 'player5'), ('6', 'player6'), ('7', 'player7'),
    ('8', 'player8'), ('9', 'player9'), ('10', 'player10'), ('11', 'player11'),
    ('12', 'player12'), ('13', 'player13'), ('14', 'player14'),
)

STRATEGY_CHOICES = (
    ('strategy_3-5-2', '3-5-2'),
    ('strategy_4-2-3-1', '4-2-3-1')
)

BEFOREREVIEW_CHOICES = (
    ('0', 'strategy'), ('1', 'player1'), ('2', 'player2'), ('3', 'player3'),
    ('4', 'player4'), ('5', 'player5'), ('6', 'player6'), ('7', 'player7'),
    ('8', 'player8'), ('9', 'player9'), ('10', 'player10'), ('11', 'player11')
)


class FreeBoardManager(models.Manager):
    def get_queryset(self):
        return super(FreeBoardManager, self).get_queryset().filter(is_superuser=False)


class FreeBoard(models.Model):
    sort = models.CharField(max_length=255, choices=REVIEW_CHOICES, default='free')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, allow_unicode=True, blank=True)
    body = models.TextField()
    user = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(blank=True, null=True)

    read = models.IntegerField(default=0, blank=True)
    is_active = models.BooleanField(default=True, blank=True)
    is_superuser = models.BooleanField(default=False, blank=True)

    player_review = models.ForeignKey(PlayerSeason, related_name='footballboard_player_review', blank=True, null=True)
    after_game_review = models.ForeignKey(Match, related_name='footballboard_after_game', blank=True, null=True)
    before_game_review = models.ForeignKey(Match, related_name='footballboard_before_game', blank=True, null=True)

    tags = GenericRelation(Tagging)
    comments = GenericRelation(Comment)
    recommends = GenericRelation(Recommend)
    actions = GenericRelation(Action)

    objects = models.Manager()
    active = FreeBoardManager()

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return self.title

    def set_sort(self):
        return self.get_sort_display()

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super(FreeBoard, self).save(*args, **kwargs)


class AfterReview(models.Model):
    freeboard = models.ForeignKey(FreeBoard, blank=True, null=True, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name='afterreview_match')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='afterreview_user', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    sort = models.CharField(max_length=15, choices=AFTERREVIEW_CHOICES)
    player = models.ForeignKey(PlayerSeason, related_name='afterreview_player', blank=True, null=True)
    point = models.PositiveIntegerField(default=1, blank=True, null=True)
    review = models.TextField(blank=True, null=True)

    is_simple = models.BooleanField(default=True) # 간단 평점을 남겼는지에 대한 여부

    def __str__(self):
        return '{} review {}'.format(self.user, self.match)

    class Meta:
        ordering = ('-id', '-match', 'player')


class BeforeReview(models.Model):
    freeboard = models.ForeignKey(FreeBoard, on_delete=models.CASCADE)
    match = models.ForeignKey(Match, related_name='beforereview_match')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='beforereview_user', on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)

    sort = models.CharField(max_length=15, choices=BEFOREREVIEW_CHOICES)
    strategy = models.CharField(max_length=15, choices=STRATEGY_CHOICES, null=True, blank=True)
    player = models.ForeignKey(PlayerSeason, related_name='beforereview_player', null=True, blank=True)

    def __str__(self):
        return '{} preview {}'.format(self.user, self.match)

    class Meta:
        ordering = ('-match', 'player', '-id')
