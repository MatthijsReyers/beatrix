from threading import Thread
from visualizer import Visualizer
import gi, cv2, time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib

class MainWindow(Gtk.Window):
    def __init__(self, client):
        super().__init__(title="Beatrix debug monitor")
        self.set_position(Gtk.WindowPosition.CENTER_ALWAYS)
        self.set_default_size(1200,800)

        self.client = client
        self.position = [50.0, 50.0, 50.0]
        
        self.grid = Gtk.Grid()
        self.grid.set_vexpand(True)
        self.grid.set_hexpand(True)
        self.add(self.grid)

        self.visualizer = Visualizer()
        self.grid.attach(self.visualizer, 4, 0, 3, 1)

        self.__init_camera_frame()
        self.__init_position_frame()

        self.connect('destroy', self.stop)

    def start(self):
        self.running = True
        self.camera_thread = Thread(target=self.__camera_thread, args=(), daemon=True)
        self.camera_thread.start()
        self.command_thread = Thread(target=self.__command_thread, args=(), daemon=True)
        self.command_thread.start()

    def stop(self, event):
        print('[*] Exiting, joining threads.')
        self.running = False
        self.camera_thread.join()
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

    def __init_camera_frame(self):
        self.camera_frame = Gtk.Frame()
        self.camera_frame.set_label("Camera feed")
        self.camera_frame.set_size_request(400, 300)
        self.camera_frame.set_hexpand(True)

        self.camera_image = Gtk.Image()
        self.camera_frame.add(self.camera_image)

        self.grid.attach(self.camera_frame, 0, 0, 3, 1)

    def __camera_thread(self):
        print('[*] Started camera thread.')
        while self.running:
            try:
                frame = self.client.recieve_video()
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pb = GdkPixbuf.Pixbuf.new_from_data(
                    frame.tostring(),
                    GdkPixbuf.Colorspace.RGB,
                    False,
                    8,
                    frame.shape[1],
                    frame.shape[0],
                    frame.shape[2]*frame.shape[1])
                GLib.idle_add(self.camera_image.set_from_pixbuf, pb.copy())
            except Exception as e:
                print('Got exception: ', type(e), e)
                time.sleep(0.8)

    def __command_thread(self):
        print('[*] Started command thread.')

    def __on_slider_move(self, axis):
        def update(thing):
            print('moving')
            self.position[axis] = thing.get_value()
            self.update_position(self.position)
        return update

