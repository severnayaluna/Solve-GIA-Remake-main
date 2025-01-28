from django.contrib import admin

from .models import *


class VariantAdmin(admin.ModelAdmin):
    pass


class TaskAdmin(admin.ModelAdmin):
    pass


class CustomGroupAdmin(admin.ModelAdmin):
    pass


class HomeWorkAdmin(admin.ModelAdmin):
    pass


class ResultAdmin(admin.ModelAdmin):
    pass


class AttemptAdmin(admin.ModelAdmin):
    pass


admin.site.register(Variant, VariantAdmin)
admin.site.register(Task, TaskAdmin)
admin.site.register(CustomGroup, CustomGroupAdmin)
admin.site.register(Homework, HomeWorkAdmin)
admin.site.register(Result, ResultAdmin)
admin.site.register(Attempt, AttemptAdmin)
