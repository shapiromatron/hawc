import sys

from django.core.management.base import BaseCommand

try:
    from granian import Granian
    from granian.constants import Interfaces

    GRANIAN_AVAILABLE = True
except ImportError:
    GRANIAN_AVAILABLE = False


class Command(BaseCommand):
    help = "Runs the web application using Granian"

    def add_arguments(self, parser):
        parser.add_argument(
            "--interface",
            default="wsgi",
            help="Application interface (wsgi or asgi)",
        )
        parser.add_argument(
            "--host",
            default="0.0.0.0",  # noqa: S104
            help="Host to bind to",
        )
        parser.add_argument(
            "--port",
            type=int,
            default=8000,
            help="Port to bind to",
        )
        parser.add_argument(
            "--workers",
            type=int,
            default=1,
            help="Number of worker processes",
        )
        parser.add_argument(
            "--blocking-threads",
            type=int,
            default=None,
            help="Number of blocking threads per worker",
        )
        parser.add_argument(
            "--log-level",
            default="info",
            help="Log level (critical, error, warning, info, debug)",
        )
        parser.add_argument(
            "--access-log",
            action="store_true",
            help="Enable access log",
        )
        parser.add_argument(
            "--respawn-failed-workers",
            action="store_true",
            help="Enable workers respawn on unexpected exit",
        )
        parser.add_argument(
            "--workers-lifetime",
            type=int,
            default=None,
            help="Maximum worker lifetime in seconds before respawn",
        )

    def handle(self, *args, **options):
        if not GRANIAN_AVAILABLE:
            self.stderr.write(
                self.style.ERROR("Granian is not installed. Install it with: pip install granian")
            )
            sys.exit(1)

        # Map interface string to Granian interface constant
        interface_map = {
            "wsgi": Interfaces.WSGI,
            "asgi": Interfaces.ASGI,
        }
        interface = interface_map.get(options["interface"], Interfaces.WSGI)

        # Create Granian server instance
        server = Granian(
            target="hawc.main.wsgi:application",
            address=options["host"],
            port=options["port"],
            interface=interface,
            workers=options["workers"],
            blocking_threads=options["blocking_threads"],
            log_level=options["log_level"],
            log_access=options["access_log"],
            respawn_failed_workers=options["respawn_failed_workers"],
            workers_lifetime=options["workers_lifetime"],
        )

        # Run the server
        server.serve()
