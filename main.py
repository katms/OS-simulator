"""
running:
handle system calls and interrupts, indicated by keyboard input

check upper/lowercase

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

def verify_input(prompt, is_correct, print_error=None):
    # repeat until the user provides acceptable input
    inp = input(prompt)
    if is_correct(inp):
        return inp
    else:
        # optional error message, can use input
        if print_error:
            print(print_error(inp))
        return verify_input(prompt, is_correct, print_error)

class Device_Queue():
    def __init__(self, name):
        self.name = name
        self.queue = []

    def deque(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

    def enqueue(self, process):
        filename = input("Filename: ")
        memstart = verify_input("Starting memory address: ",lambda i: i.isdigit())
        if "p" in self.name:
            rw = "w"
        else:
            rw = verify_input("R/W: ", lambda i: i.lower() in "rw").lower()
        length = verify_input("File length: ", lambda i: i.isdigit())

        self.queue.append((process, filename, memstart, rw, length))

    def __bool__(self):
        return bool(self.queue)

    def __str__(self):
        if not self.queue:
            return ""
        # todo: proper spacing, move header and count from there
        # todo: it pritns differently in Pycharm and out of it so maybe do something more complicated
        # todo: or switch from columns
        res = '-'+self.name+'-\n'
        for process in self.queue:
            line = "\t"+process[0]+"\t"+process[1]+"\t\t"+process[2]+"\t\t"+process[3]+"\t"+process[4]+'\n'
            #print(line)
            res+=line

            line = "\t".join(process)
            #res+='\t'+line+'\n'
        return res

    def test_str(self):
        line = ""


DEVICE_PREFIXES = "pdc"

class Device_Manager():
    def __init__(self, printers, disks, cds):
        self.printers = {}
        self.disks = {}
        self.cds = {}

        for n in range(1, printers+1):
            self.printers[n] = Device_Queue('p'+str(n))

        for n in range(1, disks+1):
            self.disks[n] = Device_Queue('d'+str(n))

        for n in range(1, cds+1):
            self.cds[n] = Device_Queue('c'+str(n))

    def get(self, name):
        # prefix is in "pdc"
        name = name.lower()
        prefix = name[0]
        index = int(name[1:])
        if prefix == 'p':
            device_type = self.printers
        elif prefix == 'd':
            device_type = self.disks
        elif prefix == 'c':
            device_type = self.cds
        return device_type.get(index)

    def get_all(self, prefix):
        # get all devices of one type
        if prefix == 'p':
            devices = self.printers
        elif prefix == 'd':
            devices = self.disks
        elif prefix == 'c':
            devices = self.cds
        return devices.values()




def is_command(command):
    SNAPSHOT_OPTIONS = "r"+DEVICE_PREFIXES
    COMMANDS = "At"

    if len(command) == 1 and command in COMMANDS:
        return True
    elif len(command) == 2 and (command[0] == 'S' and command[1] in SNAPSHOT_OPTIONS):
        # snapshot
        return True
    elif command[0].lower() in DEVICE_PREFIXES and command[1:].isdigit():
        # device name
        return True
    else:
        return False


ready_queue = []
pid=1


def snapshot(option):
    # todo: snapshot
    if option == 'r':
        print("PID")
        for process in ready_queue:
            print(process)
    else:
        header = []
        LENGTH = 10
        """for label in ("    PID", "Filename", "Memstart", "R/W", "File length"):
            spaces = ' '*(LENGTH-len(label))
            header.append(label+spaces)"""
        header = "\t".join(("\tPID", "Filename", "Memstart", "R/W", "File length"))
            #("\tPID", "Filename", "Memstart", "R/W", "File length")) #"PID \t Filename \t Memstart \t R/W \t File length"
        print(header)

        #print(manager.get_all(option))

        for device_queue in manager.get_all(option):
            #print(type(device_queue))
            # todo: 24 lines
            if device_queue:
                print(device_queue)

        """for device in filter(lambda k: option in k, devices):
            print(device)
            for process_info in devices[device].queue:
                print(process_info)"""


# sys gen
def get_int(message):
    return int(verify_input(message, lambda n: n.isdigit()))

manager = Device_Manager(get_int("Printers: "), get_int("Disks: "), get_int("CDs: "))

#running
while True:
    signal = verify_input("$ ", is_command, lambda c: "'"+c+"' is not a recognized command.")
    if len(signal) >= 2: # in case there are >=10 devices of a single type
        if signal[0] == "S":
            snapshot(signal[1])

        else:
            # device interrupt
            device = manager.get(signal)
            if device is None:
                print("No such device.")
            elif signal[0].isupper():
                # device completion
                if device:
                    pcb = device.deque()[0]
                    ready_queue.append(pcb)
                else:
                    print("Device queue is empty.")
            else:
                # device request
                if ready_queue:
                    device.enqueue(ready_queue.pop(0))
                else:
                    print("No process in CPU.")

    else:
        if signal == 't':
            # terminate current CPU process
            if ready_queue:
                ready_queue.pop(0)
            else:
                print("No processes running.")
        elif signal == 'A':
            # queue new process
            # store pid as a string because so far there's no reason I should have to do this later
            ready_queue.append(str(pid))
            pid+=1
