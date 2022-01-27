from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
from lib.constants import *
from math import pi, radians, degrees
import math

beatrix_rep = Chain(name='beatrix_representation', links=[
    OriginLink(),
    URDFLink(
        name="base",
        origin_translation=[0, 0, 6],
        origin_orientation=[0, 0, pi],
        rotation=[0, 0, 1],
        bounds=(0, radians(270))
    ),
    URDFLink(
        name="shoulder",
        origin_translation=[0, 0, 3],
        origin_orientation=[-0.5 * pi, 0, pi],
        rotation=[1, 0, 0],
        bounds=(radians(38), radians(90))
    ),
    URDFLink(
        name="elbow",
        origin_translation=[0, 0, 20],
        origin_orientation=[-radians(10), 0, 0],
        rotation=[1, 0, 0],
        bounds=(radians(10), radians(150))
    ),
    URDFLink(
        name="wrist",
        origin_translation=[0, 0, 15],
        origin_orientation=[-radians(88), 0, pi],
        rotation=[1, 0, 0],
        bounds=(radians(0), radians(180))
    ),
    URDFLink(
        name="wrist_turn",
        origin_translation=[0, 0, 10],
        origin_orientation=[0, 0, 0],
        rotation=[1, 0, 0],
        bounds=(radians(0), radians(180))
    ),
],
                   #active_links_mask=[False, True, True, True, True, True]
                   )


ik_chain = Chain(name='left_arm', links=[
    OriginLink(),
    URDFLink(
        name="base",
        origin_translation=[0, 0, BASE_HEIGHT],
        origin_orientation=[0, 0, 0],
        rotation=[0, 0, 1],
        # bounds=(math.radians(90), math.radians(180))
    ),
    URDFLink(
        name="base2",
        origin_translation=[0, 0, SHOULDER_HEIGHT],
        origin_orientation=[0, pi*-0.5, 0],
        rotation=[0, 1, 0],
        # bounds=(0,0)
        bounds=(math.radians(10), math.radians(90))
    ),
    URDFLink(
        name="shoulder",
        origin_translation=[0, 0, SHOULDER_LENGTH],
        origin_orientation=[0, 0, 0],
        rotation=[0, 1, 0],
        # bounds=(0,0)
    ),
    URDFLink(
        name="elbow",
        origin_translation=[0, 0, ELBOW_LENGTH],
        origin_orientation=[0, 0, 0],
        rotation=[0, 1, 0],
        # bounds=tuple(map(math.radians, ANGLE_BOUNDS[BASE_JOINT_ID]))
    ),
    URDFLink(
        name="wrist",
        origin_translation=[0, 0, WRIST_LENGTH],
        origin_orientation=[0, 0, 0],
        rotation=[0, 1, 0],
        # bounds=tuple(map(math.radians, ANGLE_BOUNDS[BASE_JOINT_ID]))
    ),
    # URDFLink(
    #     name="elbow",
    #     origin_translation=[25, 0, 0],
    #     origin_orientation=[0, 0, 0],
    #     rotation=[0, 1, 0],
    #     # bounds=(0, 1.3)
    # ),
    # URDFLink(
    #     name="wrist",
    #     origin_translation=[22, 0, 0],
    #     origin_orientation=[0, 0, 0],
    #     rotation=[0, 1, 0],
    # )
])


