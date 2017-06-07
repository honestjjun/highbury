from django.db import models
from django.utils import timezone
from django.conf import settings

from PIL import Image

import os


# save 하면서 그림의 이미지 사이징을 줄여 버린다.
def change_image_size(self, *args, **kwargs):
    if self.sort == 'main_advertise':
        self.banner.name = 'main_advertise_{}.jpg'.format(self.title)
        super(Advertise, self).save(*args, **kwargs)

        if self.banner.width > settings.MAIN_ADVERTISEMENTS[0] or self.banner.width < settings.MAIN_ADVERTISEMENTS[0] or self.banner.height > settings.MAIN_ADVERTISEMENTS[1] or self.banner.height < settings.MAIN_ADVERTISEMENTS[1]:
            image = Image.open(self.banner.path)
            image = image.resize(settings.MAIN_ADVERTISEMENTS, Image.ANTIALIAS)
            image.save(self.banner.path, format='JPEG', quality=70)

    elif self.sort == 'sub_top' or self.sort == 'profile_top':
        self.banner.name = '{}_{}.jpg'.format(self.sort, self.title)
        super(Advertise, self).save(*args, **kwargs)

        if self.banner.width > settings.SUB_TOP_ADVERTISEMENTS[0] or self.banner.width < settings.SUB_TOP_ADVERTISEMENTS[0] or self.banner.height > settings.SUB_TOP_ADVERTISEMENTS[1] or self.banner.height < settings.SUB_TOP_ADVERTISEMENTS[1]:
            image = Image.open(self.banner.path)
            image = image.resize(settings.SUB_TOP_ADVERTISEMENTS, Image.ANTIALIAS)
            image.save(self.banner.path, format='JPEG', quality=70)
    elif self.sort == 'community_right':
        self.banner.name = '{}_{}.jpg'.format(self.sort, self.title)
        super(Advertise, self).save(*args, **kwargs)

        if self.banner.width > settings.RIGHT_TOP_ADVERTISEMENTS[0] or self.banner.width < settings.RIGHT_TOP_ADVERTISEMENTS[0] or self.banner.height > settings.RIGHT_TOP_ADVERTISEMENTS[1] or self.banner.height < settings.RIGHT_TOP_ADVERTISEMENTS[1]:
            image = Image.open(self.banner.path)
            image = image.resize(settings.RIGHT_TOP_ADVERTISEMENTS, Image.ANTIALIAS)
            image.save(self.banner.path, format='JPEG', quality=70)


class AdvertiseManage(models.Manager):
    def get_queryset(self):
        return super(AdvertiseManage, self).get_queryset().filter(is_active=True, event_start__lt=timezone.now(), event_end__gt=timezone.now())


class Advertise(models.Model):
    SORT_CHOICES = (
        ('main_advertise', 'main_advertise'),
        ('sub_top', 'sub_top'),
        ('profile_top', 'profile_top'),
        ('community_right', 'community_right')
    )
    num = models.PositiveIntegerField(default=0, null=True)
    title = models.CharField(max_length=255)
    event_start = models.DateTimeField()
    event_end = models.DateTimeField()
    created = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=False)
    link = models.CharField(max_length=255, blank=True, null=True)
    banner = models.ImageField(upload_to='banner')
    banner_md = models.ImageField(upload_to='banner', blank=True, null=True)
    banner_sm = models.ImageField(upload_to='banner', blank=True, null=True)
    sort = models.CharField(max_length=255, choices=SORT_CHOICES)

    objects = models.Manager()
    active = AdvertiseManage()

    class Meta:
        ordering = ('-num', 'banner')

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # 존재하는 아이디일 경우 (update)
        if self.id:
            exist_advertise = Advertise.objects.get(id=self.id)

            # 기존 배너의 path 랑 이름이 다르다면 기존 그림을 지우고 새로운 것을 저장한다.
            if exist_advertise.banner.path != self.banner.path:
                os.remove(exist_advertise.banner.path)
                change_image_size(self, *args, **kwargs)

            # 기존 title 이랑 다르다면 그림의 title 명을 바꿔버린다.
            elif exist_advertise.title != self.title or exist_advertise.sort != self.sort:
                new_name = 'banner/{}_{}.jpg'.format(self.sort, self.title)
                os.rename(exist_advertise.banner.path, settings.MEDIA_ROOT+new_name)
                self.banner.name = new_name
                super(Advertise, self).save(*args, **kwargs)

            # 위의 경우가 아니면 그냥 저장함
            else:
                super(Advertise, self).save(*args, **kwargs)
        # 존재하지 않는 새로운 아이디일 경우 save를 한다.
        else:
            change_image_size(self, *args, **kwargs)

            self.num = self.id
            super(Advertise, self).save(*args, **kwargs)


