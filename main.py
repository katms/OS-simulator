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

def correct_input(prompt, is_correct):
    inp = input(prompt)
    if is_correct(inp):
        return inp
    else:
        return correct_input(prompt, is_correct)

class Device_Queue():
    def __init__(self, name):
        self.name = name
        self.queue = []

    def dequeue(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

    def enqueue(self, process):
        filename = input("Filename: ")
        memstart = correct_input("Memstart: ",lambda i: i.isdigit())
        if "p" in self.name:
            rw = "w"
        else:
            rw = correct_input("R/W: ", lambda i: i.lower in "rw")
        length = correct_input("File length: ", lambda i: i.isdigit())

        self.queue.append((process, filename, memstart, rw, length))


DEVICE_PREFIXES = "pdc"
def is_command(command):
    SNAPSHOT_OPTIONS = "r"+DEVICE_PREFIXES
    COMMANDS = "At"

    #signal = input("$ ")
    # todo: why is this only printing every other string? I think it's skipping some, too
    #print(signal)

    if len(command) == 1 and command in COMMANDS:
        return True

    elif len(command) == 2 and ((command[0] == 'S' and command[1] in SNAPSHOT_OPTIONS)
                           or (command[0].lower() in DEVICE_PREFIXES and command[1].isdigit())):
        return True

    else:
        return False


ready_queue = []
device_queues = {"p": None, "d": None, "c": None, "r": ready_queue}
pid=1


def get_device(device_name):
    pass

def snapshot(option):
    """if option == 'r':
        header = "PID"
        print(header)
        for process in ready_queue:
            print(process)
    # since I don't have the means to add them yet...
    else:
        header = "PID \t Filename \t Memstart \t R/W \t File length"
        print(header)
        devices = device_queues[option]
        for device in devices:
            if devices[device]:
                for process in devices[device]:
                    for info in process:
                        print(info)"""
    for t in device_queues:
        print(t, device_queues[t])

# sys gen

def add_devices(prefix, count):
    devices = {}
    for n in range(1, count+1):
        name = prefix+str(n)
        devices[name] = []
    device_queues[prefix] = devices

def get_int(message):
    return int(correct_input(message, lambda n: n.isdigit()))

printers = get_int("Printers: ")
disks = get_int("Disks: ")
cds = get_int("CDs: ")

for name, number in zip(DEVICE_PREFIXES, (printers, disks, cds)):
    add_devices(name, number)


#running
while True:
    signal = correct_input("$ ", is_command)
    if len(signal) == 2:
        if signal[0] == "S":
            print("Snapshot", signal[1])
            snapshot(signal[1])

        else:
            device = get_device(signal)
            if signal[0].isupper():
                print(signal, "completed")
            else:
                print("Request", signal)

    else:
        if signal == 't':
            if ready_queue:
                ready_queue.pop(0)
            else:
                print("No processes running.")
        elif signal == 'A':
            print("New process")
            ready_queue.append(pid)
            pid+=1
        """elif signal == 'S':
            print("Snapshot()")"""
