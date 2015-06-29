from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from myuser.models import HAWCUser


HELP_TEXT = """Interactive prompt to create users/send welcome emails. Can either use
interactive prompts, or non-interactive prompts via command line. If using the
command-line, specify lists of assessments based on primary keys, comma-separated.
To add no assessments, enter the value "N". To send a welcome email, enter "Y" or "N".

A complete example may be:

python manage.py create_user --noinput hikingfan@gmail.com George Washington N 118 N Y
"""


def get_assessment_ids(txt):
    if len(txt) == 0 or txt.lower()[0] == "n":
        return False
    ids = txt.replace(" ", "").split(",")
    return [int(d) for d in ids]


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument('email', nargs='?', default=None)
        parser.add_argument('first_name', nargs='?', default=None)
        parser.add_argument('last_name', nargs='?', default=None)
        parser.add_argument('pms', nargs='?', default=None)
        parser.add_argument('tms', nargs='?', default=None)
        parser.add_argument('rvs', nargs='?', default=None)
        parser.add_argument('send_welcome', nargs='?', default=None)
        parser.add_argument(
            '--noinput',
            action='store_false',
            dest='interactive', default=True,
            help=('Tells Django to NOT prompt the user for input of any kind. '
                  'You must provide all 7 input fields to create without input'))

    def handle(self, *args, **options):
        interactive = options.get('interactive')
        if interactive:
            try:
                email = raw_input("Enter user email: ")
                first_name = raw_input("Enter first name: ")
                last_name = raw_input("Enter last name: ")
                pms = raw_input("Enter assessment ids to assign as project manager (comma delimited, N if none): ")
                tms = raw_input("Enter assessment ids to assign as team-member (comma delimited, N if none): ")
                rvs = raw_input("Enter assessment ids to assign as reviewer (comma delimited, N if none): ")
                send_welcome = raw_input("Send welcome email [Y or N] ? ")
            except KeyboardInterrupt:
                self.stdout.write("\nUser creation aborted.\n")
                return
        else:
            email = options.get('email')
            first_name = options.get('first_name')
            last_name = options.get('last_name')
            pms = options.get('pms')
            tms = options.get('tms')
            rvs = options.get('rvs')
            send_welcome = options.get('send_welcome')
            print email, first_name, last_name, pms, tms, rvs, send_welcome
            if not all((email, first_name, last_name, pms, tms, rvs, send_welcome)):
                raise CommandError("Invalid number of input arguments")

        HAWCUser.objects.create_user_batch(
            email=email,
            first_name=first_name,
            last_name=last_name,
            pms=get_assessment_ids(pms),
            tms=get_assessment_ids(tms),
            rvs=get_assessment_ids(rvs),
            welcome_email=(send_welcome.lower() == "y")
        )
