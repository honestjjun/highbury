from django.conf.urls import url

from . import views


urlpatterns=[
    # 리그 페이지
    url(r'^match/$', views.match, name="match"),
    url(r'^match/(?P<year_value>[0-9]+)/(?P<month_value>[0-9]+)/(?P<value>[-\w]+)/$', views.match, name='match2'),
    url(r'^match/(?P<game>[-\w]+)/$', views.match_point, name='match_point'),

    # 투표 시스템
    url(r'^vote/$', views.vote, name="vote"),
    url(r'^vote/end/$', views.dead_survey, name='dead_survey'),

    url(r'^vote/question/(?P<question_id>[0-9]+)$', views.question, name='question'),
]