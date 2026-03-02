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


def _run_cmd(text: str):
    cmd, args = text.split(" ", 1)
    os.execv(cmd, args.split())  # noqa: S606


def run_cron():
    _run_cmd("/usr/local/bin/celery celery --app=hawc.main.celery beat--loglevel=INFO")


def run_worker():
    _run_cmd("/usr/local/bin/celery celery --app=hawc.main.celery worker --loglevel=INFO")


def run_web():
    _run_cmd(
        "/usr/local/bin/granian granian --interface wsgi --host 0.0.0.0 --port 5000 --workers 3 --workers-lifetime 3600 --respawn-interval 60 --access-log --respawn-failed-workers hawc.main.wsgi:application"
    )


def run_sync():
    cmds = [
        ("clear_cache",),
        ("clearsessions",),
        ("collectstatic", "--noinput"),
        ("migrate", "--noinput"),
        ("recreate_views",),
    ]
    if os.environ.get("HAWC_LOAD_TEST_DB") == "1":
        cmds.insert(0, ("load_test_db",))
    for cmd in cmds:
        subprocess.run(["/usr/local/bin/manage", *cmd], check=True)


def main():
    p = argparse.ArgumentParser(description="HAWC startup CLI")
    p.add_argument("cmd", choices=list(Cmd), help="action to run")
    a = p.parse_args()

    match a.cmd:
        case Cmd.cron:
            run_cron()
        case Cmd.workers:
            run_worker()
        case Cmd.web:
            run_web()
        case Cmd.sync:
            run_sync()
        case Cmd.sync_web:
            run_sync()
            run_web()


if __name__ == "__main__":
    main()
