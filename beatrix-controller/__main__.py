import sys, platform, argparse

# Are we running on a Raspberry Pi?
is_pi = platform.system() != 'Windows' and 'MANJARO' not in platform.release()

# Setup commandline arguments parser.
parser = argparse.ArgumentParser(description='Controller software for the Beatrix robot arm.')
parser.add_argument('--no-pi', default=is_pi, action='store_true',
                    help='Don\'t connect to GPIO pins, useful for when you don\'t want to run this\
                        software on a Raspberry Pi.')

# Parse arguments (skip first since its the file).
args = parser.parse_args(sys.argv[1:])

# Import system components.
from robotarm import RobotArm
from camera import Camera
from controller import Controller
from debugserver import DebugServer

# Initialize system components.
camera = Camera(debug_mode=args.no_pi)
server = DebugServer()
# robotarm   = RobotArm(debug_mode=args.no_pi)
# controller = Controller(camera, robotarm)
