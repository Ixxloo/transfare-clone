import secrets
import uuid
from datetime import timedelta
from django.conf import settings
from django.db import models
from django.utils import timezone


def make_token():
    return secrets.token_urlsafe(16)


def default_expiry():
    return timezone.now() + timedelta(days=7)


class Transfer(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    token = models.CharField(max_length=64, unique=True, db_index=True, default=make_token)

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name="transfers",
    )

    message = models.TextField(blank=True)
    password_hash = models.CharField(max_length=128, blank=True)

    total_size = models.BigIntegerField(default=0)
    download_count = models.IntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiry)

    is_complete = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Transfer {self.token}"

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at

    @property
    def is_available(self):
        return self.is_complete and not self.is_deleted and not self.is_expired


class TransferFile(models.Model):
    transfer = models.ForeignKey(Transfer, on_delete=models.CASCADE, related_name="files")

    key = models.CharField(max_length=512)          # path in R2
    original_name = models.CharField(max_length=255)
    size = models.BigIntegerField(default=0)
    content_type = models.CharField(max_length=120, blank=True)

    uploaded = models.BooleanField(default=False)

    def __str__(self):
        return self.original_name