"""
Katherine Sullivan
OS hw #2

Todo:
disk scheduling algorithm
input history parameter alpha
PCB also has: tau, previous burst time,
at every interrupt, query timer
Snapshot prints out all of these things too

Mostly done, see todos:
input #cylinders for each disk
disk requests need a cylinder

"""

class Device_Queue():
    """Manages the process queue for a single device."""
    def __init__(self, name):
        # so far the name's only real purpose is in determining if this is a printer
        self.name = name
        self.queue = []

        if "d" in self.name:
            # todo: check with Schweitzer that there can't be zero cylinders
            self.cylinders = get_int("Cylinders in disk #{}: ".format(self.name[1:]), lambda c: c > 0)
        else:
            # I guess I don't actually need this, but consistency or something
            # also don't switch to using inheritance, think about how enqueue() would work if you did
            self.cylinders = 0

    def deque(self):
        if self.queue:
            return self.queue.pop(0)
        else:
            return None

    def enqueue(self, process):
        # prompt for additional arguments
        filename = input("Filename: ")
        memstart = verify_input("Starting memory address: ",lambda i: i.isdigit())
        # can only write to a printer
        if "p" in self.name:
            rw = "w"
        else:
            # make sure r/w is lowercase
            rw = verify_input("R/W: ", lambda i: i.lower() in "rw").lower()
        if rw == "w":
            length = verify_input("File length: ", lambda i: i.isdigit())
        else:
            length = "-"

        if 'd' in self.name:
            # todo: do we need to do anything with this information? or was I just supposed to ask for it
            # todo: also should the cylinders be numbered [0, cylinders) or [1, cylinders]
            cylinders = verify_input("Cylinder: ", lambda c: c.isdigit() and int(c) < self.cylinders)

        self.queue.append((process, filename, memstart, rw, length))

    def __bool__(self):
        return bool(self.queue)

    def __str__(self):
        # empty device queues don't print
        if not self.queue:
            return ""
        # print every process in order in columns

        # I'm just going to assume this is aligned with the header
        # because ensuring it would be really complicated
        # I tried
        # and then I noticed the same code aligns differently depending where I run it
        # and then I gave up
        # this combination of tabs works on at least three mediums, including eniac
        res = '-'+self.name+'-'
        if 'd' in self.name:
            # todo: again, does this go here or not
            res += "\tCylinders: {}\n".format(self.cylinders)
        else:
            res += '\n'
        for process in self.queue:
            line = "\t"+process[0]+"\t"+process[1]+"\t\t"+process[2]+"\t\t"+process[3]+"\t"+process[4]+'\n'
            res+=line
        return res


# put in a class primarily because using globals was bothering me
class Device_Manager():
    """
    Manages all queues (including CPU queue[s]) by device type
    """
    DEVICE_PREFIXES = "pdc"
    def __init__(self, printers, disks, cds):
        self.printers = {}
        self.disks = {}
        self.cds = {}

        # the front is considered the process in the CPU
        self.ready_queue = []

        # incrementing process ID
        self.pid=1

        # device queues are mapped to integers to ensure they print in numerical order
        # that was important right
        for n in range(1, printers+1):
            self.printers[n] = Device_Queue('p'+str(n))

        for n in range(1, disks+1):
            self.disks[n] = Device_Queue('d'+str(n))

        for n in range(1, cds+1):
            self.cds[n] = Device_Queue('c'+str(n))

    def new_process(self):
        # store pid as a string because so far
        # there's no reason I should have to do this later on whenever I use it
        self.ready_queue.append(str(self.pid))
        self.pid+=1

    def terminate(self):
        # terminate current process
        if self.ready_queue:
            self.ready_queue.pop(0)
        else:
            print("No processes running.")

    def get(self, name):
        # returns the named device or None
        # guaranteed: prefix is in "pdc"
        name = name.lower()
        prefix = name[0]
        index = int(name[1:])

        # so my IDE will stop warning me about this
        device_type = {} # {}.get(k) -> None

        if prefix == 'p':
            device_type = self.printers
        elif prefix == 'd':
            device_type = self.disks
        elif prefix == 'c':
            device_type = self.cds
        return device_type.get(index)

    def get_all(self, prefix):
        # guaranteed: prefix is in "pdc"
        # get all device queues of one type
        devices = ()
        if prefix == 'p':
            devices = self.printers
        elif prefix == 'd':
            devices = self.disks
        elif prefix == 'c':
            devices = self.cds
        return devices.values()

    def snapshot(self, option=None):
        """output all processes of some given set of queues"""

        if option is None:
            option = verify_input("Select r, p, d, c: ", lambda o: o in "rpdc")

        output=""
        if option == 'r':
            header = "\tPID"
            for process in self.ready_queue:
                output+=('\t'+process+'\n')
        else:

            for device_queue in self.get_all(option):
                if device_queue:
                    output+=str(device_queue)
            header = "\t".join(("\tPID", "Filename", "Memstart", "R/W", "File length"))

        line_count=0
        MAX_LINES = 23
        # only print MAX_LINES lines at a time, and reiterate the header
        for line in output.split("\n"):
            if line: # skip the blank line that's always at the end
                if line_count == 0:
                    print(header)
                    line_count+=1
                print(line)
                line_count+=1
                if line_count >= MAX_LINES:
                    input("Press enter for more")
                    line_count=0

DEVICE_PREFIXES = Device_Manager.DEVICE_PREFIXES
SNAPSHOT_OPTIONS = "r"+DEVICE_PREFIXES


# keep asking until the user provides acceptable input
def verify_input(prompt, is_correct, print_error=None):
    inp = input(prompt)
    if is_correct(inp):
        return inp
    else:
        # optional error message, can use input
        if print_error:
            # print_error is responsible for printing the message so I have the option to not print one based on inp
            print_error(inp)
        # ask again and return that result
        return verify_input(prompt, is_correct, print_error)

def get_int(message, additional=lambda n:True):
    # handles getting and parsing an integer
    # optional second test - evaluates an integer, not a string
    return int(verify_input(message, lambda n: n.isdigit() and additional(int(n))))



def main():

    # sys_gen
    manager = Device_Manager(get_int("Printers: "), get_int("Disks: "), get_int("CDs: "))
    COMMANDS = {'A': manager.new_process, 't': manager.terminate, 'S': manager.snapshot}

    # running
    # one of the lengthier input verifiers, recognizes commands
    def is_command(command):
        if len(command) == 1 and command in COMMANDS:
            return True
        elif len(command) == 2 and (command[0] == 'S' and command[1] in SNAPSHOT_OPTIONS):
            # snapshot
            return True
        elif len(command) >=2 and command[0].lower() in DEVICE_PREFIXES and command[1:].isdigit():
            # device name
            return True
        else:
            return False
    def unrecognized(command):
        # for printing an error message
        # skip this for blank input
        if command and not command.isspace():
            print("'"+command.strip()+"' is not a recognized command.")

    while True:
        signal = verify_input("", is_command, unrecognized)
        # if there are >=10 devices of a single type, the name could be at least 3 characters
        if len(signal) >= 2:
            # is_command only accepts two-char strings beginning S so it must be the right length
            if signal[0] == "S":
                manager.snapshot(signal[1])

            else:
                # device interrupt
                device = manager.get(signal)
                if device is None:
                    print("No such device.")
                elif signal[0].isupper():
                    # device completion
                    if device:
                        pcb = device.deque()[0]
                        manager.ready_queue.append(pcb)
                    else:
                        print("Device queue is empty.")
                else:
                    # device request
                    if manager.ready_queue:
                        device.enqueue(manager.ready_queue.pop(0))
                    else:
                        print("No process in CPU.")

        else: # signal in COMMANDS
            COMMANDS[signal]()

if __name__ == '__main__':
    main()
