BASE_JOINT_ID = 100
SHOULDER_JOINT_ID = 101
ELBOW_JOINT_ID = 102
WRIST_JOINT_ID = 103
WRIST_TURN_JOINT_ID = 104
GRABBER_JOINT_ID = 105

N_JOINTS = 6

INITIAL_ANGLES = {
    BASE_JOINT_ID: 0,  # TODO
    SHOULDER_JOINT_ID: 90,
    ELBOW_JOINT_ID: 10,
    WRIST_JOINT_ID: 88,
    WRIST_TURN_JOINT_ID: 90  # TODO
    # GRABBER_JOINT_ID: 000       # TODO
}

ANGLE_BOUNDS = {
    BASE_JOINT_ID: (0, 270),
    SHOULDER_JOINT_ID: (38, 90),
    ELBOW_JOINT_ID: (10, 150),
    WRIST_JOINT_ID: (0, 180),
    WRIST_TURN_JOINT_ID: (0, 180)
    # GRABBER_JOINT_ID: (80, 100)
}

SERVO_PORTS = {
    BASE_JOINT_ID: 0,
    SHOULDER_JOINT_ID: (1, 2),
    ELBOW_JOINT_ID: 3,
    WRIST_JOINT_ID: 4,
    WRIST_TURN_JOINT_ID: 5
    # GRABBER_JOINT_ID: 6
}

JOINT_TYPE = {
    BASE_JOINT_ID: {'duality': 'single',
                    'mirrored': False},
    SHOULDER_JOINT_ID: {'duality': 'dual',
                        'mirrored': (True, False)},
    ELBOW_JOINT_ID: {'duality': 'single',
                     'mirrored': False},
    WRIST_JOINT_ID: {'duality': 'single',
                     'mirrored': False},
    WRIST_TURN_JOINT_ID: {'duality': 'single',
                          'mirrored': False},
    # GRABBER_JOINT_ID: {'duality': 'single',
    #               'mirrored': False}

}

ACTUATION_RANGE = {
    BASE_JOINT_ID: 270,
    SHOULDER_JOINT_ID: 180,
    ELBOW_JOINT_ID: 180,
    WRIST_JOINT_ID: 180,
    WRIST_TURN_JOINT_ID: 180,
    # GRABBER_JOINT_ID: 180
}
