import gtk

from deluge.log import LOG as log
from deluge.ui.client import client
from deluge.plugins.pluginbase import GtkPluginBase
import deluge.component as component
import deluge.common
from deluge.ui.gtkui.torrentdetails import Tab

class MagnetTab(Tab):
    def __init__(self):
        Tab.__init__(self)
        glade_tab = gtk.glade.XML(get_resource("magnet_tab.glade"))

        self._name = "Magnet"
        self._child_widget = glade_tab.get_widget("magnet_tab")
        self._tab_label = glade_tab.get_widget("magnet_tab_label")

        self._ms = MultiSquare(0,['#000000','#FF0000','#0000FF'],
                               display=self._child_widget.get_display(),
                               menu=glade_tab.get_widget("priority_menu"))

        vb = gtk.VBox()
        vb.add(self._ms)
        self.cb = gtk.CheckButton(label="Set priority of first un-downloaded piece to High")
        self.cb.connect("toggled",self.onPrioTogg)
        vb.pack_end(self.cb,expand=False,fill=False,padding=5)

        vp = gtk.Viewport()
        vp.set_shadow_type(gtk.SHADOW_NONE)
        vp.add(vb)


        self._child_widget.add(vp)
        self._child_widget.get_parent().show_all()

        #keep track of the current selected torrent
        self._current = -1

        self._showed_prio_warn = False


    def onPrioTogg(self,widget):
        if (self._current):
            if (widget.get_active()):
                if not(self._showed_prio_warn):
                    reactor.callLater(0,self._showPrioWarn)
                    self._showed_prio_warn = True
                client.magnet.add_priority_torrent(self._current)
            else:
                client.magnet.del_priority_torrent(self._current)
        else:
            widget.set_active(False)

    def __dest(self, widget, response):
        widget.destroy()

    def _showPrioWarn(self):
        md = gtk.MessageDialog(component.get("MainWindow").main_glade.get_widget("main_window"),
                               gtk.DIALOG_MODAL,
                               gtk.MESSAGE_WARNING,
                               gtk.BUTTONS_OK,
                               "Using this option is rather unsocial and not particularly good for the torrent protocol.\n\nPlease use with care, and seed the torrent afterwards if you use this.")
        md.connect('response', self.__dest)
        md.show_all()
        return False


    def setColors(self,colors):
        self._ms.setColors(colors)

    def clear(self):
        self._ms.clear()
        self._current = None

    def __update_callback(self, (is_fin, num_pieces, pieces, curdl)):
        if (num_pieces == 0):
            return
        if (is_fin):
            self._ms.setNumSquares(num_pieces)
            for i in range (0,num_pieces):
                self._ms.setSquareColor(i,1)
            return

        self._ms.setNumSquares(num_pieces)

        cdll = len(curdl)
        cdli = 0
        if (cdll == 0):
            cdli = -1

	for i,p in enumerate(pieces):
            if p:
                self._ms.setSquareColor(i,1)
            elif (cdli != -1 and i == curdl[cdli]):
                self._ms.setSquareColor(i,2)
                cdli += 1
                if cdli >= cdll:
                    cdli = -1
            else:
                self._ms.setSquareColor(i,0)


    def update(self):
        # Get the first selected torrent
        selected = component.get("TorrentView").get_selected_torrents()

        # Only use the first torrent in the list or return if None selected
        if len(selected) != 0:
            selected = selected[0]
            if(selected != self._current):
                #new torrent selected, clear the selected pieces, update priority checkbox
                self._ms.resetSelected()
                self._current = selected
                client.pieces.is_priority_torrent(self._current).addCallback(self.cb.set_active)
        else:
            # No torrent is selected in the torrentview
            return

        client.pieces.get_torrent_info(selected).addCallback(self.__update_callback)
