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

check sample output



ERROR CHECKING (non-existent devices, terminate nonexistent process)
"""

DEVICE_PREFIXES = "cdp"
SNAPSHOT_OPTIONS = "r"+DEVICE_PREFIXES
COMMANDS = "ASt"

def get_device(device):
    pass

def snapshot(option=None):
    pass

def prompt():
    signal = input("$ ")

    if len(signal) == 1 and signal in COMMANDS:
        return signal

    elif len(signal) == 2 and (signal[0] == 'S' and signal[1] in SNAPSHOT_OPTIONS) \
                            or (signal[0].lower() in "cdp" and signal[1].isdigit()):
        return signal

    else:
        return prompt()

while True:
    signal = prompt()
    if len(signal) == 2:
        if signal[0] == "S":
            print("Snapshot", signal[1])

        else:
            if signal[0].isupper():
                print(signal, "completed")
            else:
                print("Request", signal)

    else:
        if signal == 't':
            print("Terminating")
        elif signal == 'A':
            print("New process")
        elif signal == 'S':
            print("Snapshot()")
