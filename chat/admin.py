from django.contrib import admin
from .models import ChatRoom, Message

@admin.register(ChatRoom)
class ChatRoomAdmin(admin.ModelAdmin):
    list_display = ("name", "id", "created_by", "task", "created_at")
    search_fields = ("name",)

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ("room", "id", "sender", "created_at")
    search_fields = ("content",)
