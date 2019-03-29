from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(MyUser)
admin.site.register(Tower)
admin.site.register(DataSetPG)
admin.site.register(Cluster)
admin.site.register(EquipmentType)
admin.site.register(Equipment)
admin.site.register(UserGroupType)
admin.site.register(Calibration)
admin.site.register(PeriodConfiguration)
admin.site.register(EquipmentCharacteristic)
admin.site.register(UserTowerDates)

# admin.site.register(TestTower)
# admin.site.register(TestUser)
# admin.site.register(TestDates)

admin.site.register(TestConfPeriod)
admin.site.register(TestSensorConfig)
admin.site.register(TestCalibration)
admin.site.register(TestEquipment)