from django.contrib import admin
from django.db.models import JSONField
from django_json_widget.widgets import JSONEditorWidget
from .models import ChatUser, Queue, Subscription


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = ("id", "chat_id", "username", "first_name", "last_name")
    search_fields = ("username", "first_name", "last_name", "chat_id")
    ordering = ("id",)


@admin.register(Queue)
class QueueAdmin(admin.ModelAdmin):
    formfield_overrides = {
        JSONField: {"widget": JSONEditorWidget},
    }
    list_display = (
        "id",
        "name",
    )
    search_fields = ("name",)
    ordering = ("id", "name")


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "queue")
    search_fields = ("user__username", "queue__name")
    list_filter = ("queue",)
