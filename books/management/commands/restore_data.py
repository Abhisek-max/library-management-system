from django.core.management.base import BaseCommand
from django.core.management import call_command


class Command(BaseCommand):
    help = "Restore database backup"

    def handle(self, *args, **kwargs):
        call_command("loaddata", "backup.json")
        self.stdout.write(
            self.style.SUCCESS("Backup restored successfully")
        )