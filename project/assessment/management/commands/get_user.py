from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from myuser.models import HAWCUser


HELP_TEXT = """Given a session ID, attempt to get user name and email."""


class Command(BaseCommand):
    args = ''
    help = HELP_TEXT

    def handle(self, *args, **options):
        if len(args) != 1:
            raise CommandError("Requires a session-id from cookies")

        session_id = args[0]
        engine = import_module(settings.SESSION_ENGINE)
        SessionStore = engine.SessionStore
        session = SessionStore(session_id)
        user_id = session.get('_auth_user_id')
        if user_id:
            user = HAWCUser.objects.get(pk=session.get('_auth_user_id'))
            print "Session found!"
            print "Full name: {}".format(user.get_full_name())
            print "Email: {}".format(user.email)
        else:
            print 'Session not found; used session-id "{}"'.format(session_id)
