from textwrap import dedent

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from faker import Faker


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
                "Are you sure you want to do this?\n\n"
                "Type 'yes' to continue, or 'no' to cancel: ",
            )
            if input("".join(message)) != "yes":
                raise CommandError("Scrubbing user data cancelled.")

        fake = Faker()
        Faker.seed(555)

        # slow; since we're using the same password for everyone... cache it
        hash_password = make_password("password")

        # generate
        for user in get_user_model().objects.all():
            user.first_name = fake.first_name()
            user.last_name = fake.last_name()
            user.email = f"{user.first_name.lower()}.{user.last_name.lower()}@{fake.domain_name()}"
            user.password = hash_password
            user.save()

        # save superuser
        superuser = get_user_model().objects.filter(is_superuser=True).first()
        superuser.first_name = "Super"
        superuser.last_name = "Duper"
        superuser.email = "webmaster@hawcproject.org"
        user.password = hash_password
        superuser.save()

        num_users = get_user_model().objects.count()
        message = dedent(
            f"""\
        Rewrite complete!

        - All {num_users} users have randomly generated names and email-addresses.
        - All {num_users} users have passwords set to `password`
        - A superuser has the username `webmaster@hawcproject.org`
        - A superuser has the password `password`
        """
        )

        self.stdout.write(self.style.SUCCESS(message))
