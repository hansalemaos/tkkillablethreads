# Killable, non-blocking threads for tkinter 

## Tested against Windows / Python 3.11 / Anaconda

### Made for tkinter, but can be used without it too!

```py
from tkinter import *
from tkinter import messagebox
from tkkillablethreads import ExecuteAsThreadedTask
import time


def sleepprinter(*args, **kwargs):
    print(args, kwargs)
    for q in range(7):
        print("sleeping")
        time.sleep(1)
    messagebox.showinfo("Thread Ready", f"Results Ready - check: c.results ")
    return "bab"


top = Tk()
top.geometry("100x400")
c = ExecuteAsThreadedTask(fu=sleepprinter, args=("baba", "bbu"), kwargs={"oi": "badxx"})


def threadCallBack():
    c()
    messagebox.showinfo("Started Thread", str(c))


def threadCallBack2():
    c.killthread()
    messagebox.showinfo("Killed Thread", str(c))


B = Button(top, text="Start Thread", command=threadCallBack)
B.pack()
BCancel = Button(top, text="Cancel Thread", command=threadCallBack2)
BCancel.pack()
top.mainloop()
```