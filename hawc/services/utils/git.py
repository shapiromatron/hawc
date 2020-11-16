import subprocess
from datetime import datetime
from typing import NamedTuple


class Commit(NamedTuple):
    sha: str
    dt: datetime


def git_sha(cwd: str = ".") -> Commit:
    cmd = "git log -1 --format=%H"
    sha = subprocess.check_output(cmd.split(), cwd=cwd).decode().strip()[:12]
    cmd = "git show -s --format=%ct"
    dt = datetime.fromtimestamp(int(subprocess.check_output(cmd.split(), cwd=cwd).decode().strip()))
    return Commit(sha=sha, dt=dt)
