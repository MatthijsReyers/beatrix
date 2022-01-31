from threading import Thread, Lock
from objectrecognition import RecognizedObject
from lib.locations import INPUT_AREA_CAM_VIEW, PUZZLE_AREA_CAM_VIEW, PUZZLE_LOCATIONS, INPUT_AREA_GRAB_CENTER
from lib.shapes import Shape
from enum import Enum
import time

class AutoPilotState(Enum):
    STOPPING = 1
    STOPPED  = 2
    STARTING = 3
    STARTED  = 4

class AutoPilot:
    def __init__(self, server: 'DebugServer', controller: 'Controller', camera: 'Camera'):
        self.controller = controller
        self.camera = camera
        self.server = server

        self.state = AutoPilotState.STOPPED
        self._state_mutex = Lock()

        self._pilot_thread = None

    def is_running(self):
        """ Checks if the autopilot is currently running. (May block if the autopilot thread is just 
        being started). """
        self._state_mutex.acquire()
        running = (self.state == AutoPilotState.STARTED or self.state == AutoPilotState.STARTING)
        self._state_mutex.release()
        return running

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
        self.server.send_update(autopilot_state=str(state))
        print('[A] Setting autopilot to:', state)

    def __pilot_thread(self):
        self._state_mutex.acquire()
        self.__set_state(AutoPilotState.STARTED)
        self._state_mutex.release()

        while self.is_running():
            obj = self.__identify_object()
            if not self.is_running(): break

            time.sleep(4)
            if not self.is_running(): break

            self.__pickup_object(obj)
            if not self.is_running(): break

            time.sleep(4)
            if not self.is_running(): break

            self.__move_object(obj.label)
            if not self.is_running(): break

            time.sleep(4)
            if not self.is_running(): break

            self.__place_down_object(obj.label)
            if not self.is_running(): break

            time.sleep(4)
            if not self.is_running(): break

    def __identify_object(self) -> RecognizedObject:
        self.controller.go_to_location(location=INPUT_AREA_CAM_VIEW)
        result = None
        while (result is None):
            result = self.controller.classify_current_view()
            time.sleep(0.5)
        return result

    def __pickup_object(self, obj: RecognizedObject):
        print('[@] Picking up', obj.label, 'object')
        # TODO: Actually use RecognizedObject for grab location.
        self.controller.hover_above_location(INPUT_AREA_GRAB_CENTER)
        if not self.is_running(): return
        self.controller.go_to_location(INPUT_AREA_GRAB_CENTER)
        self.controller.robotarm.set_grabber(closed=True)

    def __move_object(self, shape: Shape):
        print('[@] Moving object')
        self.controller.hover_above_location(PUZZLE_LOCATIONS[shape])

    def __place_down_object(self, shape: Shape):
        print('[@] Placing down object')
        self.controller.go_to_location(PUZZLE_LOCATIONS[shape])
        self.controller.robotarm.set_grabber(closed=False)