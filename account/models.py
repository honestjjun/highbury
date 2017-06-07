from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from random import randint
from .manager import MyUserManager
from PIL import Image


def tSplit(s, sep):
    stack = [s]
    for char in sep:
        pieces = []
        for subStr in stack:
            pieces.extend(subStr.split(char))
        stack = pieces
    return stack


class MyUser(AbstractBaseUser, PermissionsMixin):
    SEX_CHOICES = (
        ('man', 'man'),
        ('woman', 'woman')
    )
    email = models.EmailField(verbose_name='email', unique=True)
    nickname = models.CharField(max_length=255)
    sex = models.CharField(max_length=5, choices=SEX_CHOICES, default='man')
    date_of_birth = models.DateField(blank=True)

    photo = models.ImageField(upload_to='profile_photo', default='default/default.png')
    tel = models.IntegerField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    created = models.DateTimeField(default=timezone.now)
    updated = models.DateField(blank=True, null=True)

    recommend_free_board = models.CharField(max_length=255, blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_yellow = models.BooleanField(default=False)
    is_red = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_input_game_result = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['nickname', 'sex', 'date_of_birth']

    def get_full_name(self):
        return self.nickname

    def get_short_name(self):
        return self.nickname

    def __str__(self):
        return self.nickname

    @property
    def is_staff(self):
        return self.is_superuser

    def update(self, size = (160,160)):
        user_email_split = tSplit(self.email, "@.")
        user_email_join = '_'.join(user_email_split)
        self.photo.name = '{}.jpg'.format(user_email_join)
        super(MyUser, self).save()
        pw = self.photo.width
        ph = self.photo.height
        nw = size[0]
        nh = size[1]

        if (pw, ph) != (nw, nh):
            filename = str(self.photo.path)
            image = Image.open(filename)
            pr = float(pw) / float(ph)
            nr = float(nw) / float(nh)

            if pr > nr:
                # photo aspect is wider than destination ratio
                tw = int(round(nh * pr))
                image = image.resize((tw, nh), Image.ANTIALIAS)
                l = int(round((tw - nw)/2.0))
                image = image.crop((l, 0, l+nw, nh))
            elif pr < nr:
                # photo aspect is taller than destination ratio
                th = int(round(nw/pr))
                image = image.resize((nw, th), Image.ANTIALIAS)
                t = int(round((th - nh)/2.0))
                image = image.crop((0, t, nw, t+nh))
            else:
                # photo aspect matches the destination ratio
                image = image.resize(size, Image.ANTIALIAS)

            image.save(filename)


class RegistEmail(models.Model):
    email = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        super(RegistEmail, self).save(*args, **kwargs)
        self.barcode = 'highbury-user'+str(randint(10000000,99999999))+str(self.id)
        super(RegistEmail, self).save(*args, **kwargs)
