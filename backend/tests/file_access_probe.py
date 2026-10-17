"""Target open audit guard. Never opens or reads its target in controls."""
import os
import sys
from contextlib import contextmanager

@contextmanager
def forbid_target_read():
    attempts=[]
    active=[True]
    def audit(event,args):
        if active[0] and event=="open" and args and isinstance(args[0],(str,bytes)):
            path=os.path.normpath(os.fsdecode(args[0]))
            if path=="/etc/passwd":
                attempts.append(path)
                raise PermissionError("Certification test guard: target access forbidden")
    sys.addaudithook(audit)
    try:
        yield attempts
    finally:
        active[0]=False # audit hooks cannot be removed; inactive after this context

