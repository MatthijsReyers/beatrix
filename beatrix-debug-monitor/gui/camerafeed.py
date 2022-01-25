from matplotlib.backends.backend_gtk3agg import (FigureCanvasGTK3Agg as FigureCanvas)
from threading import Thread
from pickle import UnpicklingError
import gi, cv2, time

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GdkPixbuf, GLib


class CameraFeed(Gtk.Frame):
    def __init__(self, client, logger):
        super().__init__()
        self.set_label("Camera feed")
        self.set_size_request(400, 300)
        self.set_hexpand(True)

        self.client = client
        self.logger = logger
        self.camera_image = Gtk.Image()
        self.add(self.camera_image)

        self.running = False

    def start(self):
        self.running = True
        self.camera_thread = Thread(target=self.__camera_thread, args=(), daemon=True)
        self.camera_thread.start()

    def stop(self):
        self.running = False
        self.camera_thread.join()

    def __camera_thread(self):
        print('[*] Started camera thread.')
        while self.running:
            try:
                okay, frame = self.client.recieve_video()
                if okay:
                    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    print(frame.shape)
                    pb = GdkPixbuf.Pixbuf.new_from_data(
                        frame.tostring(),
                        GdkPixbuf.Colorspace.RGB,
                        False,
                        8,
                        frame.shape[1],
                        frame.shape[0],
                        frame.shape[2]*frame.shape[1])
                    GLib.idle_add(self.camera_image.set_from_pixbuf, pb.copy())
            except UnpicklingError as e:
                # print(e
                pass
            except Exception as e:
                self.logger.exception(e, 'CameraFeed.__camera_thread')
                time.sleep(0.8)