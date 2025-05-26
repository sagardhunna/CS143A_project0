### Fill in the following information before submitting
# Group id: 62
# Members: Sagar Dhunna, Quan Tran, Aarav Shah

from typing import Callable
from collections import deque
import heapq

# PID is just an integer, but it is used to make it clear when a integer is expected to be a valid PID.
PID = int

# This class represents the PCB of processes.
# It is only here for your convinience and can be modified however you see fit.
class PCB:
	pid: PID
	priority: int
	exiting: bool = False
	runtime: int = 0
	waiting: bool = False

	def __init__(self, pid: PID, priority: int=None):
		self.pid = pid
		self.priority = priority

	def __eq__(self, other):
		return self.pid == other.pid

	def __lt__(self, other):
		return self.pid < other.pid

# This class represents the Kernel of the simulation.
# The simulator will create an instance of this object and use it to respond to syscalls and interrupts.
# DO NOT modify the name of this class or remove it.
class Kernel:
	scheduling_algorithm: str
	logger: any
	ready_queue: any
	waiting_queues: dict[int, list[tuple[PID, PCB]]]
	idle_pcb: PCB
	running: PCB
	semaphores: dict[int, int]
	sem_key: Callable[[PCB], int]

	# Called before the simulation begins.
	# Use this method to initilize any variables you need throughout the simulation.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def __init__(self, scheduling_algorithm: str, logger):
		self.scheduling_algorithm = scheduling_algorithm
		if scheduling_algorithm == "FCFS" or scheduling_algorithm == "RR":
			self.ready_queue = deque()
			self.sem_key = lambda pcb: pcb.pid
		elif scheduling_algorithm == "Priority":
			self.ready_queue = []
			self.sem_key = lambda pcb: pcb.priority

		self.logger = logger
		self.waiting_queues = {}
		self.idle_pcb = PCB(0)
		self.running = self.idle_pcb
		self.semaphores = {}

	# This method is triggered every time a new process has arrived.
	# new_process is this process's PID.
	# priority is the priority of new_process.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def new_process_arrived(self, new_process: PID, priority: int, process_type: str) -> PID:
		self.ready_queue.append(PCB(new_process, priority)) # everytime a process arrives, add it to the right of our queue
		self.choose_next_process() # should do nothing for FCFS, because context switching only occurs on process exit

		return self.running.pid

	# This method is triggered every time the current process performs an exit syscall.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_exit(self) -> PID:
		self.running.exiting = True # sets current process to not be running
		self.choose_next_process() # select new process to run as current has completed
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
		if self.scheduling_algorithm == "FCFS":
			# if currently idle
			if not self.running.pid:
				if self.ready_queue:
					self.running = self.ready_queue.popleft()
					return
 
			# if currently waiting		
			if self.running.waiting:
				if self.ready_queue:
					self.running = self.ready_queue.popleft()
				else:
					self.running = self.idle_pcb
				return
   
			# if currently exiting
			if self.running.exiting:
				if self.ready_queue:
					self.running = self.ready_queue.popleft()
				else:
					self.running = self.idle_pcb
	 
		elif self.scheduling_algorithm == "Priority":
			if not self.running.pid: # first time adding a process, just need to pop whatever was latest to be inserted
				if self.ready_queue:
					self.running = self.ready_queue.pop(0)
					return
			elif self.running.exiting or self.running.waiting:
				# if we are exiting a process, we need to either switch to next in line process (should be sorted as we sort everytime a new process is inserted) or switch back to idle
				if self.ready_queue:
					# sort our array based on priority
					self.ready_queue.sort(key=lambda process: process.priority)
					self.running = self.ready_queue.pop(0)
				else:
					self.running = self.idle_pcb
			else:
				# sort our array based on priority
				self.ready_queue.sort(key=lambda process: process.priority)
				# compare current running process' priority, with priority or process at front of queue
				if self.ready_queue:
					curr_process = self.running
					next_process = self.ready_queue[0]
					if next_process.priority < curr_process.priority: # if next in line has a higher priority, we will switch context and add current to queue, otherwise do nothing
						self.running = self.ready_queue.pop(0) # pop front of queue
						self.ready_queue.append(curr_process) # add curr process back to queue because we are swapping context
						return
  
		elif self.scheduling_algorithm == "RR":
			# if currently idle
			if not self.running.pid:
				if self.ready_queue:
					self.running = self.ready_queue.popleft()
					return

			# if currently waiting		
			if self.running.waiting:
				if self.ready_queue:
					self.running = self.ready_queue.popleft()
				else:
					self.running = self.idle_pcb

			# if currently exiting
			if self.running.exiting:
				if self.ready_queue:
					self.running = self.ready_queue.popleft()
				else:
					self.running = self.idle_pcb
				return

			# elapsed time >= 40ms
			if self.running.runtime >= 40:
				self.ready_queue.append(self.running)
				self.running.runtime = 0
				self.running = self.ready_queue.popleft()
				return
		
					
	# This method is triggered when the currently running process requests to initialize a new semaphore.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_init_semaphore(self, semaphore_id: int, initial_value: int):
		self.semaphores[semaphore_id] = initial_value
		self.waiting_queues[semaphore_id] = []
		return
	
	# This method is triggered when the currently running process calls p() on an existing semaphore.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_semaphore_p(self, semaphore_id: int) -> PID:
		# might need to wait
		if self.semaphores[semaphore_id] <= 0:
			heapq.heappush(self.waiting_queues[semaphore_id], (self.sem_key(self.running), self.running))
			self.running.waiting = True
   
		# update semaphore value
		self.semaphores[semaphore_id] -= 1

		# might need context switch
		self.choose_next_process()
		return self.running.pid

	# This method is triggered when the currently running process calls v() on an existing semaphore.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_semaphore_v(self, semaphore_id: int) -> PID:
		# might need to wake up waiting process
		if self.waiting_queues[semaphore_id]:
			_, pcb = heapq.heappop(self.waiting_queues[semaphore_id])
			pcb.waiting = False
			self.ready_queue.append(pcb)
   
		# update semaphore value
		self.semaphores[semaphore_id] += 1
  
		# if priority, might need context switch
		if self.scheduling_algorithm == "Priority":
			self.choose_next_process()
		
		return self.running.pid

	# This method is triggered when the currently running process requests to initialize a new mutex.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_init_mutex(self, mutex_id: int):
		return

	# This method is triggered when the currently running process calls lock() on an existing mutex.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_mutex_lock(self, mutex_id: int) -> PID:
		return self.running.pid


	# This method is triggered when the currently running process calls unlock() on an existing mutex.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def syscall_mutex_unlock(self, mutex_id: int) -> PID:
		return self.running.pid

	# This function represents the hardware timer interrupt.
	# It is triggered every 10 microseconds and is the only way a kernel can track passing time.
	# Do not use real time to track how much time has passed as time is simulated.
	# DO NOT rename or delete this method. DO NOT change its arguments.
	def timer_interrupt(self) -> PID:
		# for debugging only
  		# self.logger.log("Timer interrupt")
		# self.logger.log(f"s0: {self.semaphores}")
		
		self.running.runtime += 10
		if self.scheduling_algorithm == "RR":
			self.choose_next_process()
   
		return self.running.pid