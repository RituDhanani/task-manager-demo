from django.conf import settings
from django.db import models

User = settings.AUTH_USER_MODEL

class ChatRoom(models.Model):
    """
    Represents a chat room.
    Can be linked to a Task or be a general room.
    """
    name = models.CharField(max_length=255)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="created_chatrooms",
    )

    # Optional: link chat to a task (very useful for your project)
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="chatrooms",
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Message(models.Model):
    """
    Stores chat messages.
    Persisted to DB for history & reconnect scenarios.
    """
    room = models.ForeignKey(
        ChatRoom,
        on_delete=models.CASCADE,
        related_name="messages",
    )

    sender = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="chat_messages",
    )

    content = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Message from {self.sender} in {self.room}"
