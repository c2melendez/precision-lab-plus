"""Shared Python audit guard. Controls emit events, never launch processes."""
import sys
from contextlib import contextmanager

LAUNCH_EVENTS=("subprocess.Popen","os.system","os.posix_spawn","os.exec","os.spawn","os.fork","pty.spawn")
@contextmanager
def forbid_process_launch():
    attempts=[]
    active=[True]
    def audit(event,args):
        if active[0] and event in LAUNCH_EVENTS:
            attempts.append(event)
            raise PermissionError("Certification test guard: process launch forbidden")
    sys.addaudithook(audit)
    try:
        yield attempts
    finally:
        active[0]=False

