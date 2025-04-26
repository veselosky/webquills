from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from webquills.sites.actions import create_default_groups_and_perms, create_site
from webquills.sites.models import Domain

User = get_user_model()


class Command(BaseCommand):
    help = "Set up a site for Webquills."

    def add_arguments(self, parser):
        parser.add_argument(
            "--user",
            type=str,
            help="The email or ID of the user who will own the site. Defaults to the superuser with the lowest ID.",
        )
        parser.add_argument(
            "--subdomain",
            type=str,
            default="www",
            help="The subdomain for the site. Defaults to 'www'.",
        )
        parser.add_argument(
            "--name",
            type=str,
            help="The name of the site. Defaults to '<subdomain>.<WEBQUILLS_ROOT_DOMAIN>'.",
        )

    def handle(self, *args, **options):
        # Check if there are any users in the database
        if not User.objects.exists():
            self.stderr.write("No users found. Please run `createsuperuser` first.")
            return

        # Determine the default user (superuser with the lowest ID)
        default_user = User.objects.filter(is_superuser=True).order_by("id").first()
        if not default_user:
            self.stderr.write("No superuser found. Please create a superuser first.")
            return

        # Resolve the user parameter
        user_input = options.get("user")
        if user_input:
            try:
                if user_input.isdigit():
                    user = User.objects.get(id=int(user_input))
                else:
                    user = User.objects.get(email=user_input)
            except User.DoesNotExist:
                self.stderr.write(f"User '{user_input}' not found.")
                return
        else:
            user = default_user

        # Resolve the subdomain and name parameters
        subdomain = options.get("subdomain") or "www"
        name = options.get("name") or f"{subdomain}.{settings.WEBQUILLS_ROOT_DOMAIN}"

        # Create default groups and permissions
        self.stdout.write("Creating default groups and permissions...")
        create_default_groups_and_perms()

        # Create the site
        self.stdout.write(f"Creating site '{name}' with subdomain '{subdomain}'...")
        try:
            site = create_site(user=user, name=name, subdomain=subdomain)
        except Exception as e:
            self.stderr.write(f"Error creating site: {e}")
            return

        # Check if this is the only site in the database
        if site and site.__class__.objects.count() == 1:
            self.stdout.write("Creating default domain 'localhost' for the site...")
            try:
                Domain.objects.create(
                    site=site,
                    display_domain="localhost",
                    normalized_domain="localhost",
                )
            except Exception as e:
                self.stderr.write(f"Error creating default domain: {e}")
                return

        self.stdout.write("Setup completed successfully.")
