from pprint import pformat
import ctypes
import sys
import threading


def killthread(threadobject):
    # based on https://pypi.org/project/kthread/
    if not threadobject.is_alive():
        return True
    tid = -1
    for tid1, tobj in threading._active.items():
        if tobj is threadobject:
            tid = tid1
            break
    if tid == -1:
        sys.stderr.write(f"{threadobject} not found")
        return False
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
        ctypes.c_long(tid), ctypes.py_object(SystemExit)
    )
    if res == 0:
        return False
    elif res != 1:
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, 0)
        return False
    return True


class ExecuteAsThreadedTask:
    def __init__(
        self, fu=None, args=(), kwargs=None, daemon=True, clean_old_threads=True
    ):
        self.fu = fu
        self.args = args
        self.kwargs = kwargs
        if not self.kwargs:
            self.kwargs = {}
        self.ta = None
        self.results = {
            "running": [False],
            "returnvalue": [],
            "exception": [],
        }
        self.newargs = ()
        self.newkwargs = {}
        self.daemon = daemon
        self.clean_old_threads = clean_old_threads

    def __str__(self):
        return pformat(self.results)

    def __repr__(self):
        return self.__str__()

    def __call__(self, *args, **kwargs):
        self.newargs = self.args + args
        self.newkwargs = self.kwargs.copy()
        self.newkwargs.update(kwargs)
        try:
            if self.results["running"][0]:
                sys.stderr.write("Thread is already running")
                sys.stderr.flush()
                return False
            else:
                if self.clean_old_threads:
                    self.results["exception"].clear()
                    self.results["returnvalue"].clear()
            self.ta = ThreadedTaskSimpleNotQueue(
                fu=self.fu,
                results=self.results,
                args=self.newargs,
                kwargs=self.newkwargs,
            )
            self.ta.daemon = self.daemon
            self.results["running"].append(True)
            self.results["running"].pop(0)
            self.ta.start()
            return True

        except Exception as e:
            try:
                self.killthread()

                self.results["exception"].append(e)
            except Exception:
                pass

    def killthread(self):
        running = not killthread(self.ta)
        self.results["running"].append(running)
        self.results["running"].pop(0)


class ThreadedTaskSimpleNotQueue(threading.Thread):
    def __init__(self, fu=None, results=None, args=(), kwargs=None):
        super().__init__()
        self.fu = fu
        self.args = args
        self.kwargs = kwargs
        if not self.kwargs:
            self.kwargs = {}
        self.results = results

    def run(self):
        try:
            result = self.fu(*self.args, **self.kwargs)
            self.results["returnvalue"].append(result)
        except Exception as e:
            self.results["exception"].append(e)
        self.results["running"].append(False)
        self.results["running"].pop(0)
