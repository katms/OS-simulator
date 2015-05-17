"""
Katherine Sullivan
OS hw #3

Done:
sys gen - prompt for total memory, max process size, page size
A - prompt for process size, error check
job pool
Snapshot - m,j, page table
paging
handle freeing memory when a process terminates
memstart address hex, logical -> physical
K# command
"""
from math import ceil


class PCB(object):
    _pid = 1
    # leaving these here for now but I might move alpha
    ALPHA = None
    DEFAULT_TAU = None

    HEADER = "\t".join(("PID", "Total", "Avg", "Size"))

    total_CPU_time = 0
    terminated = 0

    def __init__(self, size):
        self.id = str(PCB._pid)
        PCB._pid += 1

        self.tau = PCB.DEFAULT_TAU

        self.CPU_time = 0
        self._nbursts = 0

        # for CPU bursts that get preempted
        self._preempted = 0

        self.size = size
        self.table = []

    def end_burst(self):
        # burst time must be positive
        # if the process was never preempted then _preempted=0
        t = get_int("Actual CPU burst length: ", lambda b: b > 0) + self._preempted
        self.CPU_time += t
        self._nbursts += 1
        # reset preempted
        self._preempted = 0

        self.tau = PCB.ALPHA*t + (1-PCB.ALPHA)*self.tau

    @property
    def average_burst(self):
        return self.CPU_time/self._nbursts if self.CPU_time > 0 else 0.0

    def __str__(self):
        # make sure average fits in its column
        rounded = round(self.average_burst, 2)
        return "\t".join((self.id, str(self.CPU_time), str(rounded), str(self.size)))

    def terminate(self):
        # do not make this the destructor, it would get called for every process on Ctrl-C
        # because that's how destructors work you idiot
        self.end_burst()
        for label, item in zip(PCB.HEADER.split('\t'), str(self).split('\t')):
            print(label, item, sep=": ", end='\t')
        print()
        PCB.total_CPU_time += self.CPU_time
        PCB.terminated += 1

    def preempt(self):
        self._preempted = get_int("Running process preempted. Length of CPU burst thus far: ")

    @staticmethod
    def systems_average():
        return PCB.total_CPU_time/PCB.terminated if PCB.total_CPU_time > 0 else 0.0

    def __del__(self):
        self.kill()

    def __eq__(self, other):
        if type(other) == PCB:
            return self.id == other.id
        elif type(other) == int:
            return str(other) == self.id
        else:  # assume id is a string
            return other == self.id

    @property
    def pages(self):
        # print page table
        res = "   L   P\n"
        for i in range(len(self.table)):
            # logical, physical
            res += "   {} | {}\n".format(i, self.table[i].index)
        return res

    def lookup(self, address):
        size = self.table[0].size
        page_number = address//size
        offset = address%size
        return self.table[page_number].address(offset)

    def kill(self):
        # __del__ doesn't work on Devices and this is easier than fixing that
        for f in self.table:
            f.free()
        self.table.clear()


class Device_Queue():
    """Manages the process queue for a single device."""

    HEADER = "\t".join(("File", "Logc", "Phys", "R/W", "Length"))

    def __init__(self, name):
        # so far the name's only real purpose is in determining if this is a printer or a disk
        self.name = name
        self.queue = []

    def deque(self):
        if self.queue:
            return self.queue.pop(0)[0]
        else:
            return None

    def enqueue(self, process):
        self.queue.append(self.file_info(process))

    def file_info(self, process):
        # prompt for additional arguments
        filename = input("Filename: ")

        def is_hex(n):
            for d in n:
                if d not in "aAbBcCdDeEfF0123456789":
                    return False
            return True

        logical = verify_input("Logical memory address: ", lambda i: is_hex(i) and int(i,16) < process.size)
        dec = int(logical, 16)
        physical = process.lookup(int(logical,16))
        print("Physical address:",physical)

        # can only write to a printer
        if "p" in self.name:
            rw = "w"
        else:
            # make sure r/w is lowercase
            rw = letter_of("R/W: ", "rw")
        if rw == "w":
            length = verify_input("File length: ", lambda i: i.isdigit())
        else:
            length = "-"
        return process, filename, logical, physical, rw, length

    def __bool__(self):
        return bool(self.queue)

    def __str__(self):
        # empty device queues don't print
        if not self.queue:
            return ""
        # print every process in order, in columns

        res = ('-'*4)+self.name+'\n'
        for process in self.queue:
            item = aligned_string(process)
            res += item
        return res

    def remove(self, id):
        # assume pid exists in queue
        for i in range(len(self.queue)):
            if self.queue[i][0].id == id:
                self.queue[i][0].kill()
                del self.queue[i]
                return True


class Disk(Device_Queue):
    """Device queue that implements FSCAN"""
    def __init__(self, name):
        super().__init__(name)
        self.cylinders = get_int("Cylinders in disk #{}: ".format(self.name[1:]), lambda c: c > 0)

        # self.buffered_requests is ignored until self.queue is empty
        self.buffered_requests = []
        # start wherever
        self.head = 0

    def enqueue(self, process):
        # cylinders are numbered [0, cylinders)
        request = self.file_info(process)
        cylinders = get_int("Cylinder: ", lambda c: c < self.cylinders)
        self.buffered_requests.append(request + (cylinders,))

        if not self.queue:  # this is the very first request
            self._fscan()

    def deque(self):
        if self.queue:  # if disk is already seeking
            self.head = self.queue[0][-1]
            result = super().deque()
            if not self.queue:  # that was the last request
                # freeze buffered_requests
                self._fscan()
            return result

        else:  # assume both queues are empty
            return super().deque()

    def _fscan(self):
        """freeze queue and sort requests"""

        def get_cylinder(item):
            return item[-1]

        up = [x for x in self.buffered_requests if get_cylinder(x) >= self.head]
        down = [x for x in self.buffered_requests if get_cylinder(x) < self.head]
        up.sort(key=get_cylinder)
        down.sort(key=get_cylinder, reverse=True)
        self.queue = up + down
        self.buffered_requests = []

    def __bool__(self):
        # now that I've modified Disk to switch queue and b_r
        # whenever queue is empty, this is unnecessary
        # but I don't feel like proving it so this stays
        return super().__bool__() or bool(self.buffered_requests)

    def __str__(self):
        if not self:
            return super().__str__()
        res = ('-'*4)+self.name+'\t'+"#Cylinders: {}".format(self.cylinders)+'\n'

        if self.queue:
            res += "Seeking:\n"
            for p in self.queue:
                line = aligned_string(p)
                res += line

        if self.buffered_requests:
            res += "Buffered:\n"
            for b in self.buffered_requests:
                line = aligned_string(b)
                res += line
        return res

    def remove(self, id):
        if not super().remove(id):
            for i in range(len(self.buffered_requests)):
                if self.buffered_requests[i][0].id == id:
                    self.buffered_requests[i][0].kill()
                    del self.buffered_requests[i]
                    return True
        elif not self.queue:  # if Disk just killed the only request being serviced
            self._fscan()


# put in a class primarily because using globals was bothering me
class Device_Manager():
    """Manages all queues (including CPU queue[s]) by device type"""
    DEVICE_PREFIXES = "pdc"

    def __init__(self, printers, disks, cds):
        self.printers = {}
        self.disks = {}
        self.cds = {}

        # the front is considered the process in the CPU
        self.ready_queue = []

        self.job_pool = []

        self.pid_table = {}

        # device queues are mapped to integers to ensure they print in numerical order
        # that was important right
        for n in range(1, printers+1):
            self.printers[n] = Device_Queue('p'+str(n))

        for n in range(1, disks+1):
            self.disks[n] = Disk('d'+str(n))

        for n in range(1, cds+1):
            self.cds[n] = Device_Queue('c'+str(n))

        self.table = Page_Table()
        self.max_proc_size = self.table.max_proc_size

    def new_process(self):
        psize = get_int("Process size: ", lambda s: s > 0)
        if psize <= self.max_proc_size:
            new = PCB(psize)
            self.job_pool.append(new)
            self.pid_table[new.id] = self.job_pool
            self.dispatch_jobs()
        else:
            print("Rejected: Maximum process size is {}".format(self.max_proc_size))

    def dispatch_jobs(self):
        if not self.job_pool:
            return

        def largest_fit(p):
            if p.size/self.table.page_size <= self.table.free_pages:
                return p.size
            else:  # cannot fit
                return -1

        largest = max(self.job_pool, key=largest_fit)
        if largest.size/self.table.page_size <= self.table.free_pages:
            self.add_to_ready_queue(largest)
            self.table.allocate(largest)
            self.job_pool.remove(largest)
            # check again
            self.dispatch_jobs()

        else:  # no jobs can fit in memory
            return

    def terminate(self):
        # terminate current process
        if self.ready_queue:
            self.ready_queue.pop(0).terminate()
            self.dispatch_jobs()
        else:
            print("No processes running.")

    def get(self, name):
        # returns the named device or None
        # guaranteed: prefix is in "pdc"
        name = name.lower()
        prefix = name[0]
        index = int(name[1:])

        # so my IDE will stop warning me about this
        device_type = {}  # {}.get(k) -> None

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
        devices = {}
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
            option = letter_of("Select {}: ".format(", ".join(SNAPSHOT_OPTIONS)), SNAPSHOT_OPTIONS)

        output = ""
        header = ""

        def print_queue(queue):
            # print a list of only PCBs
            nonlocal header, output
        if option in 'rj':
            header = PCB.HEADER
            queue = self.ready_queue if option == 'r' else self.job_pool
            for process in queue:
                output += (str(process)+'\n')
                if option == 'r': # skip for job pool processes
                    output += process.pages
        elif 'm' == option:
            header = "N\tOwner"
            output = str(self.table)
        else:
            for device_queue in self.get_all(option):
                if device_queue:
                    output += str(device_queue)
            header = PCB.HEADER+'\t'+Device_Queue.HEADER
            if 'd' == option:
                header += "\t"+"Cyl"

        line_count = 0
        MAX_LINES = 23
        # only print MAX_LINES lines at a time, and reiterate the header
        for line in output.split("\n")[:-1]:  # skip the blank line that's always at the end
            if line_count == 0:
                print(header)
                line_count += 1
            print(line)
            line_count += 1
            if line_count >= MAX_LINES:
                input("Press enter for more")  # 24th line
                line_count = 0

        # shouldn't clash with the 24-line limit
        print("Total CPU time: ", PCB.total_CPU_time, "Systems average: ", PCB.systems_average())

    def add_to_ready_queue(self, pcb):
        self.pid_table[pcb.id] = self.ready_queue
        if self.ready_queue:
            CPU_process = self.ready_queue[0]
        else:
            CPU_process = None
        self.ready_queue.append(pcb)
        # preemptive sjf scheduling
        self.ready_queue.sort(key=lambda p: p.tau)
        if CPU_process is not None and CPU_process is not self.ready_queue[0]:
            CPU_process.preempt()

    def kill(self, id):
        if id in self.pid_table:
            dispatch = (self.pid_table[id] is self.ready_queue)
            self.pid_table[id].remove(id)
            self.pid_table.pop(id)
            if dispatch:
                self.dispatch_jobs()
            return id
        else:
            return None


class Page_Table():
    def __init__(self):
        def is_power2(n):
            power = 1
            while power <= n:
                if power == n:
                    return True
                power *= 2
            return False


        page_size = get_int("Page size: ", is_power2)
        self.page_size = page_size


        total = get_int("Total memory: ", lambda m: m > 0 and m%page_size==0)
        self.total_memory = total
        self.max_proc_size = get_int("Maximum process size: ", lambda s: 0 < s <= total)

        self.npages = self.total_memory//self.page_size

        def update_free_frame_list():
            # update free frame list
            self.free_frames = [f for f in self.frames if f.owner is None]

        class Frame():
            def __init__(self, index):
                self.owner = None
                self.index = index

            @property
            def size(self):
                return page_size

            def address(self, offset):
                # drop preceding '0x'
                return hex((self.size*self.index)+offset)[2:]

            def __str__(self):
                return str(self.index)+'\t'+str(self.owner)

            def free(self):
                self.owner = None
                update_free_frame_list()

        self.frames = [Frame(i) for i in range(self.npages)]
        self.free_frames = self.frames.copy()

    def allocate(self, process):
        needed = ceil(process.size/self.page_size)
        pages, self.free_frames = self.free_frames[:needed], self.free_frames[needed:]
        for p in pages:
            p.owner = process.id
        process.table = pages

    def __str__(self):
        res = ""
        for f in self.frames:
            res += str(f) + '\n'
        # free frame list
        res += "Free: "
        res += str([f.index for f in self.free_frames])
        res += '\n'
        return res

    @property
    def free_pages(self):
        return len(self.free_frames)


DEVICE_PREFIXES = Device_Manager.DEVICE_PREFIXES
SNAPSHOT_OPTIONS = "rjm"+DEVICE_PREFIXES


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


# moved back from get_type() to resolve a bug introduced by that function where it accepted negative numbers or -0
def get_int(message, additional=lambda n: True):
    return int(verify_input(message, lambda i: i.isdigit() and additional(int(i))))


def letter_of(prompt, master_string):
    """"Accepts a single character (case insensitive) from master string and automatically converts it to lowercase"""
    def letter(ch):
        return len(ch) == 1 and ch.lower() in master_string.lower()
    return verify_input(prompt, letter).lower()

# todo: tables
# print I/O requests exactly like this for both disks and other devices
def aligned_string(process):
    return '\t'.join(map(str, process)) + '\n' + process[0].pages

def main():

    # sys_gen
    manager = Device_Manager(get_int("Printers: "), get_int("Disks: "), get_int("CDs: "))
    COMMANDS = {'A': manager.new_process, 't': manager.terminate, 'S': manager.snapshot}

    # prevent any negative input, including '-0'
    def get_float(message, require=lambda f: True):
        def is_float(f):
            return f.replace('.', "").isdigit() and f.count('.') <= 1
        return float(verify_input(message, lambda f: is_float(f) and require(float(f))))

    PCB.ALPHA = get_float("History parameter (alpha): ", lambda a: 0 <= a <= 1)
    PCB.DEFAULT_TAU = get_float("Initial burst estimate: ")

    # running
    # one of the lengthier input verifiers, recognizes commands
    def is_command(command):
        if len(command) == 1 and command in COMMANDS:
            return True
        elif len(command) == 2 and (command[0] == 'S' and command[1] in SNAPSHOT_OPTIONS):
            # snapshot
            return True
        elif len(command) >= 2:
            if command[1:].isdigit():
                # device name
                # Kill
                return command[0].lower() in DEVICE_PREFIXES or 'K' == command[0]
            else:
                return False
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
            if signal[0] == "S":
                manager.snapshot(signal[1])

            elif "K" == signal[0]:
                if manager.kill(signal[1:]) is None:
                    print("PID {} not found".format(signal[1:]))

            else:
                # device interrupt
                device = manager.get(signal)
                if device is None:
                    print("No such device.")
                elif signal[0].isupper():
                    # device completion
                    if device:
                        manager.add_to_ready_queue(device.deque())
                    else:
                        print("Device queue is empty.")
                else:
                    # device request
                    if manager.ready_queue:
                        current_process = manager.ready_queue.pop(0)
                        current_process.end_burst()
                        manager.pid_table[current_process.id] = device
                        device.enqueue(current_process)
                    else:
                        print("No process in CPU.")

        else:  # signal in COMMANDS
            COMMANDS[signal]()

if __name__ == '__main__':
    main()
