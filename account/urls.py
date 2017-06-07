from django.conf.urls import url

from . import views


urlpatterns = [
    # main
    url(r'^$', views.main, name='main'),

    # 로그인 / 로그아웃
    url(r'^login$', views.login, name='login'),
    url(r'^logout$', views.logout, name='logout'),
    url(r'^password/email$', views.password_email, name='password_email'),
    url(r'^password/change/(?P<nickname>[-\w]+)$', views.password_change, name='password_change'),

    # 회원 가입
    url(r'^register/terms$', views.register_terms, name='register_terms'),
    url(r'^register/email$', views.register_email, name='register_email'),
    url(r'^register/email/(?P<value>[-\w]+)$', views.register_email_check, name='register_email_check'),
    url(r'^register/done$', views.register_done, name='register_done'),
    url(r'^register/(?P<email_barcode>[-\w]+)$', views.register, name='register'),

    # mypage # user
    url(r'^mypage$', views.mypage, name='mypage'),
    url(r'^mypage/nickname$', views.same_nickname, name='same_nickname'),
    url(r'^mypage/nickname/input$', views.nickname_input, name='nickname_input'),
    url(r'^mypage/picture$', views.input_picture, name='input_picture'),
    url(r'^mypage/password/change$', views.mypage_password_change, name='mypage_password_change'),
    url(r'^mypage/notify$', views.notify, name='notify'), # 아직 미구현

    # mypage # point
    url(r'^mypage/point$', views.point, name='point'),
    url(r'^mypage/point/use_point$', views.use_point, name='use_point'),
    url(r'^mypage/point/achievement/(?P<sort>[-\w]+)$', views.achievement, name='achievement'),

    # profile
    url(r'^profile/(?P<user>[-\w]+)$', views.profile, name='profile'),
    url(r'^profile/(?P<user>[-\w]+)/write$', views.profile_write, name='profile_write'),
    url(r'^profile/(?P<user>[-\w]+)/achievements/(?P<sort>[-\w]+)$', views.profile_achievements, name='profile_achievements'),
]
