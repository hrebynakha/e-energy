"""Models for energyweb"""

from django.db import models


class ChatUser(models.Model):
    """Chat user model"""

    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return (
            str(self.username)
            or str(f"{self.first_name or ''} {self.last_name or ''}".strip())
            or str(self.chat_id)
        )


class Queue(models.Model):
    """Queue model"""

    name = models.CharField(max_length=255, unique=True)
    current_state = models.JSONField(blank=True, null=True)
    prev_state = models.JSONField(blank=True, null=True)

    def __str__(self):
        return f"Queue: {self.name}"


class Subscription(models.Model):
    """Subscription model"""

    user = models.ForeignKey(
        ChatUser, on_delete=models.CASCADE, related_name="subscriptions"
    )
    queue = models.ForeignKey(
        Queue, on_delete=models.CASCADE, related_name="subscriptions"
    )

    class Meta:
        unique_together = ("user", "queue")

    def __str__(self):
        return f"{self.user} → {self.queue}"
