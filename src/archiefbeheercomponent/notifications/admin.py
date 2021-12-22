from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("user", "destruction_list")
    date_hierarchy = "created"
    raw_id_fields = ("user", "destruction_list")
