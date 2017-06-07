from django.conf.urls import url

from . import views


urlpatterns = [
    # point shop list page
    url(r'^list/$', views.point_list, name='list'),
    url(r'^list/(?P<category_id>[0-9]+)$', views.point_list, name='category_list'),
    # point shop detail page
    url(r'^detail/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/$', views.point_detail, name='detail'),
    # point shop recommend page
    url(r'^detail/recommend/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/$', views.product_recommend, name='product_recommend'),
    # point shop buy complete page
    url(r'^complete/(?P<id>[0-9]+)/(?P<slug>[-\w]+)/(?P<order_num>[-\w]+)$', views.buy_complete, name='buy_complete'),
    # point shop delete page
    url(r'^delete/(?P<product_id>[0-9]+)/(?P<id>[0-9]+)/(?P<sort>[-\w]+)$', views.delete, name='delete'),
]