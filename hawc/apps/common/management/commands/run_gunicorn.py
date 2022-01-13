import sys

from django.core.management.base import BaseCommand
from gunicorn.app.base import BaseApplication

from .....main.wsgi import application


class DjangoApplication(BaseApplication):
    # https://github.com/CtrlC-Root/proto-aws-django/blob/master/
    #   pkg/frontdesk/production/management/commands/run_web.py
    def load_config(self):
        pass

    def add_arguments(self, parser):
        keys = sorted(self.cfg.settings, key=self.cfg.settings.__getitem__)
        keys.remove("pythonpath")  # conflicts with django; has same behavior
        for key in keys:
            self.cfg.settings[key].add_option(parser)

    def load(self):
        return application

    def load_config_from_args(self, args):
        for key, value in args.items():
            if key in self.cfg.settings and value:
                self.cfg.set(key.lower(), value)


class Command(BaseCommand):
    help = "Runs the web application using Gunicorn"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._app = DjangoApplication()

    def add_arguments(self, parser):
        self._app.add_arguments(parser)

    def handle(self, *args, **options):
        self._app.load_config_from_args(options)
        sys.exit(self._app.run())
