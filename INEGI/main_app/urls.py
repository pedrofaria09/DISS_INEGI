from django.conf.urls import url

from . import views

urlpatterns =[
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^add_tower/?$', views.add_tower, name='add_tower'),
    url(r'^add_user/?$', views.add_user, name='add_user'),

    url(r'^list_towers/?$', views.list_towers, name='list_towers'),
    url(r'^list_users/?$', views.list_users, name='list_users'),

    url(r'^view_tower/(?P<tower_id>[\w\-]+)$', views.view_tower, name='view_tower'),
    url(r'^view_user/(?P<user_id>[0-9]+)$', views.view_user, name='view_user'),

    url(r'^delete_tower/?$', views.delete_tower, name='delete_tower'),
    url(r'^delete_user/?$', views.delete_user, name='delete_user'),

    url(r'^ban_user/?$', views.ban_user, name='ban_user'),


    url(r'^show_towers_data_mongo/?$', views.show_towers_data_mongo, name='show_towers_data_mongo'),
    url(r'^add_raw_data_mongo/?$', views.add_raw_data_mongo, name='add_raw_data_mongo'),

    url(r'^show_towers_data_influx/?$', views.show_towers_data_influx, name='show_towers_data_influx'),
    url(r'^add_raw_data_influx/?$', views.add_raw_data_influx, name='add_raw_data_influx'),

    url(r'^show_towers_data_pg/?$', views.show_towers_data_pg, name='show_towers_data_pg'),
    url(r'^add_raw_data_pg/?$', views.add_raw_data_pg, name='add_raw_data_pg'),
]