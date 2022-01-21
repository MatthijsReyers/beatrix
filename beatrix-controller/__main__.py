import argparse, sys

# Setup commandline arguments parser.
parser = argparse.ArgumentParser(description='Controller software for the Beatrix robot arm.')
parser.add_argument('--no-pi', default=False, action='store_true',
                    help='Don\'t connect to GPIO pins, useful for when you don\'t want to run this\
                        software on a Raspberry Pi.')

# Parse arguments (skip first since its the file).
args = parser.parse_args(sys.argv[1:])

# Import system components.
from robotarm import RobotArm
from camera import Camera
from controller import Controller

# Initialize system components.
camera = Camera(debug_mode=args.no_debug)
robotarm = RobotArm(debug_mode=args.no_debug)
controller = Controller(camera, robotarm)
