from deluge.log import LOG as log
from deluge.ui.client import client
import deluge.component as component
import deluge.common

# Python2 galore

try:
    # Py3 first
    from gi.repository import Gtk as gtk
except ImportError:
    import gtk

try:
    from deluge.ui.gtkui.torrentdetails import Tab
except ImportError:
    from deluge.ui.gtk3.torrentdetails import Tab

import cgi

try:
    from deluge.plugins.pluginbase import GtkPluginBase
except ImportError:
    from deluge.plugins.pluginbase import Gtk3PluginBase as GtkPluginBase

def get_resource(filename):
    import pkg_resources, os
    return pkg_resources.resource_filename("showmagnet", os.path.join("data", filename))

class GladeLoader(object):
    def __init__(self):
        try:
            #GTK2
            loader = gtk.glade.XML(get_resource("magnet_tab.glade"))
            self.get_object = lambda x: loader.get_widget(x)
        except AttributeError:
            # GTK3
            loader = gtk.Builder()
            loader.add_from_file(get_resource("magnet_tab_gtk3.glade"))
            self.get_object = lambda x: loader.get_object(x)

class MagnetTab(Tab):
    def __init__(self):
        Tab.__init__(self)
        loader = GladeLoader()

        self._name = "Magnet"
        self._child_widget = loader.get_object("magnet_tab")
        self._tab_label = loader.get_object("magnet_tab_label")

        vb = gtk.VBox()
        self.cb = gtk.Label("Magnet link goes here")
        self.cb.set_line_wrap(True)
        self.cb.set_line_wrap_mode(True)  # Wrap on char
        vb.pack_end(self.cb,expand=True,fill=True,padding=5)

        vp = gtk.Viewport()
        vp.add(vb)


        self._child_widget.add(vp)
        self._child_widget.get_parent().show_all()

        #keep track of the current selected torrent
        self._current = -1


    def __dest(self, widget, response):
        widget.destroy()

    def clear(self):
        self._current = None

    def __update_callback(self, mag_link):
        esc_link=cgi.escape(mag_link)
        self.cb.set_markup('<a href="{link}">{link}</a>'.format(
            link=esc_link,
        ))


    def update(self):
        # Get the first selected torrent
        selected = component.get("TorrentView").get_selected_torrents()

        # Only use the first torrent in the list or return if None selected
        if len(selected) != 0:
            selected = selected[0]
            # TODO skip fancy if?
            if(selected != self._current):
                #new torrent selected, clear the selected pieces, update priority checkbox
                self._current = selected
                bl = client.showmagnet.get_link(self._current)
                bl.addCallback(self.__update_callback)
        else:
            # No torrent is selected in the torrentview
            return
