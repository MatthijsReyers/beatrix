import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

class TopBar(Gtk.Box):
    def __init__(self, client, config):
        super().__init__(self)
        self.set_spacing(10)
        self.set_orientation(Gtk.Orientation.HORIZONTAL)
        self.set_homogeneous(False)

        self.client = client
        self.config = config

        # Raspberry pi IP address entry box
        # ===========================================================================
        self.ip_select = Gtk.Box()
        self.ip_select.set_orientation(Gtk.Orientation.VERTICAL)
        self.ip_select.set_spacing(3)

        label = Gtk.Label('Raspberry Pi:')
        label.set_hexpand(True)
        label.set_justify(Gtk.Justification.LEFT)
        self.ip_select.add(label)

        box = Gtk.Box()
        box.set_orientation(Gtk.Orientation.HORIZONTAL)
        box.set_spacing(3)
        
        self.ip = self.config.raspberry_ip
        ip_entry = Gtk.Entry()
        ip_entry.set_text(self.ip)
        ip_entry.connect('changed', self.__on_ip_entry)
        box.add(ip_entry)

        self.ip_btn = Gtk.Button()
        self.ip_btn.set_label('OK')
        self.ip_btn.connect('button-press-event', self.__on_ip_save)
        self.ip_btn.set_sensitive(False)
        box.add(self.ip_btn)
        
        self.ip_select.add(box)

        # Server source select
        # ===========================================================================
        source_select = Gtk.Box()
        source_select.set_homogeneous(False)
        source_select.set_orientation(Gtk.Orientation.VERTICAL)
        source_select.set_spacing(3)
        source_select.set_hexpand(False)

        source_select.add(Gtk.Label('Connect to:'))

        self.localhost = Gtk.Label('')

        self.stack = Gtk.Stack()
        if self.config.local_server:
            self.stack.add_titled(self.localhost, 'Localhost', 'Localhost')
            self.stack.add_titled(self.ip_select, 'Raspberry Pi', 'Raspberry Pi')
        else:
            self.stack.add_titled(self.ip_select, 'Raspberry Pi', 'Raspberry Pi')
            self.stack.add_titled(self.localhost, 'Localhost', 'Localhost')
        self.stack.connect('notify::visible-child', self.__on_source_select)

        switcher = Gtk.StackSwitcher()
        switcher.set_stack(self.stack)
        switcher.set_hexpand(False)
        source_select.add(switcher)

        self.add(source_select)
        self.add(self.stack)

        # Padding
        # ===========================================================================
        padding = Gtk.Box()
        padding.set_hexpand(True)
        self.add(padding)
        self.set_child_packing(padding, True, True, True, Gtk.PackType.START)

    def __on_source_select(self, event, param):
        local = True
        if self.stack.props.visible_child not in [self.localhost,  self.ip_select]:
            return
        elif self.stack.props.visible_child == self.ip_select:
            local = False
        if self.config.local_server != local:
            self.config.local_server = local
            self.client.stop()
            self.client.connect()

    def __on_ip_entry(self, entry):
        self.ip = entry.get_text().replace(' ', '')
        if self.ip == self.config.raspberry_ip:
            self.ip_btn.set_sensitive(False)
        else: self.ip_btn.set_sensitive(True)

    def __on_ip_save(self, x, y):
        self.config.raspberry_ip = self.ip
        if not self.config.local_server:
            self.client.stop()
            self.client.connect()
        self.ip_btn.set_sensitive(False)