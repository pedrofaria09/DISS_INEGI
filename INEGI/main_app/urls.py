from django.conf.urls import url
from django.views.generic import RedirectView

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^import_raw_data/$', views.import_raw_data, name='import_raw_data'),
    url(r'^data_visualization/$', views.data_visualization, name='data_visualization'),
    url(r'^login/$', views.login_view, name='login'),
    url(r'^logout/$', views.logout_view, name='logout'),
    url(r'^search/?$', views.search, name='search'),
    url(r'^ban_user/?$', views.ban_user, name='ban_user'),
    url(r'^pdf/?$', views.GeneratePdf.as_view(), name='pdf'),

    # Add one component
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
    url(r'^add_classification_period/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<equi_conf_id>[0-9]+)$', views.add_classification_period, name='add_classification_period'),
    url(r'^add_dimension_type/?$', views.add_dimension_type, name='add_dimension_type'),
    url(r'^add_dimension/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<equi_conf_id>[0-9]+)$', views.add_dimension, name='add_dimension'),
    url(r'^add_comment_classification/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<equi_conf_id>[0-9]+)/(?P<classification_id>[0-9]+)$', views.add_comment_classification, name='add_comment_classification'),
    url(r'^add_comment_tower/(?P<tower_id>[0-9]+)$', views.add_comment_tower, name='add_comment_tower'),

    # List components
    url(r'^list_towers/?$', views.list_towers, name='list_towers'),
    url(r'^list_users/?$', views.list_users, name='list_users'),
    url(r'^list_clusters/?$', views.list_clusters, name='list_clusters'),
    url(r'^list_equipments/?$', views.list_equipments, name='list_equipments'),
    url(r'^list_type/(?P<type>([\w ]+))$', views.list_type, name='list_type'),
    url(r'^list_machines/?$', views.list_machines, name='list_machines'),
    url(r'^list_associate_towers/$', views.list_associate_towers, name='list_associate_towers'),
    url(r'^list_status/?$', views.list_status, name='list_status'),
    url(r'^list_dimensions_type/?$', views.list_dimensions_type, name='list_dimensions_type'),

    # View one component
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
    url(r'^view_classification_period/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<equi_conf_id>[0-9]+)/(?P<classification_id>[0-9]+)$', views.view_classification_period, name='view_classification_period'),
    url(r'^view_dimension_type/(?P<dimension_type_id>[0-9]+)$', views.view_dimension_type, name='view_dimension_type'),
    url(r'^view_dimension/(?P<tower_id>[0-9]+)/(?P<period_id>[0-9]+)/(?P<equi_conf_id>[0-9]+)/(?P<dimension_id>[0-9]+)$', views.view_dimension, name='view_dimension'),
    url(r'^view_comment/(?P<tower_id>[0-9]+)/(?P<comment_id>[0-9]+)/(?P<type>([\w ]+))$', views.view_comment, name='view_comment'),

    # Deletes
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
    url(r'^delete_classification_period/?$', views.delete_classification_period, name='delete_classification_period'),
    url(r'^delete_dimension_type/?$', views.delete_dimension_type, name='delete_dimension_type'),
    url(r'^delete_dimension/?$', views.delete_dimension, name='delete_dimension'),
    url(r'^delete_comment/?$', views.delete_comment, name='delete_comment'),

    # AutoCompletes
    url(r'^equipment-type-autocomplete/$', views.EquipmentTypeAutocomplete.as_view(), name='equipment-type-autocomplete'),
    url(r'^equipment-autocomplete/$', views.EquipmentAutocomplete.as_view(), name='equipment-autocomplete'),
    url(r'^tower-autocomplete/$', views.TowerAutocomplete.as_view(), name='tower-autocomplete'),
    url(r'^group-autocomplete/$', views.GroupAutocomplete.as_view(), name='group-autocomplete'),
    url(r'^model-autocomplete/$', views.ModelAutocomplete.as_view(), name='model-autocomplete'),
    url(r'^user-autocomplete/$', views.UserAutocomplete.as_view(), name='user-autocomplete'),
    url(r'^calibration-autocomplete/$', views.CalibrationAutocomplete.as_view(), name='calibration-autocomplete'),
    url(r'^status-autocomplete/$', views.StatusAutocomplete.as_view(), name='status-autocomplete'),
    url(r'^unit-autocomplete/$', views.UnitAutocomplete.as_view(), name='unit-autocomplete'),
    url(r'^statistic-autocomplete/$', views.StatisticAutocomplete.as_view(), name='statistic-autocomplete'),
    url(r'^metric-autocomplete/$', views.MetricAutocomplete.as_view(), name='metric-autocomplete'),
    url(r'^component-autocomplete/$', views.ComponentAutocomplete.as_view(), name='component-autocomplete'),
    url(r'^dimension-type-autocomplete/$', views.DimensionTypeAutocomplete.as_view(), name='dimension-type-autocomplete'),
    url(r'^comment-tower-autocomplete/$', views.CommentTowerTypeAutocomplete.as_view(), name='comment-tower-autocomplete'),
    url(r'^comment-classification-autocomplete/$', views.CommentClassificationTypeAutocomplete.as_view(),name='comment-classification-autocomplete'),
    url(r'^affiliation-autocomplete/$', views.AffiliationAutocomplete.as_view(), name='affiliation-autocomplete'),
    url(r'^tower-conf_periods-autocomplete/$', views.TowerConfPeriodsAutocomplete.as_view(), name='tower-conf_periods-autocomplete'),

    # Charts
    url(r'^classify_from_charts/?$', views.classify_from_charts, name='classify_from_charts'),
    # django_nvd3
    url(r'^chart_nvd3/?$', views.chart_nvd3, name='chart_nvd3'),
    # django_graphos
    url(r'^chart_graphos/?$', views.chart_graphos, name='chart_graphos'),
    # django_chartsjs
    url(r'^chart_chartjs/?$', views.chart_chartjs, name='chart_chartjs'),
    url(r'^line_chart_json/?$', views.LineChartJson.as_view(), name='line_chart_json'),
    url(r'^view_raw_data/?$', views.LineHighchartRawData.as_view(), name='view_raw_data'),
    url(r'^line_highchart_json_tests/?$', views.LineHighchartJsonTESTS.as_view(), name='line_highchart_json_tests'),
    url(r'^view_classifications_chart/?$', views.XChartClassifications, name='view_classifications_chart'),

    # Databases
    url(r'^show_towers_data_mongo/?$', views.show_towers_data_mongo, name='show_towers_data_mongo'),
    url(r'^add_raw_data_mongo/?$', views.add_raw_data_mongo, name='add_raw_data_mongo'),
    url(r'^add_raw_data_mongo2/?$', views.add_raw_data_mongo2, name='add_raw_data_mongo2'),
    url(r'^dropdb_mongo/?$', views.dropdb_mongo, name='dropdb_mongo'),
    url(r'^count_mongo/?$', views.count_mongo, name='count_mongo'),
    url(r'^query_mg/?$', views.query_mg, name='query_mg'),

    url(r'^show_towers_data_influx/?$', views.show_towers_data_influx, name='show_towers_data_influx'),
    url(r'^add_raw_data_influx/?$', views.add_raw_data_influx, name='add_raw_data_influx'),
    url(r'^add_raw_data_influx2/?$', views.add_raw_data_influx2, name='add_raw_data_influx2'),
    url(r'^dropdb_influx/?$', views.dropdb_influx, name='dropdb_influx'),
    url(r'^count_influx/?$', views.count_influx, name='count_influx'),
    url(r'^query_in/?$', views.query_in, name='query_in'),

    url(r'^show_towers_data_pg/?$', views.show_towers_data_pg, name='show_towers_data_pg'),
    url(r'^add_raw_data_pg/?$', views.add_raw_data_pg, name='add_raw_data_pg'),
    url(r'^add_raw_data_pg2/?$', views.add_raw_data_pg2, name='add_raw_data_pg2'),
    url(r'^dropdb_pg/?$', views.dropdb_pg, name='dropdb_pg'),
    url(r'^count_pg/?$', views.count_pg, name='count_pg'),
    url(r'^query_pg/?$', views.query_pg, name='query_pg'),

    # Types
    url(r'^add_calib_equip/$', views.add_calib_equip, name='add_calib_equip'),
    url(r'^add_type_equipment/$', views.add_type_equipment, name='add_type_equipment'),
    url(r'^add_type_model/$', views.add_type_model, name='add_type_model'),
    url(r'^add_type_status/$', views.add_type_status, name='add_type_status'),
    url(r'^add_type_unit/$', views.add_type_unit, name='add_type_unit'),
    url(r'^add_type_statistic/$', views.add_type_statistic, name='add_type_statistic'),
    url(r'^add_type_metric/$', views.add_type_metric, name='add_type_metric'),
    url(r'^add_type_component/$', views.add_type_component, name='add_type_component'),
    url(r'^add_type_dimension/$', views.add_type_dimension, name='add_type_dimension'),
    url(r'^add_type_affiliation/$', views.add_type_affiliation, name='add_type_affiliation'),
    url(r'^add_type_user_group/$', views.add_type_user_group, name='add_type_user_group'),
    url(r'^add_equipment_json/$', views.add_equipment_json, name='add_equipment_json'),

    url(r'^favicon\.ico$',RedirectView.as_view(url='/static/img/favicon.ico')),
]
