from django.conf.urls import url

from . import views


urlpatterns=[
    # 쓸데 없는 사진 없애기(썸머 노트)
    url(r'^delete_trash_picture/$', views.delete_trash_picture, name='delete_trash_picture'),

    # 경기 결과 입력
    url(r'^input_game_select$', views.input_game_select, name='input_game_select'),
    url(r'^input_game_result/(?P<match_id>[0-9]+)$', views.input_game_result, name='input_game_result'),

    # 신고 관련
    url(r'^charge/$', views.charge, name='charge'),
    url(r'^charge/ajax', views.charge_ajax, name='charge_ajax'),
    url(r'^charge/result/ajax', views.charge_result_ajax, name='charge_result_ajax'),

    # 포인트 샵 태그 입력
    url(r'^input_pointshop_tags$', views.input_pointshop_tags, name='input_pointshop_tags'),
    url(r'^input_pointshop_tags/(?P<id>[0-9]+)/(?P<slug>[-\w]+)$', views.input_pointshop_tags, name='product_tags'),

    # 채팅 관련(연습)
    url(r'^chat/$', views.chat, name='chat'),
]
