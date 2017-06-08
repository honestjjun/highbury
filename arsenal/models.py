from PIL import Image
from django.db import models
from django.utils import timezone
from django.conf import settings

from data.models import Match


VOTE_CHOICES = (
    ('select', 'select'),
    ('write', 'write'),
    ('picture', 'picture'),
)

VALUE_CHOICES = (
    ('letter', 'letter'),
    ('picture', 'picture')
)


class EventVote(models.Model):
    event_round = models.IntegerField(default=1)
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    match = models.ForeignKey(Match, related_name='userpoint_match')
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    vote_date = models.DateTimeField(default=timezone.now)
    is_result = models.BooleanField(default=False)

    class Meta:
        ordering = ('match', 'vote_date')

    def __str__(self):
        return '{}'.format(self.match)
    
    def save(self, *args, **kwargs):
        try:
            recent_match = EventVote.objects.filter(match__match_date__lt=timezone.now())[0]
        except EventVote.DoesNotExist:
            super(EventVote, self).save(*args, **kwargs)
        else:
            self.event_round = recent_match.event_round + 1
            super(EventVote, self).save(*args, **kwargs)


class VoteQuestionActive(models.Manager):
    def get_queryset(self):
        return super(VoteQuestionActive, self).get_queryset().filter(is_active=True, start_vote__lt=timezone.now(), end_vote__gt=timezone.now()).order_by('id',)


class VoteQuestionDead(models.Manager):
    def get_queryset(self):
        return super(VoteQuestionDead, self).get_queryset().filter(is_active=True, end_vote__lt=timezone.now())


class VoteQuestion(models.Model):
    question = models.CharField(max_length=255) # 질문 내용
    created = models.DateTimeField(default=timezone.now) # 설문지 만든날
    start_vote = models.DateTimeField() # 설문지 시작하는 날
    end_vote = models.DateTimeField() #설문지 끝나는 날
    choice_num = models.IntegerField(default=1) # 최대 선택해야 하는 개수 정의
    is_active = models.BooleanField(default=True) # 보여줄지 말지에 대한 정의
    is_sort = models.CharField(max_length=50, choices=VOTE_CHOICES, default='select') # 설문지의 종류를 정의

    objects = models.Manager()
    active = VoteQuestionActive() # 오늘 날짜 기준으로 활동 가능한 설문지 검색
    dead = VoteQuestionDead() # 오늘 날짜 기준으로 죽은 설문지 검색

    class Meta:
        ordering = ('-id', '-created')

    def __str__(self):
        return self.question


class VoteAnswer(models.Model):
    question = models.ForeignKey(VoteQuestion, related_name='vote_answer_question')
    answer = models.CharField(max_length=255, blank=True, null=True)
    pic_answer = models.ImageField(upload_to='survey', blank=True, null=True)
    is_transform = models.CharField(max_length=10, choices=VALUE_CHOICES, default='letter')
    is_show = models.BooleanField(default=True) # 이거 없애도 될거 같다. 왜 만든건지 모르겠음.
    vote = models.IntegerField(default=0)

    def __str__(self):
        return self.answer

    def save(self, *args, **kwargs):
        if self.is_transform == 'letter':
            super(VoteAnswer, self).save(*args, **kwargs)
        elif self.is_transform == 'picture':
            try:
                VoteAnswer.objects.get(id=self.id)
            except VoteAnswer.DoesNotExist:
                self.pic_answer.name = '{}/{}_{}.jpg'.format(timezone.now().strftime('%Y-%m-%d'), self.question, self.answer)
                super(VoteAnswer, self).save(*args, **kwargs)
    
                image = Image.open(self.pic_answer.path)
                image = image.resize((100,100), Image.ANTIALIAS)
                image.save(self.pic_answer.path, format='JPEG', quality=70)
                super(VoteAnswer, self).save(*args, **kwargs)
            else:
                super(VoteAnswer, self).save(*args, **kwargs)


class VoteUser(models.Model):
    question = models.ForeignKey(VoteQuestion, related_name='vote_user_question')
    select_answer = models.ManyToManyField(VoteAnswer, related_name='vote_user_answer', blank=True)
    write_answer = models.TextField(null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='vote_user_author')
    created = models.DateTimeField(default=timezone.now)
    is_sort = models.CharField(max_length=50, choices=VOTE_CHOICES, default='select')

    class Meta:
        ordering = ('-created',)

    def __str__(self):
        return str(self.question)
