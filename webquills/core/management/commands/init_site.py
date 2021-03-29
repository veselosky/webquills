from django.core.management.base import BaseCommand, CommandError
from webquills.core.commands import initialize_site


class Command(BaseCommand):
    help = "Create site and home page in empty database"

    def handle(self, *args, **options):
        initialize_site()
