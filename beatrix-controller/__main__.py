import sys, platform, argparse

# Are we running on a Raspberry Pi?
is_pi = platform.system() != 'Windows' and 'MANJARO' not in platform.release()

# Setup commandline arguments parser.
parser = argparse.ArgumentParser(description='Controller software for the Beatrix robot arm.')
parser.add_argument('--no-io', default=not is_pi, action='store_true',
                    help='Don\'t connect to GPIO pins, useful for when you don\'t want to run this\
                        software on a Raspberry Pi.')
parser.add_argument('--no-cam', default=False, action='store_true',
                    help='Don\'t try to capture frames from the camera, useful for when you want to\
                        test the software without a pi camera.')

# Parse arguments (skip first since its the file).
args = parser.parse_args(sys.argv[1:])

# Import system components.
from robotarm import RobotArm
from camera import Camera
from controller import Controller
from debugserver import DebugServer
from autopilot import AutoPilot
from commandhandler import CommandHandler
from objectrecognition import ObjectRecognizer

# Initialize system components.
server     = DebugServer()
camera     = Camera(debug_server=server)
robotarm   = RobotArm(server, debug_mode=args.no_io)
recognizer = ObjectRecognizer('./beatrix-controller/int8-model_3.lite')
controller = Controller(robotarm, camera, recognizer)
autopilot  = AutoPilot(server, controller, camera)
handler    = CommandHandler(server, controller, autopilot)

try:
    # Start threads
    server.start(handler)
    camera.start()
    camera.camera_thread.join()

except KeyboardInterrupt as e:
    server.stop()
    camera.stop()
