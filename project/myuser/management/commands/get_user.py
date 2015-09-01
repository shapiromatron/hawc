from importlib import import_module

from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model


HELP_TEXT = """Given a session ID, attempt to get user name and email."""


class Command(BaseCommand):
    help = HELP_TEXT

    def add_arguments(self, parser):
        parser.add_argument('session_id', help='session-id')

    def handle(self, *args, **options):
        session_id = options.get('session_id')
        engine = import_module(settings.SESSION_ENGINE)
        SessionStore = engine.SessionStore
        session = SessionStore(session_id)
        user_id = session.get('_auth_user_id')
        User = get_user_model()
        if user_id:
            user = User.objects.get(pk=session.get('_auth_user_id'))
            print "Session found!"
            print "Full name: {}".format(user.get_full_name())
            print "Email: {}".format(user.email)
        else:
            print 'Session not found; used session-id "{}"'.format(session_id)
