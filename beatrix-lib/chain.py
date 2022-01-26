from ikpy.chain import Chain
from ikpy.link import OriginLink, URDFLink
from lib.constants import *


import math
print("test")

ik_chain = Chain(name='left_arm', links=[
    OriginLink(),
    URDFLink(
        name="base",
        origin_translation=[0, 5, 0],
        origin_orientation=[0, 1.5, 0],
        rotation=[0, 1, 0],
        #bounds=(-4,4)
    ),
    # URDFLink(
    #     name="test2",
    #     origin_translation=[0, 0, 2],
    #     origin_orientation=[0, 3, 0],
    #     rotation=[0, 1, 0],
    #     # bounds=(0,0)
    # ),
    # URDFLink(
    #     name="elbow",
    #     origin_translation=[0, 0, 10],
    #     origin_orientation=[0, 0, 0],
    #     rotation=[0, 1, 0],
    #     bounds=tuple(map(math.radians, ANGLE_BOUNDS[BASE_JOINT_ID]))
    # ),

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
