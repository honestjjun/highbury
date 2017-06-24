from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.utils import timezone

from io import BytesIO
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

    def pre_save(self, size = (160,160), update=None):
        # 정보에 사진이 있을 경우 리사이징 시켜 버림
        if self.photo:
            im = Image.open(self.photo).convert('RGB')

            output = BytesIO()

            im = im.resize(size)

            im.save(output, format='JPEG', quality=100)
            output.seek(0)

            # 파일명을 유저 이메일명으로 수정
            stack = [self.email]
            for char in "@.":
                pieces = []
                for subStr in stack:
                    pieces.extend(subStr.split(char))
                stack = pieces
            user_email_join = '_'.join(stack)

            # change the imagefield value to be the newley modifed image value
            self.photo = InMemoryUploadedFile(output, 'ImageField', "{}.jpg".format(user_email_join), 'image/jpeg', sys.getsizeof(output), None)
            if update:
                self.save(update_fields=['photo'])
        super(MyUser, self).save()


class RegistEmail(models.Model):
    email = models.CharField(max_length=255)
    barcode = models.CharField(max_length=100, blank=True, null=True)
    
    def __str__(self):
        return self.email
    
    def save(self, *args, **kwargs):
        super(RegistEmail, self).save(*args, **kwargs)
        self.barcode = 'highbury-user'+str(randint(10000000,99999999))+str(self.id)
        super(RegistEmail, self).save(*args, **kwargs)
