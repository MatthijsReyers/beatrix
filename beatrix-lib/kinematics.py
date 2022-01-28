from typing import Tuple
from abc import abstractmethod
from ikpy.chain import Chain
from lib.constants import *
from enum import Enum
from math import degrees

class WristOrientation(Enum):
    UNSET = 0
    HORIZONTAL = 1
    VERTICAL = 2

class Kinematics():
    def __init__(self):
        pass

    @abstractmethod
    def inverse(self, position: Tuple[float, float, float], wrist_orientation: WristOrientation = WristOrientation.UNSET) -> dict:
        raise NotImplemented

    @abstractmethod
    def forward(self, angles: list) -> Tuple[float, float, float]:
        raise NotImplemented


class IkPyKinematics(Kinematics):
    def __init__(self, chain: Chain):
        self.chain = chain

    def inverse(self, position: Tuple[float, float, float], wrist_orientation: WristOrientation = WristOrientation.UNSET) -> dict:
        """
        Calculates the solution of angles for a workspace coordinate (in degrees)
        Args:
            wrist_orientation: desired orientation for the wrist joint
            position: X,Y,Z coordinates

        Returns:
            Angles dictionary:  {JOINT_ID: anglex, JOINT_ID2: anglexx, etc...} with angles in degrees

        """


        solution_angles = self.chain.inverse_kinematics(position)
        new_angles = {
            BASE_JOINT_ID: degrees(solution_angles[1]) + 90,  # +90 for compensation of chain bounds (-90, 180)
            # instead of (0, 270)
            SHOULDER_JOINT_ID: degrees(solution_angles[2]),
            ELBOW_JOINT_ID: degrees(solution_angles[3]),
            WRIST_JOINT_ID: degrees(solution_angles[4]),
            WRIST_TURN_JOINT_ID: degrees(solution_angles[5])
        }
        return new_angles

    def forward(self, angles: dict) -> Tuple[float, float, float]:
        # self.chain.forward_kinematics()
        return (0, 0, 0)
