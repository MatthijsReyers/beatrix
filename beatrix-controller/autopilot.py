from lib.locations import INPUT_AREA_CAM_VIEW, PUZZLE_LOCATIONS, HOVER_ABOVE_PUZZLES, HOVER_ABOVE_INPUT
from lib.shapes import Shape
from lib.constants import BASE_JOINT_ID
from lib.transform import camera_to_board, board_to_world
from lib.kinematics import WristOrientation
from objectrecognition import RecognizedObject
from threading import Thread, Lock
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
        """ Checks if the autopilot is currently running. (Needs to acquire the state mutex and so may 
        block for a few ms if the autopilot thread is just being started/stopped). """
        self._state_mutex.acquire()
        running = (self.state == AutoPilotState.STARTED or self.state == AutoPilotState.STARTING)
        self._state_mutex.release()
        return running

    def start(self):
        """ Starts the autopilot thread and sets the autopilot state to STARTING. Will stop and restart
        the autopilot if it is already running. """
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
        """ Stops the autopilot thread and blocks until the autopilot state has been set to STOPPED. """
        if self.is_running():
            self._state_mutex.acquire()
            self.__set_state(AutoPilotState.STOPPING)
            self._state_mutex.release()
            if self._pilot_thread:
                self._pilot_thread.join()
            self._state_mutex.acquire()
            self.__set_state(AutoPilotState.STOPPED)
            self._state_mutex.release()

    def __set_state(self, state: AutoPilotState):
        """" Updates the Autopilot state. Note that this method does NOT acquire the state mutex and 
        should NOT be called without acquiring it first! Use this method in favour of modifying the state
        directly to log autopilot state to clients/terminal. """
        self.state = state
        self.server.send_update(autopilot_state=str(state))
        print('[@] Setting autopilot to:', state)

    def __pilot_thread(self):
        """ Main control loop that determines the order of actions that should be performed

        """
        self._state_mutex.acquire()
        self.__set_state(AutoPilotState.STARTED)
        self._state_mutex.release()

        while self.is_running():
            obj = self.__identify_object()
            if not self.is_running(): break

            self.__pickup_object(obj)
            if not self.is_running(): break

            time.sleep(1)
            if not self.is_running(): break

            self.__move_object(obj.label)
            if not self.is_running(): break

            self.__place_down_object(obj.label)
            if not self.is_running(): break

    def __identify_object(self) -> RecognizedObject:
        """
        Accesses the camera through the controller and does so until a valid object is recognised
        Returns: object that was recognised and should be picked up

        """
        location_offset_angles = INPUT_AREA_CAM_VIEW.get_angle_dict()
        location_offset_angles[BASE_JOINT_ID] = location_offset_angles[BASE_JOINT_ID] - 10
        self.controller.robotarm.set_arm(location_offset_angles)
        self.controller.go_to_location(location=INPUT_AREA_CAM_VIEW)
        time.sleep(2)
        result = None
        while (result is None and self.is_running()):
            print('[@] Identifying object')
            result = self.controller.classify_current_view()
            time.sleep(0.5)
        return result

    def __pickup_object(self, obj: RecognizedObject):
        """
        Determines the 3d location of the object to be picked up, moves the arm towards the object,
        and closes grabber

        Args: obj: object to be picked up
        """
        print('[@] Picking up', obj.label, 'object')

        location = camera_to_board(obj.center)
        print('[@] I wanna go to: ', location)

        location = board_to_world(location)
        adjusted_location = (location[0], location[1], location[2] - 2)
        location = adjusted_location
        if not self.is_running(): return

        self.controller.hover_above_coordinates(location, wrist_orientation=WristOrientation.VERTICAL)

        if not self.is_running(): return
        self.controller._move_arm_to_workspace_coordinate(location, wrist_orientation=WristOrientation.VERTICAL)
        self.controller.robotarm.set_grabber(closed=True)
        time.sleep(1)
        self.controller.go_to_location(HOVER_ABOVE_INPUT)

    def __move_object(self, shape: Shape):
        """
        Moves the object above the puzzle area
        Args:
            shape: was previously used to hover above the exact puzzle piece location
            Removed because rare but quirky problems with inversed kinematics
        """
        print('[@] Moving object')
        self.controller.go_to_location(HOVER_ABOVE_PUZZLES)

    def __place_down_object(self, shape: Shape):
        """
        Places down object in the correct locations according to the location defined in PUZZLE_LOCATIONS constant
        Args:
            shape: label of the object currently in the gripper
        """
        print('[@] Placing down object')
        self.controller.go_to_location(PUZZLE_LOCATIONS[shape])
        self.controller.robotarm.set_grabber(closed=False)