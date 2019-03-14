from django.contrib import admin
from .models import MyUser, Tower, DataSetPG

# Register your models here.

admin.site.register(MyUser)
admin.site.register(Tower)
admin.site.register(DataSetPG)
