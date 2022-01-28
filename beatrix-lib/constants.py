
""" Average/safe buffer size for a video frame """
VIDEO_BUFFER_SIZE = 1000000

""" TCP port that the Raspberry Pi video camera's image is streamed over. """
VIDEO_PORT = 37020

""" TCP port that the control commands are sent over. """
CONTROL_PORT = 4400

""" Home/start position of the robot arm in x,y,z coordinates. """
HOME_POSITION = [50, 50, 50]

HOME_ANGLES = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0]

""" DT used for calculating steps in set_arm"""
D_TIME = 1 / 10 # 2Hz

BASE_HEIGHT = 6.0
SHOULDER_HEIGHT = 3.0
SHOULDER_LENGTH = 22
ELBOW_LENGTH = 15
WRIST_LENGTH = 10

"Global Identifiers of the different joints"
BASE_JOINT_ID       = 'base_joint'
SHOULDER_JOINT_ID   = 'shoulder_joint'
ELBOW_JOINT_ID      = 'elbow_joint'
WRIST_JOINT_ID      = 'wrist_joint'
WRIST_TURN_JOINT_ID = 'wrist_turn_joint'
GRABBER_JOINT_ID    = 'grabber_joint'

N_JOINTS = 6

""" Parameters used for initializing grabber servo/joints.Grabber class. """
GRABBER_PARAMETERS = {
    "min angle": 80, 
    "max angle": 100, 
    "actuation range": 180,
    "open": 90, 
    "closed": 180, 
    "port": 6
}

"Initial angles of all the joints so that the arm stands vertically"
INITIAL_ANGLES = {
    BASE_JOINT_ID: 0,  # TODO
    SHOULDER_JOINT_ID: 90,
    ELBOW_JOINT_ID: 10,
    WRIST_JOINT_ID: 88,
    WRIST_TURN_JOINT_ID: 90  # TODO
    # GRABBER_JOINT_ID: 000       # TODO
}

"The angle bounds (allowed angles) for each joint"
ANGLE_BOUNDS = {
    BASE_JOINT_ID: (0, 270),
    SHOULDER_JOINT_ID: (90, 142),
    ELBOW_JOINT_ID: (10, 150),
    WRIST_JOINT_ID: (0, 180),
    WRIST_TURN_JOINT_ID: (0, 180)
    # GRABBER_JOINT_ID: (80, 100)
}

"The servo ports for each joint, note that the shoulder has two ports as it consists of two servo motors"
SERVO_PORTS = {
    BASE_JOINT_ID: 0,
    SHOULDER_JOINT_ID: (1, 2),
    ELBOW_JOINT_ID: 3,
    WRIST_JOINT_ID: 4,
    WRIST_TURN_JOINT_ID: 5
    # GRABBER_JOINT_ID: 6
}

"Joint type of each joint as used by the single_servo and dual_servo classes"
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

"Upper limits of the actuation range, note that lower limit always is 0 for the servo's"
ACTUATION_RANGE = {
    BASE_JOINT_ID: 270,
    SHOULDER_JOINT_ID: 180,
    ELBOW_JOINT_ID: 180,
    WRIST_JOINT_ID: 180,
    WRIST_TURN_JOINT_ID: 180,
    # GRABBER_JOINT_ID: 180
}
