#!/usr/bin/env python3
# ruff: noqa: T201, S606, S104
import argparse
import os
import subprocess
from enum import StrEnum, auto


class Cmd(StrEnum):
    cron = auto()
    sync = auto()
    web = auto()
    worker = auto()
    sync_web = auto()


def run_manage(*args):
    subprocess.run(["/app/.venv/bin/manage", *args], check=True)


def sync():
    if os.environ.get("HAWC_LOAD_TEST_DB") == "1":
        run_manage("load_test_db")
    for cmd in [
        ("collectstatic", "--noinput"),
        ("migrate", "--noinput"),
        ("recreate_views",),
        ("clear_cache",),
    ]:
        print(f"Running: {cmd[0]}")
        run_manage(*cmd)
    print("Sync complete!")


def web():
    os.execv(
        "/app/.venv/bin/granian",
        [
            "granian",
            "--interface",
            "wsgi",
            "--host",
            "0.0.0.0",
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


def cron():
    os.execv(
        "/app/.venv/bin/celery",
        ["celery", "--app=hawc.main.celery", "beat", "--loglevel=INFO"],
    )


def worker():
    os.execv(
        "/app/.venv/bin/celery",
        ["celery", "--app=hawc.main.celery", "worker", "--loglevel=INFO"],
    )


def main():
    p = argparse.ArgumentParser(description="HAWC startup CLI")
    p.add_argument("cmd", choices=list(Cmd), help="action to run")
    a = p.parse_args()

    match a.cmd:
        case Cmd.cron:
            cron()
        case Cmd.worker:
            worker()
        case Cmd.web:
            web()
        case Cmd.sync:
            sync()
        case Cmd.sync_web:
            sync()
            web()


if __name__ == "__main__":
    main()
