
""" Average/safe buffer size for a video frame """
VIDEO_BUFFER_SIZE = 1000000

""" TCP port that the Raspberry Pi video camera's image is streamed over. """
VIDEO_PORT = 37020

""" TCP port that the control commands are sent over. """
CONTROL_PORT = 4400

""" Home/start position of the robot arm in x,y,z coordinates. """
HOME_POSITION = [50,50,50]



PLATFORM_HEIGHT = 5.0

""" ID's of the individual joints. """
BASE_JOINT_ID = 100
SHOULDER_JOINT_ID = 101
ELBOW_JOINT_ID = 102
WRIST_JOINT_ID = 103
WRIST_TURN_JOINT_ID = 104
GRABBER_JOINT_ID = 105

""" Maximum angle joints/servos may take. """
ANGLE_BOUNDS = {
    BASE_JOINT_ID: (0, 270),
    SHOULDER_JOINT_ID: (38, 90),
    ELBOW_JOINT_ID: (10, 150),
    WRIST_JOINT_ID: (0, 180),
    WRIST_TURN_JOINT_ID: (0, 180),
    GRABBER_JOINT_ID: (80, 100)
}