""""""

"""
sys gen:
user specifies # of printer, disk, and CD/RW
only one CPU (for now)
"""

"""
running:
handle system calls and interrupts, indicated by keyboard input

check upper/lowercase

A
create a PCB (includes generating pid)


t
terminate, delete PCD for that process

[d]#
request the named device
prompt for parameters:
filename,
starting memory address (int),
"r" or "w" (if printer must be w),
if "w" how long the file is
enqueue this process's PCB to the device's queue

[D]#
named device signals completion of its current process, move it to the back of the ready queue


S
Snapshot
should be < 24 lines (one line per process?)

wait for option: r - ready, p - printers, d - disks, c - CD/RW queues

check samples



ERROR CHECKING (non-existent devices, terminate nonexistent process)
"""




"""
class OS:
    def __init__(self):
        # sys gen
        device_queues = {}
        printers = input("Number of printers: ")
        for p in range(0, printers):
            devices["p"+str(p+1)] = []

        disks = input("Number of disks: ")
        for d in range(0, disks):
            devices["d"+str(d+1)] = []

        cds = input("Number of CDs: ")
        for c in range(0, cds):
            devices["c"+str(c+1)] = []"""

"""
class Process:
    PID = 1
    def __init__(self):
        self.pid = Process.PID
        Process.PID+=1"""

"""
def sys_gen():
    # todo: get rid of global
    global devices
    # todo: check they're ints?
    printers = input("Number of printers: ")
    for p in range(0, printers):
        #devices["p"+p+1]
        devices.append("p"+str(p+1))

    disks = input("Number of disks: ")
    for d in range(0, disks):
        devices.append("d"+str(d+1))

    cds = input("Number of CDs: ")
    for c in range(0, cds):
        # todo: is it c? check notebook
        devices.append("c"+str(c+1))
"""

# todo: don't think this will ultimately be a list but if it's a dict not sure what the values would be
devices = list()

# as far as I know, this will be a list (FIFO)
ready_queue = list()

# I have no idea if this is what I need
CPU_process = None

pid = 0

# todo: unless this becomes init() take it out of the function
printers = input("Number of printers: ")
for p in range(0, printers):
    #devices["p"+p+1]
    devices.append("p"+str(p+1))

disks = input("Number of disks: ")
for d in range(0, disks):
    devices.append("d"+str(d+1))

cds = input("Number of CDs: ")
for c in range(0, cds):
    # todo: is it c? check notebook
    devices.append("c"+str(c+1))

def snapshot():
    pass
    """
    if queue == 'r':
        pass
    elif queue == 'p':
        pass
    elif queue == 'd' or queue == 'c':
        pass
    """

while True:
    signal = input()
    # todo: check if wrong format?
    if signal[0].isupper():
        # if no process in CPU handle that
        # device signal, PCB arrival, or snapshot
        if len(signal) > 1:
            pass
            # handle device completion
        elif signal == "A":
            # todo: use class instead of tuple? what about printers?
            ready_queue.append((pid,))
            pid+=1
            if CPU_process is None:
                CPU_process = ready_queue.pop(0)
        elif signal == "S":
            snapshot()

    else:
        # terminate CPU_process, or a device request
        if signal == 't':
            if CPU_process is None:
                pass
            else:
                CPU_process = None
                if ready_queue:
                    CPU_process = ready_queue.pop(0)
                    # assume CPU_process isn't held anywhere else
        else:
            pass

