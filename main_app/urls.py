from django.conf.urls import url

from . import views

urlpatterns =[
    url(r'^$', views.index, name='index'),
    url(r'^add_tower/$', views.add_tower, name='add_tower'),
    url(r'^show_towers/$', views.show_towers, name='show_towers'),
    url(r'^delete_tower/(?P<tower_id>[0-9]+)$', views.delete_tower, name='delete_tower'),
    url(r'^show_towers_data/$', views.show_towers_data, name='show_towers_data'),
    url(r'^add_raw_data/$', views.add_raw_data, name='add_raw_data'),
    url(r'^show_towers_data_influx/$', views.show_towers_data_influx, name='show_towers_data_influx'),
]