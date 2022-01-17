import argparse, sys

# Setup commandline arguments parser.
parser = argparse.ArgumentParser(description='Controller software for the Beatrix robot arm.')
parser.add_argument('--no-pi', default=False, action='store_true',
                    help='Don\'t connect to GPIO pins, useful for when you don\'t want to run this\
                        software on a Raspberry Pi.')
parser.add_argument('--no-debug', default=False, action='store_true',
                    help='Don\'t show debug window, useful for when you want to run this software\
                        on a headless Raspberry Pi.')

# Parse arguments (skip first since its).
args = parser.parse_args(sys.argv[1:])

# Import system components.
from robotarm import RobotArm
from camera import Camera
from controller import Controller

# Initialize system components.
camera = Camera(debug_mode=args.no_debug)
robotarm = RobotArm(debug_mode=args.no_debug)
controller = Controller(camera, robotarm)

# Start debug window if needed. (Note the connditional import so that the control software can be 
# run without the GTK module installed).
if not args.no_debug:
    from debugwindow import DebugWindow
    from gi.repository import Gtk
    debugwindow = DebugWindow()
    debugwindow.connect("destroy", Gtk.main_quit)
    debugwindow.show_all()
    Gtk.main()
