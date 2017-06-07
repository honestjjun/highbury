from django.conf.urls import url

from . import views


urlpatterns=[
    url(r'^take_message_box/$', views.take_message_box, name='take_message_box'),

    url(r'^detail/(?P<message_id>[0-9]+)/(?P<value>[-\w]+)/$', views.detail, name='detail'),
    url(r'^send_message_box/$', views.send_message_box, name='send_message_box'),
    url(r'^same_nickname/$', views.same_nickname, name='same_nickname'),

    url(r'^message/delete/(?P<id>[0-9]+)/(?P<which>[-\w]+)/$', views.delete_message, name='delete_message'),
    url(r'^send_message/$', views.send_message, name='send_message'),
    url(r'^send_message/(?P<reply>[-\w]+)/$', views.send_message, name='reply_send_message'),

    url(r'^message/message_ajax$', views.message_ajax, name='message_ajax'),
]
