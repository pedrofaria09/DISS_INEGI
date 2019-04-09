from django.conf.urls import url

from . import views

urlpatterns =[
    url(r'^$', views.index, name='index'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),

    url(r'^add_tower/?$', views.add_tower, name='add_tower'),
    url(r'^add_user/?$', views.add_user, name='add_user'),
    url(r'^add_cluster/?$', views.add_cluster, name='add_cluster'),
    url(r'^add_equipment/?$', views.add_equipment, name='add_equipment'),
    url(r'^add_type/(?P<type>([\w ]+))$', views.add_type, name='add_type'),
    url(r'^add_machine/?$', views.add_machine, name='add_machine'),
    url(r'^add_conf_period/(?P<tower_id>[0-9]+)$', views.add_conf_period, name='add_conf_period'),
    url(r'^add_calibration/(?P<equipment_id>[0-9]+)$', views.add_calibration, name='add_calibration'),
    url(r'^add_associate_towers/$', views.add_associate_towers, name='add_associate_towers'),
    url(r'^add_equipment_config/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)$', views.add_equipment_config, name='add_equipment_config'),
    url(r'^add_status/?$', views.add_status, name='add_status'),

    url(r'^list_towers/?$', views.list_towers, name='list_towers'),
    url(r'^list_users/?$', views.list_users, name='list_users'),
    url(r'^list_clusters/?$', views.list_clusters, name='list_clusters'),
    url(r'^list_equipments/?$', views.list_equipments, name='list_equipments'),
    url(r'^list_type/(?P<type>([\w ]+))$', views.list_type, name='list_type'),
    url(r'^list_machines/?$', views.list_machines, name='list_machines'),
    url(r'^list_associate_towers/$', views.list_associate_towers, name='list_associate_towers'),
    url(r'^list_status/?$', views.list_status, name='list_status'),

    url(r'^view_tower/(?P<tower_id>([\w ]+))$', views.view_tower, name='view_tower'),
    url(r'^view_user/(?P<user_id>[0-9]+)$', views.view_user, name='view_user'),
    url(r'^view_cluster/(?P<cluster_id>([\w ]+))$', views.view_cluster, name='view_cluster'),
    url(r'^view_equipment/(?P<equipment_id>([\w ]+))$', views.view_equipment, name='view_equipment'),
    url(r'^view_type/(?P<equipment_id>([\w ]+))/(?P<type>([\w ]+))$', views.view_type, name='view_type'),
    url(r'^view_machine/(?P<machine_id>([\w ]+))$', views.view_machine, name='view_machine'),
    url(r'^view_conf_period/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)$', views.view_conf_period, name='view_conf_period'),
    url(r'^view_calibration/(?P<equipment_id>[0-9]+)/(?P<calib_id>[0-9]+)$', views.view_calibration, name='view_calibration'),
    url(r'^view_associate_towers/(?P<association_id>([\w ]+))$', views.view_associate_towers, name='view_associate_towers'),
    url(r'^view_equipment_config/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<equi_conf_id>[0-9]+)$', views.view_equipment_config, name='view_equipment_config'),
    url(r'^view_status/(?P<status_id>[0-9]+)$', views.view_status, name='view_status'),

    url(r'^delete_tower/?$', views.delete_tower, name='delete_tower'),
    url(r'^delete_user/?$', views.delete_user, name='delete_user'),
    url(r'^delete_cluster/?$', views.delete_cluster, name='delete_cluster'),
    url(r'^delete_equipment/?$', views.delete_equipment, name='delete_equipment'),
    url(r'^delete_type/?$', views.delete_type, name='delete_type'),
    url(r'^delete_machine/?$', views.delete_machine, name='delete_machine'),
    url(r'^delete_conf_period/?$', views.delete_conf_period, name='delete_conf_period'),
    url(r'^delete_calibration/?$', views.delete_calibration, name='delete_calibration'),
    url(r'^delete_associate_tower/?$', views.delete_associate_tower, name='delete_associate_tower'),
    url(r'^delete_equipment_config/?$', views.delete_equipment_config, name='delete_equipment_config'),
    url(r'^delete_status/?$', views.delete_status, name='delete_status'),

    url(r'^equipment-type-autocomplete/$', views.EquipmentTypeAutocomplete.as_view(), name='equipment-type-autocomplete'),
    url(r'^equipment-autocomplete/$', views.EquipmentAutocomplete.as_view(), name='equipment-autocomplete'),
    url(r'^tower-autocomplete/$', views.TowerAutocomplete.as_view(), name='tower-autocomplete'),
    url(r'^group-autocomplete/$', views.GroupAutocomplete.as_view(), name='group-autocomplete'),
    url(r'^model-autocomplete/$', views.ModelAutocomplete.as_view(), name='model-autocomplete'),
    url(r'^user-autocomplete/$', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    url(r'^calibration-autocomplete/$', views.CalibrationAutocomplete.as_view(), name='calibration-autocomplete'),

    url(r'^ban_user/?$', views.ban_user, name='ban_user'),

    url(r'^show_towers_data_mongo/?$', views.show_towers_data_mongo, name='show_towers_data_mongo'),
    url(r'^add_raw_data_mongo/?$', views.add_raw_data_mongo, name='add_raw_data_mongo'),

    url(r'^show_towers_data_influx/?$', views.show_towers_data_influx, name='show_towers_data_influx'),
    url(r'^add_raw_data_influx/?$', views.add_raw_data_influx, name='add_raw_data_influx'),

    url(r'^show_towers_data_pg/?$', views.show_towers_data_pg, name='show_towers_data_pg'),
    url(r'^add_raw_data_pg/?$', views.add_raw_data_pg, name='add_raw_data_pg'),

    url(r'^wizard/?$', views.FormWizardView.as_view(), name='wizard'),

    url(r'^add_type_equipment/$', views.add_type_equipment, name='add_type_equipment'),
    url(r'^add_type_model/$', views.add_type_model, name='add_type_model'),

]