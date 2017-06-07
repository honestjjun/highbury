from django.conf.urls import url

from . import views


urlpatterns = [
    #게시판 > 리스트 / 상세 페이지
    url(r'^free/list/$', views.list, name='list'),
    url(r'^review/list/(?P<value>[-\w]+)$', views.list, name='review_list'),
    url(r'^detail/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/$', views.detail, name='detail'),

    #게시글 선택
    url(r'^write/choice/write/$', views.choice_write, name='choice_write'),
    url(r'^write/choice/game/(?P<sort>[-\w]+)/$', views.choice_game, name="choice_game"),

    #게시글 작성
    url(r'^write/free/$', views.write_free, name='write_free'),
    url(r'^write/before_game/(?P<match_id>[0-9]+)$', views.write_before, name='write_before'),
    url(r'^write/after_game/(?P<match_id>[0-9]+)/$', views.write_after, name='write_after'),
    url(r'^write/player/(?P<id>[0-9]+)/$', views.write_player, name='write_player'),

    #게시글 수정 / 게시글 삭제
    url(r'^change/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/(?P<sort>[-\w]+)/$', views.change, name='change'),
    url(r'^delete/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/$', views.article_delete, name='article_delete'),
    url(r'^recommend/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/$', views.article_recommend, name='article_recommend'),

    #코멘트 > 댓글 / 댓글의 댓글 / 댓글 삭제 / 댓글의 댓글 삭제
    url(r'^comment/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/(?P<comment_id>[0-9]+)$', views.detail, name='comment'),
    url(r'^comment/delete/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/(?P<comment_id>[0-9]+)/$', views.comment_delete, name='comment_delete'),
]
