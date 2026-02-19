#!/usr/bin/env python3
import argparse
import os
import subprocess
from enum import StrEnum, auto


class Cmd(StrEnum):
    sync = auto()
    web = auto()
    sync_web = auto()
    cron = auto()
    workers = auto()


def run_manage(*args):
    subprocess.run(["manage", *args], check=True)  # noqa: S607


def run_web():
    os.execv(  # noqa: S606
        "/usr/local/bin/granian",
        [
            "granian",
            "--interface",
            "wsgi",
            "--host",
            "0.0.0.0",  # noqa: S104
            "--port",
            "5000",
            "--workers",
            "3",
            "--workers-lifetime",
            "3600",
            "--respawn-interval",
            "60",
            "--access-log",
            "--respawn-failed-workers",
            "hawc.main.wsgi:application",
        ],
    )


def run_sync():
    if os.environ.get("HAWC_LOAD_TEST_DB") == "1":
        run_manage("load_test_db")
    for cmd in [
        ("clear_cache",),
        ("clearsessions",),
        ("collectstatic", "--noinput"),
        ("migrate", "--noinput"),
        ("recreate_views",),
    ]:
        run_manage(*cmd)


def main():
    p = argparse.ArgumentParser(description="HAWC startup CLI")
    p.add_argument("cmd", choices=list(Cmd), help="action to run")
    a = p.parse_args()

    match a.cmd:
        case Cmd.cron:
            os.execv(  # noqa: S606
                "/usr/local/bin/celery",
                ["celery", "--app=hawc.main.celery", "beat", "--loglevel=INFO"],
            )
        case Cmd.workers:
            os.execv(  # noqa: S606
                "/usr/local/bin/celery",
                ["celery", "--app=hawc.main.celery", "worker", "--loglevel=INFO"],
            )
        case Cmd.web:
            run_web()
        case Cmd.sync:
            run_sync()
        case Cmd.sync_web:
            run_sync()
            run_web()


if __name__ == "__main__":
    main()
