import logging
from subprocess import Popen
import threading


class run_process(threading.Thread):
    """
    Run process with the ability to automatically terminate a process given a
    specified time interval, in seconds. Modified slightly from this post:
    http://stackoverflow/questions/4158502

    Two input arguments:
        - cmd, the command to execute in subprocess, as a list
        - timeout, the maximum length of time to execute, in seconds

    Example call:
        - run_process(["./foo", "arg1"], 60).Run()
    """
    def __init__(self, cmd, timeout):
        threading.Thread.__init__(self)
        self.cmd = cmd
        self.timeout = timeout

    def run(self):
        self.p = Popen(self.cmd)
        self.p.wait()

    def Run(self):
        self.start()
        self.join(self.timeout)

        if self.is_alive():
            logging.warning("Executable killed for exceeding timeout: %s" %
                            ' '.join(self.cmd))
            self.p.terminate()
            self.join()
