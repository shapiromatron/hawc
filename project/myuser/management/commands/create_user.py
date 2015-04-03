from optparse import make_option

from django.core.management.base import BaseCommand, CommandError

from myuser.models import HAWCUser


HELP_TEXT = """Interactive prompt to create users/send welcome emails. Can either use
interactive prompts, or non-interactive prompts via command line. If using the
command-line, specify lists of assessments based on primary keys, comma-separated.
To add no assessments, enter the value "N". To send a welcome email, enter "y" or "n".

A complete example may be:

python manage.py create_user --noinput hikingfan@gmail.com George Washington 1,2,3 N N y
"""

def get_assessment_ids(txt):
    if len(txt) == 0 or txt.lower()[0] == "n":
        return False
    ids = txt.replace(" ", "").split(",")
    return [int(d) for d in ids]

class Command(BaseCommand):
    args = '<email> <first_name> <last_name> <pms> <tms> <rvs> <welcome_email>'
    help = HELP_TEXT

    def __init__(self, *args, **kwargs):
        # Options are defined in an __init__ method to support swapping out
        # custom user models in tests.
        super(Command, self).__init__(*args, **kwargs)

        self.option_list = BaseCommand.option_list + (
            make_option('--noinput', action='store_false', dest='interactive', default=True,
                help=('Tells Django to NOT prompt the user for input of any kind. '
                    'You must provide all 7 input fields to create without input')),
        )

    def handle(self, *args, **options):

        interactive = options.get('interactive')
        if interactive:
            if len(args) > 0:
                raise CommandError("Invalid number of input arguments")
            try:
                email = raw_input("Enter user email: ")
                first_name = raw_input("Enter first name: ")
                last_name = raw_input("Enter last name: ")
                pms = raw_input("Enter assessment ids to assign as project manager (comma delimited): ")
                tms = raw_input("Enter assessment ids to assign as team-member (comma delimited): ")
                rvs = raw_input("Enter assessment ids to assign as reviewer (comma delimited): ")
                send_welcome = raw_input("Send welcome email [Y or N] ? ")
            except KeyboardInterrupt:
                self.stdout.write("\nUser creation aborted.\n")
                return
        else:
            if len(args) != 7:
                raise CommandError("Invalid number of input arguments")
            email = args[0]
            first_name = args[1]
            last_name = args[2]
            pms = args[3]
            tms = args[4]
            rvs = args[5]
            send_welcome = args[6]

        HAWCUser.objects.create_user_batch(
            email=email,
            first_name=first_name,
            last_name=last_name,
            pms=get_assessment_ids(pms),
            tms=get_assessment_ids(tms),
            rvs=get_assessment_ids(rvs),
            welcome_email= (send_welcome.lower() == "y")
        )
