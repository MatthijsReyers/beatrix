from lib.consts import HOME_POSITION
from gui.visualizer import Visualizer
from gui.camerafeed import CameraFeed
from gui.topbar import TopBar
from threading import Thread
import gi, cv2, time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class MainWindow(Gtk.Window):
    def __init__(self, client, logger, config):
        super().__init__(title="Beatrix debug monitor")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(1200,800)
        
        self.logger = logger
        self.config = config
        self.client = client

        self.box = Gtk.Box()
        self.box.set_orientation(Gtk.Orientation.VERTICAL)
        self.add(self.box)

        self.topbar = TopBar(client, config)
        self.box.add(self.topbar)

        v_bar = Gtk.VPaned()

        # Main bar with visualizer and camera feed.
        main_bar = Gtk.HPaned()
        self.camera_feed = CameraFeed(client, logger)
        main_bar.add(self.camera_feed)
        self.visualizer = Visualizer()
        main_bar.add(self.visualizer)
        v_bar.add(main_bar)

        # 
        self.box.add(v_bar)

        self.position = [53.0, 40.0, 50.0]
        # self.__init_position_frame()
        
        # self.angles = [45,45,45,45,45,45]
        # self.__init_angles_frame()

        # self.grid = Gtk.Grid()
        # self.grid.set_vexpand(True)
        # self.grid.set_hexpand(True)
        # self.add(self.grid)
        self.connect('destroy', self.stop)
        # self.update_position(self.position)

    def start(self):
        self.running = True
        self.camera_feed.start()
        self.command_thread = Thread(target=self.__command_thread, args=(), daemon=True)
        self.command_thread.start()

    def stop(self, event):
        print('[*] Exiting, joining threads.')
        self.running = False
        self.camera_feed.stop()
        self.command_thread.join()

    def update_position(self, position: (float, float, float)):
        self.position = position
        self.visualizer.update_position(position)
        for i in range(3):
            self.position_scales[i].set_value(position[i])

    def __init_position_frame(self):
        self.position_frame = Gtk.Frame()
        self.position_frame.set_label("Position")
        self.position_frame.set_vexpand(True)
        self.position_scales = []

        scales = Gtk.Box(spacing=6)
        scales.set_orientation(Gtk.Orientation.VERTICAL)

        for axis in range(3):
            # scale = Gtk.Range()
            scale = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, -50, 50, 0.1)
            scale.set_value_pos(Gtk.PositionType.RIGHT)
            scale.set_hexpand(True)
            scale.set_has_origin(False)
            scale.set_value(0.0)
            # scale.set_inverted(True)

            scale.connect('value-changed', self.__on_slider_move(axis))
            scales.add(scale)
            self.position_scales.append(scale)

        scales_frame = Gtk.Frame()
        scales_frame.add(scales)
        self.position_frame.add(scales_frame)
        self.grid.attach(self.position_frame, 4, 4, 1, 1)

    def __init_angles_frame(self):
        pass

    def __command_thread(self):
        print('[*] Started command thread.')

    def __on_slider_move(self, axis):
        def update(thing):
            self.position[axis] = thing.get_value()
            self.update_position(self.position)
        return update

    def __on_go_home(self):
        self.update_position(HOME_POSITION)
        self.send_go_home_cmd()
