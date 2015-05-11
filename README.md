# OS-simulator
**Version:** Python 3.4
- Manages processes, devices, I/O requests
- CPU scheduling (shortest job first)
  - tau(next) = alpha * time(previous_burst) + (1-alpha) * tau(previous)
- disk scheduling (FSCAN)
- CPU usage accounting
- Memory management (paging)

### Sys-gen phase
1. Enter the number of each type of device
  - Printers are named p1 .. pN
  - Disks are named d1 .. dN
    - specify the number of cylinders for each disk
  - CD/RWs are named c1 .. cN
2. Create the frame table:
  1. total size of memory
  2. maximum allowed size of a process
  3. frame size (must be a power of two and divide up all memory)
3. Input alpha (history parameter)
4. Input the default value of tau for all new processes

### Running phase
Commands:
- A - Creates a new process. It will be rejected if it is larger than the maximum size.
- t - terminte the currently CPU process
- x# - device request 
  - x = p|d|c
- X# - device signals I/O completion
- K# - kill pid #
- S[option] - snapshot() outputs contents of non-empty queues
  - r - print ready queue (and the page table for each process)
  - p, d, c - print queues for each of the given device type
    - p - printers
    - d - disks
    - c - cds  
  - m - print the frame table and free frame list
  - j - print processes waiting in job pool
  - if no option is given, snapshot() explicitly queries the user for one
