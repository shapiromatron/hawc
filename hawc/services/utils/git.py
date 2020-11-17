import subprocess
from datetime import datetime

from pydantic import BaseModel


class Commit(BaseModel):
    sha: str
    dt: datetime

    @classmethod
    def current(cls, cwd: str = ".") -> "Commit":
        """Return information on the last commit at the repository path desired.

        Returns:
            A Commit instance
        """
        cmd = "git log -1 --format=%H"
        sha = subprocess.check_output(cmd.split(), cwd=cwd).decode().strip()[:12]
        cmd = "git show -s --format=%ct"
        dt = datetime.fromtimestamp(
            int(subprocess.check_output(cmd.split(), cwd=cwd).decode().strip())
        )
        return cls(sha=sha, dt=dt)
