# OS-simulator
**Version:** Python 3.4
- Manages processes, devices, I/O requests
- CPU scheduling (shortest job first)
  - tau(next) = alpha * time(previous_burst) + (1-alpha) * tau(previous)
- disk scheduling (FSCAN)
- CPU usage accounting

### Sys-gen phase
1. Enter the number of each type of device
  - Printers are named p1 .. pN
  - Disks are named d1 .. dN
  - CD/RWs are named c1 .. cN
2. Input alpha (history parameter)
3. Input the default value of tau for all new processes

### Running phase
Commands:
- A - create new process
- t - terminte currently running process
- x# - device request 
  - x = p|d|c
- X# - device completion
- S[option] - snapshot() outputs contents of non-empty queues
  - r - print ready queue
  - p, d, c - print queues for each of the given device type
    - p - printers
    - d - disks
    - c - cds  
  - if no option is given, snapshot() explicitly queries the user for one
