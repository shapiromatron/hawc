from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = """Reset user one-time password."""

    def add_arguments(self, parser):
        parser.add_argument(
            "email", type=str, help="Email to unset one-time password",
        )

    def handle(self, email, **options):
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise CommandError(f"User not found: {email}")

        user.otp_secret = ""
        user.save()

        message = f"One-Time Password (OTP) for {email} is disabled."
        self.stdout.write(self.style.SUCCESS(message))
