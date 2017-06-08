"""
Django settings for highbury project.

Generated by 'django-admin startproject' using Django 1.11.2.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
from django.urls import reverse_lazy

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'bz4lz^@0nyn2s=7787!7pxk!z_)0hnp94u#!^57v2qw7v%euqz'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',

    'data.apps.DataConfig',
    'advertise.apps.AdvertiseConfig',
    'arsenal.apps.ArsenalConfig',
    'administrator.apps.AdministratorConfig',
    'message.apps.MessageConfig',
    'search.apps.SearchConfig',
    'board_free.apps.BoardFreeConfig',
    'account.apps.AccountConfig',
    'pointshop.apps.PointshopConfig',
    'tag.apps.TagConfig',
    'lib',

    'django_summernote',
    'widget_tweaks',


]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'highbury.urls'

TEMPLATE_DIRS = (
    os.path.join(os.path.dirname(__file__), 'templates').replace('\\', '/'),
)

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'lib.context_processors.message_count',
                'lib.context_processors.notify_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'highbury.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

SUMMERNOTE_CONFIG = {
    'lang': 'ko-KR',
    'attachment_filesize_limit':700*5000
}

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Seoul'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')


# etc settings
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_HOST_USER = 'ionman83@gmail.com'
EMAIL_HOST_PASSWORD = 'nannorccc799'
EMAIL_PORT = 587


ABSOLUTE_URL_OVERRIDES = {
    'board_free.freeboard': lambda u: reverse_lazy('board_free:detail', args=[u.id, u.slug]),
    'pointshop.product': lambda u: reverse_lazy('pointshop:detail', args=[u.id, u.slug]),
}


AUTH_USER_MODEL = 'account.MyUser'

#INTERNAL_IPS = '127.0.0.1'

LOGIN_URL = '/login/'

DAILY_LOGIN_NUM = 1 # 로그인으로 얻을수 있는 점수와 횟수
DAILY_LOGIN_POINT = 50
DAILY_REVIEW_NUM = 2 # 리뷰 작성으로 얻을 수 있는 점수와 횟수
DAILY_REVIEW_POINT = 10
DAILY_BOARD_NUM = 5
DAILY_BOARD_POINT = 5
DAILY_COMMENT_NUM = 10
DAILY_COMMENT_POINT = 1
NEXT_GAME_VOTE_RESULT = 50 # 다음 경기 맞추기 이벤트 투표한 사람한테 주는 점수
NEXT_GAME_VOTE_CORRECT = 50 # 다음 경기 맞추기 이벤트 맞춘 사람한테 주는 점수
AFTER_GAME_GIVE_POINT = 50 # 최근 경기 간단 평점 남긴 사람한테 주는 점수


MAIN_ADVERTISEMENTS = (1140, 180)
SUB_TOP_ADVERTISEMENTS = (1140, 200)
RIGHT_TOP_ADVERTISEMENTS = (200, 200)