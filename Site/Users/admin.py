from django.contrib import admin

from .models import CustomUser, Status


class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser


class CustomUserStatus(admin.ModelAdmin):
    model = Status

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Status, CustomUserStatus)
