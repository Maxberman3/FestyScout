from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.contrib.auth.models import User
from .models import Band,Festival

# Register your models here.
admin.site.register(Band)
admin.site.register(Festival)
