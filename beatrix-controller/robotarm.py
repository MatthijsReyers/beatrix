from joints.parameters import JointParameters
from joints.singleservo import SingleServo
from joints.dualservo import DualServo
from joints.grabber import Grabber
from lib.constants import *
import numpy as np
import time, math

MAX_VELOCITY = 30  # Fastest speed of arm in degrees/s

class RobotArm:
    """
        Main class to initialise and control the robot arm
        - port allocation
            [0:base, 1:shoulder, 2:shoulder mirror, 3:elbow, 4:wrist, 5:grabber]

        ARGUMENTS
        - parameters
            Shoulder parameters are defined once
            [base, shoulder, elbow, wrist, grabber]
            - parameters: list(5) of dict(3) with 'min angle' and 'max angle', 'actuation range'
            - init_pos: list(5) of initial angles

        METHODS
            - set_arm
            - set_grabber
            - bound_angles
        PARAMETERS
            - joints
                list of joints of which this robot arm consists
    """

    def __init__(self, debug_server, joint_ids:list=None, debug_mode:bool=False):
        self.debug_server = debug_server

        if debug_mode: 
            PCA = None
        else: 
            from board import SCL, SDA
            from adafruit_pca9685 import PCA9685
            import busio
            I2C = busio.I2C(SCL, SDA)
            PCA = PCA9685(I2C)
            PCA.frequency = 50

        self.joints = dict()
        self.grabber = Grabber(GRABBER_PARAMETERS, PCA, 90, debug_mode)

        if joint_ids == None:
            joint_ids = [
                BASE_JOINT_ID,
                SHOULDER_JOINT_ID,
                ELBOW_JOINT_ID,
                WRIST_JOINT_ID,
                WRIST_TURN_JOINT_ID
            ]

        for j_id in joint_ids:
            parameters = JointParameters(min_angle=ANGLE_BOUNDS[j_id][0], max_angle=ANGLE_BOUNDS[j_id][1],
                                         servo_port=SERVO_PORTS[j_id], mirrored=JOINT_TYPE[j_id]['mirrored'],
                                         actuation_range=ACTUATION_RANGE[j_id],
                                         init_angle=INITIAL_ANGLES[j_id])

            if JOINT_TYPE[j_id]["duality"] == "single":
                self.joints[j_id] = (SingleServo(parameters=parameters, pca9685=PCA,
                                               angle=parameters.initial_angle, debug_mode=debug_mode))
            elif JOINT_TYPE[j_id]["duality"] == "dual":
                self.joints[j_id] = (DualServo(parameters=parameters, pca9685=PCA,
                                             angle=parameters.initial_angle, debug_mode=debug_mode))

        self.set_arm(INITIAL_ANGLES, 1)

    def set_arm(self, new_angles: dict, v_max:int=25):
        """
        Sets the angle of all servos smoothly over period of time
        ARGUMENTS
            - new_angle: dict()
                {Joint_id_1: desired angle, Joint_id_2: desired angle, etc...}
                joint id's as in constants file
        PARAMETERS
            - v_max: float time in seconds
        """

        if v_max > MAX_VELOCITY:
            print("Currently no implementation for movement that is too fast\n")
            print(f"Velocity: {v_max} degrees/s over the max: {MAX_VELOCITY}")
            v_max = MAX_VELOCITY

        new_angles = self.bound_angles(new_angles)
        old_angles = self.get_current_angles(new_angles.keys())

        if len(new_angles) != len(old_angles):
            raise ValueError("New angles is not the same size as old angles")

        angle_differences = dict()
        durations = dict()

        for i, value in new_angles.items():
            difference = abs(value - old_angles[i])
            if difference != 0:
                angle_differences[i] = difference
                duration_i = (difference * math.pi) / (2 * v_max)
                durations[i] = duration_i

        if len(durations) == 0:
            return
        max_duration = np.max(list(durations.values()))  # for now, use the max duration of all servos

        dtime = D_TIME
        steps = int(max_duration / dtime)

        # for each step adjust for each servo the angle
        for step in range(steps):
            current_ptime = time.process_time()
            for j_id in angle_differences:
                calculated_angle = get_angle_smooth(start_angle=old_angles[j_id],
                                                    end_angle=new_angles[j_id],
                                                    seconds=durations[j_id], elapsed=(step + 1) * dtime)
                self.joints[j_id].set_angle(calculated_angle, new_angles[j_id])

            time_elapsed = time.process_time() - current_ptime
            if step % 10 == 0:
                self.debug_server.send_update(
                    angles=self.get_current_angles())
            if time_elapsed >= dtime:
                # print("!!!! Process took longer than control loop time !!!!")
                # print("time elapsed = {}".format(time_elapsed))
                pass
            else:
                time.sleep(dtime - time_elapsed)

        self.debug_server.send_update(
            angles=self.get_current_angles())

    def set_grabber(self, closed, angle=None):
        """If no angle is parsed, state=0 is open, state=1 is closed"""
        if angle:
            self.grabber.set_angle(angle)
        elif closed:
            self.grabber.set_closed()
        else:
            self.grabber.set_open()
        self.debug_server.send_update(
            grabber=closed)

    def bound_angles(self, angles: dict):
        """
        Returns a list of angles such that all the angles lie within the bounds as defined in constants
        Args:
            angles: dictionary of angles that should be bounded

        Returns: dictionary of bound angles

        """
        for angle_id, angle in angles.items():
            if self.joints[angle_id].min_angle > angle:
                angles[angle_id] = self.joints[angle_id].min_angle
            elif self.joints[angle_id].max_angle < angle:
                angles[angle_id] = self.joints[angle_id].max_angle

        return angles

    def get_current_angles(self, requested_angles=None):
        """
        Returns dictionary of angles the joints are currently in
        Args:
            requested_angles: angles of which the angles are required, if None returns angles of all joints

        Returns: dictionary of current angles of the requested joints

        """
        if requested_angles is None:
            to_be_retrieved_angles = self.joints
        else:
            to_be_retrieved_angles = requested_angles

        angles = dict()
        for j_id in to_be_retrieved_angles:
            angles[j_id] = self.joints[j_id].current_angle
        return angles




def get_angle_smooth(start_angle, end_angle, seconds, elapsed):
    """
        Determines angles for different phases in a move such that a smooth motion is achieved
        Arguments:
            start_angle: the angle of the servo before this function was called
            end_angle: the angle we want the servo to go too
            seconds: how long the motion should last
            elapsed: how much time has passed
        Returns: new angle given the elapsed time
    """
    moving_angle = abs(start_angle - end_angle)  # degrees the servo has to move
    time = (elapsed / seconds) * np.pi
    if elapsed < seconds:
        if end_angle > start_angle:
            return start_angle + (-.5 * math.cos(time) + .5) * moving_angle
        if end_angle < start_angle:
            return start_angle - (-.5 * math.cos(time) + .5) * moving_angle
    return end_angle
