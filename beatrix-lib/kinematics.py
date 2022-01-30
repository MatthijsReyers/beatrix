from typing import Tuple
from abc import abstractmethod
from ikpy.chain import Chain
from lib.constants import *
from enum import Enum
from math import degrees
import numpy as np


class WristOrientation(Enum):
    UNSET = 0
    HORIZONTAL = 1
    VERTICAL = 2

    def __str__(self) -> str:
        if self.value == WristOrientation.HORIZONTAL.value:
            return 'Horizontal'
        if self.value == WristOrientation.VERTICAL.value:
            return 'Vertical'
        else:
            return 'Unset'

class Kinematics():
    def __init__(self):
        pass

    @abstractmethod
    def inverse(self, position: Tuple[float, float, float],
                wrist_orientation: WristOrientation = WristOrientation.UNSET) -> dict:
        raise NotImplemented

    @abstractmethod
    def get_forward_cartesian(self, angles: list) -> Tuple[float, float, float]:
        raise NotImplemented


class IkPyKinematics(Kinematics):
    def __init__(self, chain: Chain):
        self.chain = chain

    def inverse(self, position: Tuple[float, float, float],
                wrist_orientation: WristOrientation = WristOrientation.UNSET) -> dict:
        """
        Calculates the solution of angles for a workspace coordinate (in degrees)
        Args:
            wrist_orientation: desired orientation for the wrist joint
            position: X,Y,Z coordinates

        Returns:
            Angles dictionary:  {JOINT_ID: anglex, JOINT_ID2: anglexx, etc...} with angles in degrees

        """
        if wrist_orientation == WristOrientation.UNSET:
            solution_angles = self.chain.inverse_kinematics(position)
            print("unset")
        elif wrist_orientation == WristOrientation.VERTICAL:
            solution_angles = self.chain.inverse_kinematics(position, orientation_mode='Z',
                                                            target_orientation=np.array([0, 0, 1]))
            print("vertical")
        elif wrist_orientation == WristOrientation.HORIZONTAL:
            solution_angles = self.chain.inverse_kinematics(position, orientation_mode='X',
                                                            target_orientation=np.array([0, 0, 1]))  # TODO
            print("horizontal")

        new_angles = {
            BASE_JOINT_ID: degrees(solution_angles[1]) + 90,
            # +90 for compensation of chain bounds (-90, 180)
            # instead of (0, 270)
            SHOULDER_JOINT_ID: degrees(solution_angles[2]),
            ELBOW_JOINT_ID: degrees(solution_angles[3]),
            WRIST_JOINT_ID: degrees(solution_angles[4]),
            WRIST_TURN_JOINT_ID: degrees(solution_angles[5])
        }
        return new_angles

    def get_forward_cartesian(self, angles: dict) -> Tuple[float, float, float]:
        """
        returns the workspace coordinates of the end effector in x, y, z
        Args:
            angles: dictionary[JOINT_ID -> angle]

        Returns:
            tuple of x, y and z coordinate
        """
        angles_list = self.__angle_dict_to_list(angles)
        angles_list_radians = np.radians( np.array(angles_list) ).tolist()

        trans_matrix = self.chain.forward_kinematics(angles_list_radians)
        x = trans_matrix[0][3]
        y = trans_matrix[1][3]
        z = trans_matrix[2][3]
        #print("\n {} \n\n".format(trans_matrix))
        return (x, y, z)


    @staticmethod
    def __angle_dict_to_list(angles_i: dict):
        result = [0]
        result.extend(angles_i.values())
        result.append(0)
        return result
