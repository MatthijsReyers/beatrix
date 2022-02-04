
""" Ask the server for a complete update of the robot arm's current state (i.e. angles of the servos, 
    goal position, autopilot, etc.). """
GET_UPDATE = 'GET_UPD'

""" Set the current goal position of the robot arm. """
SET_POSITION = 'SET_POS'

""" Set the angles of the servo motors. """
SET_ANGLES = 'SET_ANG'

""" Set the open/closed state of the grabber. """
SET_GRABBER = 'SET_GRB'

""" Enable/disable the autopilot. """
SET_AUTOPILOT = 'SET_AUT'

""" Save the latest camera frame to filesystem. """
TAKE_PICTURE = 'TAK_PIC'
