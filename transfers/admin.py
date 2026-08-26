from django.contrib import admin
from .models import Transfer, TransferFile


class TransferFileInline(admin.TabularInline):
    model = TransferFile
    extra = 0


@admin.register(Transfer)
class TransferAdmin(admin.ModelAdmin):
    list_display = ("token", "owner", "total_size", "download_count", "expires_at", "is_complete", "is_deleted")
    list_filter = ("is_complete", "is_deleted")
    search_fields = ("token",)
    inlines = [TransferFileInline]