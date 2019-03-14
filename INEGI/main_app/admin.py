from django.contrib import admin
from .models import *

# Register your models here.

admin.site.register(MyUser)
admin.site.register(Tower)
admin.site.register(DataSetPG)
admin.site.register(Cluster)
