from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
from lib.constants import *
from math import pi, radians

beatrix_rep = Chain(name='beatrix_representation', links=[
    OriginLink(),
    URDFLink(
        name="base",
        origin_translation=[0, 0, 6],
        origin_orientation=[0, 0, pi],
        rotation=[0, 0, 1],
        bounds=(radians(-90), radians(180))
    ),
    URDFLink(
        name="shoulder",
        origin_translation=[0, 0, 3],
        origin_orientation=[-radians(INITIAL_ANGLES[SHOULDER_JOINT_ID]), 0, pi],
        rotation=[1, 0, 0],
        bounds=(radians(75), radians(142))
    ),
    URDFLink(
        name="elbow",
        origin_translation=[0, 0, 20],
        origin_orientation=[-radians(INITIAL_ANGLES[ELBOW_JOINT_ID]), 0, 0],
        rotation=[1, 0, 0],
        bounds=(radians(10), radians(150))
        # bounds=(- radians(150), - radians(10)),
    ),
    URDFLink(
        name="wrist",
        origin_translation=[0, 0, 15],
        origin_orientation=[-radians(INITIAL_ANGLES[WRIST_JOINT_ID]), 0, pi],
        rotation=[1, 0, 0],
        bounds=(radians(0), radians(180))
    ),
    URDFLink(
        name="wrist_turn",
        origin_translation=[0, 0, 10],
        origin_orientation=[0, 0, 0],
        rotation=[0, 0, 1],
        bounds=(radians(0), radians(180))
    ),
    URDFLink(
        name="grabber",
        origin_translation=[0, 0, 14],
        origin_orientation=[0, 0, 0],
        rotation=[0, 0, 0],
        #bounds=(radians(0), radians(180))
    )]
)
