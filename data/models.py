from __future__ import unicode_literals

from PIL import Image
from django.conf import settings
from django.db import models
from django.utils import timezone


# 리그 종류
LEAGUE_CHOICES = (
    ('england', '프리미어리그'),
    ('spain', '라리가리그'),
    ('france', '리그앙'),
    ('german', '분데스리가'),
)

# 시즌 종류
SEASON_CHOICES = (
    ('2017', '2017'),
    ('2018', '2018'),
)

# 태어나 나라 종류
NATION_CHOICES = (
    ('germany', 'German'),
    ('france', 'France'),
    ('spain', 'Spain'),
    ('england', 'England'),
    ('czech', 'Czech'),
)

# 포지션 종류
POSITION_CHOICES = (
    ('FW', 'FW'),
    ('MF', 'MF'),
    ('DF', 'DF'),
    ('GK', 'GK'),
)

# 백넘버 종류
BACKNUMBER_CHOICES = [(i,i) for i in range(1,100)]

# 라운드 종류
ROUND_CHOICES = (
    ('1', '1 Round'), ('2', '2 Round'), ('3', '3 Round'), ('4', '4 Round'), ('5', '5 Round'),
    ('6', '6 Round'), ('7', '7 Round'), ('8', '8 Round'), ('9', '9 Round'), ('1', '10 Round'),
    ('11', '11 Round'), ('12', '12 Round'), ('13', '13 Round'), ('14', '14 Round'), ('15', '15 Round'),
    ('16', '16 Round'), ('17', '17 Round'), ('18', '18 Round'), ('19', '19 Round'), ('20', '20 Round'),
    ('21', '21 Round'), ('22', '22 Round'), ('23', '23 Round'), ('24', '24 Round'), ('25', '25 Round'),
    ('26', '26 Round'), ('27', '27 Round'), ('28', '28 Round'), ('29', '29 Round'), ('30', '30 Round'),
    ('31', '31 Round'), ('32', '32 Round'), ('33', '33 Round'), ('34', '34 Round'), ('35', '35 Round'),
    ('36', '36 Round'), ('37', '37 Round'), ('38', '38 Round'),
    ('c_16', '챔스 16강'),
)

# 경기 결과
RESULT_CHOICES = (
    ('win', 'WIN'),
    ('draw', 'DRAW'),
    ('lose', 'LOSE')
)

STRATEGY_CHOICES = (
    ('4-2-3-1', 'strategy_4-2-3-1'),
    ('3-5-2', 'strategy_3-5-2'),
)

# point 선택
POINT_CHOICES = (
    ('login', 'login'),
    ('review', 'review'),
    ('free', 'free'),
    ('comment', 'comment'),
    ('vote', 'vote'),
    ('correct_vote', 'correct_vote'),
    ('easy_point', 'easy_point'),
    ('spend', 'spend')
)



# 가장 기본 팀 정보
class Team(models.Model):
    name = models.CharField(max_length=200)
    photo = models.ImageField(upload_to='data/football/team')
    stadium = models.CharField(max_length=200)
    league = models.CharField(max_length=200, choices=LEAGUE_CHOICES, default='england')

    class Meta:
        ordering = ('-name',)

    def __str__(self):
        return '{}'.format(self.name)

    def save(self, *args, **kwargs):
        super(Team, self).save(*args, **kwargs)
        if self.photo.width > 100:
            image = Image.open(self.photo.path)
            image = image.resize((100, 100), Image.ANTIALIAS)
            image.save(self.photo.path, format='JPEG', quality=70)


# 시즌과 리그 별로 나누고 순위가 매겨짐
class TeamSeason(models.Model):
    season = models.CharField(max_length=100, choices=SEASON_CHOICES, default='2017')
    league = models.CharField(max_length=200, choices=LEAGUE_CHOICES, default='england')
    team = models.ForeignKey(Team, related_name='team_season_information')
    ranking = models.IntegerField(default=1)
    win = models.PositiveIntegerField(default=0)
    draw = models.PositiveIntegerField(default=0)
    lose = models.PositiveIntegerField(default=0)
    benefit = models.IntegerField(default=0)
    goal_benefit = models.IntegerField(default=0)

    class Meta:
        ordering = ('league', 'season', 'ranking')

    def __str__(self):
        return '{}'.format(self.team)


# 가장 기본 선수 정보
class Player(models.Model):
    name = models.CharField(max_length=255)
    photo = models.ImageField(upload_to='data/football/player')
    review_photo = models.ImageField(upload_to='data/football/player/review_image', null=True)
    birth = models.DateField()
    nation = models.CharField(max_length=200, choices=NATION_CHOICES, blank=True, null=True)

    class Meta:
        ordering = ('name',)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        super(Player, self).save(*args, **kwargs)
        if self.photo.width > 100:
            image = Image.open(self.photo.path)
            image = image.resize((100, 100), Image.ANTIALIAS)
            image.save(self.photo.path, format='JPEG', quality=70)


# 선수 manager
class PlayerSeasonManager(models.Manager):
    def get_queryset(self):
        return super(PlayerSeasonManager, self).get_queryset().filter(season='2017', league='england')


# 시즌과 리그 별로 나눔
class PlayerSeason(models.Model):
    season = models.CharField(max_length=100, choices=SEASON_CHOICES, default='2017')
    league = models.CharField(max_length=100, choices=LEAGUE_CHOICES, default='england')
    name = models.ForeignKey(Player, related_name='player_information')
    team = models.ForeignKey(Team, related_name='player_season_information')
    back_number = models.IntegerField(choices=BACKNUMBER_CHOICES, default=1)
    position_number = models.IntegerField(default=1)
    position = models.CharField(max_length=10, choices=POSITION_CHOICES, default='GK')
    goal = models.PositiveIntegerField(default=0)
    assist = models.PositiveIntegerField(default=0)

    game = models.PositiveIntegerField(default=0)
    point = models.PositiveIntegerField(default=0)
    ratio = models.CharField(max_length=10, blank=True, null=True)

    objects = models.Manager()
    ing = PlayerSeasonManager()

    class Meta:
        ordering = ('position_number', 'position')

    def __str__(self):
        return '{} {}({}) in {}'.format(self.position, self.name, self.back_number, self.team)

    def save(self, *args, **kwargs):
        super(PlayerSeason, self).save(*args, **kwargs)
        if self.point == 0 or self.game == 0:
            pass
        else:
            self.ratio = str(round(self.point/self.game, 1))
            super(PlayerSeason, self).save(*args, **kwargs)


class MatchBeforeManager(models.Manager):
    def get_queryset(self):
        return super(MatchBeforeManager, self).get_queryset().filter(match_date__gt=timezone.now(), result__isnull=True).order_by('match_date')

class MatchAfterManager(models.Manager):
    def get_queryset(self):
        return super(MatchAfterManager, self).get_queryset().filter(match_date__lt=timezone.now(), result__in=['win','lose','draw']).order_by('-match_date')

# 매치 경기가 나옴
class Match(models.Model):
    round = models.CharField(max_length=100, choices=ROUND_CHOICES, default='1round')
    league = models.CharField(max_length=100, choices=LEAGUE_CHOICES, default='england')
    home_team = models.ForeignKey(TeamSeason, related_name='match_home_team')
    away_team = models.ForeignKey(TeamSeason, related_name='match_away_team')
    match_date = models.DateTimeField()
    result = models.CharField(max_length=10, choices=RESULT_CHOICES, blank=True, null=True)
    home_score = models.PositiveIntegerField(default=0)
    away_score = models.PositiveIntegerField(default=0)
    strategy = models.CharField(max_length=100, choices=STRATEGY_CHOICES, default='strategy_4-2-3-1', null=True)

    player1 = models.ForeignKey(PlayerSeason, related_name='match_player1', blank=True, null=True)
    player2 = models.ForeignKey(PlayerSeason, related_name='match_player2', blank=True, null=True)
    player3 = models.ForeignKey(PlayerSeason, related_name='match_player3', blank=True, null=True)
    player4 = models.ForeignKey(PlayerSeason, related_name='match_player4', blank=True, null=True)
    player5 = models.ForeignKey(PlayerSeason, related_name='match_player5', blank=True, null=True)
    player6 = models.ForeignKey(PlayerSeason, related_name='match_player6', blank=True, null=True)
    player7 = models.ForeignKey(PlayerSeason, related_name='match_player7', blank=True, null=True)
    player8 = models.ForeignKey(PlayerSeason, related_name='match_player8', blank=True, null=True)
    player9 = models.ForeignKey(PlayerSeason, related_name='match_player9', blank=True, null=True)
    player10 = models.ForeignKey(PlayerSeason, related_name='match_player10', blank=True, null=True)
    player11 = models.ForeignKey(PlayerSeason, related_name='match_player11', blank=True, null=True)

    player12 = models.ForeignKey(PlayerSeason, related_name='match_subplayer1', blank=True, null=True)
    player13 = models.ForeignKey(PlayerSeason, related_name='match_subplayer2', blank=True, null=True)
    player14 = models.ForeignKey(PlayerSeason, related_name='match_subplayer3', blank=True, null=True)

    objects = models.Manager()
    recent = MatchAfterManager()
    next = MatchBeforeManager()

    class Meta:
        ordering = ('-match_date',)

    def __str__(self):
        return '{}:{} vs {}'.format(self.round, self.home_team, self.away_team)

    def set_round(self):
        return self.get_round_display()

    def set_strategy(self):
        return self.get_strategy_display()


# 유저의 경험치
class UserPoint(models.Model):
    sort = models.CharField(max_length=20, choices=POINT_CHOICES, null=True)

    point = models.PositiveIntegerField(default=0, blank=True) # 남은 포인트 양
    total_experience = models.PositiveIntegerField(default=0, blank=True)  # 총 경험치 (포인트와 틀린 것은 포인트는 차감이 되고 total 은 차감되지 않음)
    point_name = models.CharField(max_length=20, blank=True, null=True) # 가장 마지막에 로그인한 날짜

    daily_check = models.IntegerField(default=0, blank=True, null=True) # 로그인으로 하루에 획득 가능한 포인트
    daily_review = models.IntegerField(default=0, blank=True, null=True) # 리뷰 작성으로 하루에 획득 가능한 포인트
    daily_free = models.IntegerField(default=0, blank=True, null=True) # 자유글 작성으로 하루에 획득 가능한 포인트
    daily_comment = models.IntegerField(default=0, blank=True, null=True) # 댓글 작성으로 하루에 획득 가능한 포인트

    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name='point') # 연관된 유저
    level = models.PositiveIntegerField(default=1, blank=True) # 현재 유저의 레벨
    value = models.IntegerField(default=0) # 올라가거나 떨어질 포인트 점수
    recent_update = models.DateTimeField(default=timezone.now) # 가장 마지막으로 업데이트 된 날짜
    max_experience = models.PositiveIntegerField(default=100, blank=True) # 해당 레벨의 최대 경험치
    experience = models.IntegerField(default=100, blank=True) # 해당 레벨의 남은 경험치

    class Meta:
        ordering = ('-point', 'user')

    def __str__(self):
        return '{}'.format(self.user.nickname)

    def save(self, *args, **kwargs):
        super(UserPoint, self).save(*args, **kwargs)
        time = timezone.now()
        today_name = time.strftime('%Y-%m-%d')

        # point name 이 다른 날이라면 오늘로 바꾸고 일 횟수도 초기화 시킨다.
        if self.point_name != today_name:
            self.point_name = today_name

            self.daily_check = settings.DAILY_LOGIN_NUM
            self.daily_review = settings.DAILY_REVIEW_NUM
            self.daily_free = settings.DAILY_BOARD_NUM
            self.daily_comment = settings.DAILY_COMMENT_NUM

        if self.sort == 'login':
            if self.daily_check == 0:
                self.value = 0
            else:
                self.daily_check -= 1
                self.value = self.value
        if self.sort == 'review':
            if self.daily_review == 0:
                self.value = 0
            else:
                self.daily_review -= 1
                self.value = self.value
        elif self.sort == 'free':
            if self.daily_free == 0:
                self.value = 0
            else:
                self.daily_free -= 1
                self.value = self.value
        elif self.sort == 'comment':
            if self.daily_comment == 0:
                self.value = 0
            else:
                self.daily_comment -= 1
                self.value = self.value
        elif self.sort == 'spend':
            self.point -= self.value
            super(UserPoint, self).save(*args, **kwargs)
        else:
            self.value = self.value

        if self.value != 0 and self.sort != 'spend':
            self.point += self.value
            self.total_experience += self.value
            self.experience -= self.value
            self.value = 0
            if self.experience < 0:
                self.level += 1
                self.max_experience = self.level * self.level * 100
                self.experience = self.max_experience+self.experience
            elif self.experience == 0:
                self.level += 1
                self.max_experience = self.level * self.level * 100
                self.experience = self.max_experience
            elif self.experience > self.max_experience:
                self.level -= 1
                self.experience = self.experience - self.max_experience
                self.max_experience = self.level * self.level * 100

            super(UserPoint, self).save(*args,**kwargs)
