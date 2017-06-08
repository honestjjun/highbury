from .base import *


ALLOWED_HOSTS = ['*']

DEBUG = True

USE_TZ = False

INSTALLED_APPS += [
    'storages'
]

DATABASES = {
    'default': {
        'ENGINE': os.environ.get('DB_ENGINE', 'django.db.backends.postgresql_psycopg2'),
        'NAME': os.environ['DB_NAME'],
        'USER': os.environ['DB_USER'],
        'PASSWORD': os.environ['DB_PASSWORD'],
        'HOST': os.environ['DB_HOST'],
        'PORT': os.environ['DB_PORT'],
    }
}


# 기본 static/media 저장소를 django-storages 로 변경
STATICFILES_STORAGE = 'highbury.storages.StaticS3Boto3Storage'
DEFAULT_FILE_STORAGE = 'highbury.storages.MediaS3Boto3Storage'


# S3 파일 관리에 필요한 최소한 설정
# 소스 코드에 설정 정보를 남기지 마세요. 환경 변수를 통한 설정 추천
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_STORAGE_BUCKET_NAME = os.environ['AWS_STORAGE_BUCKET_NAME']
#AWS_S3_CUSTOM_DOMAIN = 'd1k76vw1kjnwej.cloudfront.net'

AWS_S3_REGION_NAME = os.environ.get('AWS_S3_REGION_NAME', 'ap-northeast-2')