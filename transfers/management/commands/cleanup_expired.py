from django.core.management.base import BaseCommand
from django.utils import timezone

from transfers.models import Transfer
from transfers.storage import delete_object


class Command(BaseCommand):
    help = "Delete files for expired transfers and mark them deleted."

    def handle(self, *args, **options):
        expired = Transfer.objects.filter(
            expires_at__lt=timezone.now(),
            is_deleted=False,
        )

        count = 0
        for transfer in expired:
            for f in transfer.files.all():
                try:
                    delete_object(f.key)
                except Exception as e:
                    self.stderr.write(f"Could not delete {f.key}: {e}")
            transfer.is_deleted = True
            transfer.save()
            count += 1

        self.stdout.write(self.style.SUCCESS(f"Cleaned {count} transfers."))