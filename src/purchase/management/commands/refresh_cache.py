from django.core.management.base import BaseCommand

from purchase.models import Cache


class Command(BaseCommand):
    help = "Refresh cache"

    def handle(self, *args, **options):  # noqa: ARG002
        Cache.get_solo().refresh()
