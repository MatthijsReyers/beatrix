from threading import Thread, Lock
from controller import Controller
from objectrecognition import Label
import enum

class AutoPilotState(enum):
    STOPPING = 1
    STOPPED  = 2
    STARTING = 3
    STARTED  = 4

class AutoPilot:
    def __init__(self, controller: Controller):
        self.controller = controller

        self.state = AutoPilotState.STOPPED
        self._state_mutex = Lock()

        self.currently_holding: Label = None
        self._pilot_thread = None

    def start(self):
        self._state_mutex.acquire()
        # CHECK: Is the thread already running/still alive?
        if self._pilot_thread and self._pilot_thread.is_alive():
            self.__set_state(AutoPilotState.STOPPING)
            if self._pilot_thread:
                self._pilot_thread.join()
            self.__set_state(AutoPilotState.STOPPED)
        self.__set_state(AutoPilotState.STARTING)
        self._pilot_thread = Thread(
            target=self.__pilot_thread,
            args=(),
            daemon=True)
        self._pilot_thread.start()
        self._state_mutex.release()

    def stop(self):
        self._state_mutex.acquire()
        self.__set_state(AutoPilotState.STOPPING)
        if self._pilot_thread:
            self._pilot_thread.join()
        self.__set_state(AutoPilotState.STOPPED)
        self._state_mutex.release()

    def __set_state(self, state: AutoPilotState):
        """" Updates the Autopilot state. Note that this method does NOT acquire the state mutex and 
        should NOT be called without acquiring it first! Use this method in favour of modifying the state
        directly to log autopilot state to clients/terminal. """
        self.state = state
        print('[A] Setting autopilot to:', state)

    def __pilot_thread(self):
        # Update autopilot state.
        self._state_mutex.acquire()
        self.__set_state(AutoPilotState.STARTED)
        self._state_mutex.release()
        
        while self.state == AutoPilotState.STARTED:
            self.controller