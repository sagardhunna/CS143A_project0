### Fill in the following information before submitting
# Group id: 62
# Members: Sagar Dhunna, Quan Tran, Aarav Shah



from collections import deque

# PID is just an integer, but it is used to make it clear when a integer is expected to be a valid PID.
PID = int

# This class represents the PCB of processes.
# It is only here for your convinience and can be modified however you see fit.
class PCB:
    pid: PID
    priority: int
    exiting: bool = False

    def __init__(self, pid: PID, priority: int=None):

        self.pid = pid
        self.priority = priority

# This class represents the Kernel of the simulation.
# The simulator will create an instance of this object and use it to respond to syscalls and interrupts.
# DO NOT modify the name of this class or remove it.
class Kernel:
    scheduling_algorithm: str
    ready_queue: deque[PCB]
    waiting_queue: deque[PCB]
    running: PCB
    idle_pcb: PCB

    # Called before the simulation begins.
    # Use this method to initilize any variables you need throughout the simulation.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def __init__(self, scheduling_algorithm: str):
        self.scheduling_algorithm = scheduling_algorithm
        self.ready_queue = deque() # should be a heap for priority scheduling
        self.waiting_queue = deque()
        self.idle_pcb = PCB(0)
        self.running = self.idle_pcb

    # This method is triggered every time a new process has arrived.
    # new_process is this process's PID.
    # priority is the priority of new_process.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def new_process_arrived(self, new_process: PID, priority: int) -> PID:
        self.ready_queue.append(PCB(new_process, priority))
        self.choose_next_process() # should do nothing for FCFS, because context switching only occurs on process exit

        return self.running.pid

    # This method is triggered every time the current process performs an exit syscall.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_exit(self) -> PID:
        self.running.exiting = True
        self.choose_next_process()
        return self.running.pid

    # This method is triggered when the currently running process requests to change its priority.
    # DO NOT rename or delete this method. DO NOT change its arguments.
    def syscall_set_priority(self, new_priority: int) -> PID:
        self.running.priority = new_priority

        self.choose_next_process()
        return self.running.pid


    # This is where you can select the next process to run.
    # This method is not directly called by the simulator and is purely for your convinience.
    # Feel free to modify this method as you see fit.
    # It is not required to actually use this method but it is recommended.
    def choose_next_process(self):
        # if len(self.ready_queue) == 0:
        #         self.running = self.idle_pcb
        #         return
        
        # if no jobs are ready, continue running the same process
        # if not self.ready_queue: return
        
        if self.scheduling_algorithm == "FCFS":
            # if currently idle
            if not self.running.pid:
                if self.ready_queue:
                    self.running = self.ready_queue.popleft()
                    return
                
            # if currently exiting
            if self.running.exiting:
                if self.ready_queue:
                    self.running = self.ready_queue.popleft()
                else:
                    self.running = self.idle_pcb
        elif self.scheduling_algorithm == "Priority":
            self.running = self.idle_pcb