from django.conf import settings
from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

from django.utils.text import slugify
from tag.models import Tagging, Comment, Recommend


PLAYER_CHOICES = (
    ('player1', 'player1'),
    ('player2', 'player2'),
    ('player3', 'player3'),
    ('player4', 'player4'),
    ('player5', 'player5'),
    ('player6', 'player6'),
    ('player7', 'player7'),
    ('player8', 'player8'),
    ('player9', 'player9'),
    ('player10', 'player10'),
    ('player11', 'player11'),
)


STRATEGY_CHOICES = (
    ('strategy_4-2-3-1', 'strategy_4-2-3-1'),
    ('strategy_3-5-2', 'strategy_3-5-2'),
)


SATISFACTION_CHOICES = [(str(i),str(i)) for i in range(1,6)]


class Category(models.Model): # 카테고리
    name = models.CharField(max_length=255) # 상위 카테고리(ForeignKey)
    created = models.DateTimeField(default=timezone.now, db_index=True) # 카테고리 만들어진 날짜
    is_active = models.BooleanField(default=True) # 노출 여부

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('created', '-id')


class ProductCategory(models.Model): # 상품이 세로로 진열될 공간
    name = models.CharField(max_length=255) # 상품 카테고리 (세로 품목)
    category = models.ForeignKey(Category, related_name='sub_category') # 연관된 카테고리
    content = models.TextField(blank=True, null=True) # 상품 카테고리 내용
    created = models.DateTimeField(default=timezone.now, db_index=True) # 만들어진 시간
    is_active = models.BooleanField(default=True) # 노출 여부

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('created', '-id')


class Product(models.Model): # 상품 (만일 일반 상품으로 가게 될 경우 몇개 추가만 해주면 됨)
    title = models.CharField(max_length=100, null=True) # 상품 이름
    slug = models.SlugField(max_length=255, null=True, blank=True, allow_unicode=True) # slug

    main_category = models.ForeignKey(Category, null=True)
    category = models.ForeignKey(ProductCategory, related_name="product", db_index=True)  # 상품이 진열될 세로 위치
    point = models.IntegerField(default=0) # 상품에 책정된 포인트
    width = models.CharField(max_length=100, null=True) # 상품이 진열될 가로 위치
    created = models.DateTimeField(default=timezone.now) # 상품이 생성된 시간

    information = models.TextField() # 상품 정보
    image = models.ImageField(upload_to='product_image/') # 상품의 이미지
    buyer = models.ManyToManyField(settings.AUTH_USER_MODEL, blank=True) # 상품을 산 사람들 명단
    is_active = models.BooleanField(default=True) # 상품의 노출 상황

    tags = GenericRelation(Tagging)
    comments = GenericRelation(Comment)
    recommends = GenericRelation(Recommend)

    def __str__(self):
        return '{}. price {}point'.format(self.title, self.point)

    class Meta:
        ordering = ('-category', 'width')
        index_together = ('category', 'width')
        
    def save(self, *args, **kwargs):
        if not self.slug:
            make_slug = '{}-{}'.format(self.title, self.category)
            self.slug = slugify(make_slug, allow_unicode=True)
        super(Product, self).save(*args, **kwargs)
            

class DiscountManager(models.Manager):
    def get_queryset(self):
        return Discount.objects.filter(is_active=True, start_date__lt=timezone.now(), end_date__gt=timezone.now())

class Discount(models.Model): # 할인 행사
    name = models.CharField(max_length=150) # 할인 이름
    created = models.DateTimeField(default=timezone.now, db_index=True) # 할인 이름 생성 시간
    start_date = models.DateTimeField() # 할인 시작 시간
    end_date = models.DateTimeField() # 할인 마지막 시간
    discount_point = models.IntegerField(default=0) # 할인 확률
    is_active = models.BooleanField(default=True) # 할인 행사 노출 여부

    objects = models.Manager()
    active = DiscountManager()

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created', '-id')


class UsePoint(models.Model):
    category = models.ForeignKey(Category) # 상위 카테고리
    product_category = models.ForeignKey(ProductCategory, null=True) # 하위 카테고리
    product = models.ForeignKey(Product) # 상품
    
    order_number = models.CharField(max_length=200, null=True, blank=True)
    buy_date = models.DateTimeField(default=timezone.now, db_index=True) # 포인트로 상품을 산 날짜
    user = models.ForeignKey(settings.AUTH_USER_MODEL) # 상품을 산 유저
    use_point = models.IntegerField(default=0) # 사용된 포인트

    def __str__(self):
        return '{} buy {}, spent {}point'.format(self.user, self.product, self.use_point)

    class Meta:
        ordering = ('buy_date', 'id')

    def save(self, *args, **kwargs):
        super(UsePoint, self).save(*args, **kwargs)
        if not self.order_number:
            self.order_number = 'point-order-' + str(1000000 + int(self.id))
            super(UsePoint, self).save(*args, **kwargs)


# 아직 미 구현
class FantasyLeague(models.Model):
    name = models.CharField(max_length=200) # 판타지 리그 이름
    user = models.ForeignKey(settings.AUTH_USER_MODEL) # 판타지 리그 유저
    created = models.DateTimeField(default=timezone.now) # 판타지 리그 만든 날
    position = models.CharField(max_length=10, choices=PLAYER_CHOICES) # 해당 선수의 포지션
    strategy = models.CharField(max_length=15, choices=STRATEGY_CHOICES, default='strategy_4-2-3-1') # 판타지 리그의 전술
    player = models.ForeignKey(Product) # 해당 선수

    def __str__(self):
        return '{} make {} fantasy league'.format(self.user, self.name)

    class Meta:
        ordering = ('user', 'name', 'position')
        index_together = ('user', 'name', 'position')
