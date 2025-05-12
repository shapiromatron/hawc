from textwrap import dedent

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from hawc.apps.myuser.synthetic import generate


class Command(BaseCommand):
    help = """Anonymize user information."""

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            "--no-input",
            action="store_false",
            dest="interactive",
            default=True,
            help="Do NOT prompt the user for input of any kind.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        interactive = options["interactive"]
        if interactive:
            message = (
                "This will rewrite all users in the database with anonymous data.\n",
                "Are you sure you want to do this?\n\nType 'yes' to continue, or 'no' to cancel: ",
            )
            if input("".join(message)) != "yes":
                raise CommandError("Scrubbing user data cancelled.")

        self.update_site()
        self.update_users()

    def update_site(self):
        Site.objects.update(domain="127.0.0.1:8000", name="localhost")

    def update_users(self):
        # slow; but since we're using the same password for everyone... generate once
        hash_password = make_password("pw")

        # generate
        for user in get_user_model().objects.all():
            data = generate()
            user.first_name = data.first_name
            user.last_name = data.last_name
            user.email = data.email
            if user.external_id:
                user.external_id = data.username
            user.password = hash_password
            user.save()

        # save superuser
        superusers = (
            get_user_model().objects.filter(is_superuser=True, is_active=True).order_by("id")[:2]
        )
        for i, superuser in enumerate(superusers, start=1):
            superuser.first_name = "HAWC"
            superuser.last_name = f"Admin #{i}"
            superuser.email = f"admin{i}@hawcproject.org"
            superuser.external_id = f"admin{i}"
            superuser.save()

        num_users = get_user_model().objects.count()
        message = dedent(
            f"""\
        Rewrite complete!

        - All {num_users} users have randomly generated names and email addresses.
        - Two superusers have the usernames `admin1@hawcproject.org` and `admin2@hawcproject.org`
        - All {num_users} users have passwords set to `pw`
        """
        )

        self.stdout.write(self.style.SUCCESS(message))
