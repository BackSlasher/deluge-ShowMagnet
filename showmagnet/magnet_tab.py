import gtk

from deluge.log import LOG as log
from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common
from deluge.ui.gtkui.torrentdetails import Tab

def get_resource(filename):
    import pkg_resources, os
    return pkg_resources.resource_filename("showmagnet", os.path.join("data", filename))

class MagnetTab(Tab):
    def __init__(self):
        Tab.__init__(self)
        glade_tab = gtk.glade.XML(get_resource("magnet_tab.glade"))

        self._name = "Magnet"
        self._child_widget = glade_tab.get_widget("magnet_tab")
        self._tab_label = glade_tab.get_widget("magnet_tab_label")

        vb = gtk.VBox()
        self.cb = gtk.CheckButton(label="Set priority of first un-downloaded piece to High")
        vb.pack_end(self.cb,expand=False,fill=False,padding=5)

        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.add(vb)


        self._child_widget.add(vp)
        self._child_widget.get_parent().show_all()

        #keep track of the current selected torrent
        self._current = -1

        print('fffff')



    def __dest(self, widget, response):
        widget.destroy()

    def clear(self):
        self._current = None

    def __update_callback(self, mag_link):
        print('aaaaa')
        print(mag_link)
        #TODO change label


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
