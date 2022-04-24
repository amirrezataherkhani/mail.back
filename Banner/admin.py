from django.contrib import admin

# Register your models here.
from Banner.models import TimeTable, Banner

admin.site.register(Banner)
admin.site.register(TimeTable)
