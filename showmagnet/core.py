#
# core.py
#
# Copyright (C) 2009 backslasher <nitz.raz@gmail.com>
#
# Basic plugin template created by:
# Copyright (C) 2008 Martijn Voncken <mvoncken@gmail.com>
# Copyright (C) 2007-2009 Andrew Resch <andrewresch@gmail.com>
# Copyright (C) 2009 Damien Churchill <damoxc@gmail.com>
#
# Deluge is free software.
#
# You may redistribute it and/or modify it under the terms of the
# GNU General Public License, as published by the Free Software
# Foundation; either version 3 of the License, or (at your option)
# any later version.
#
# deluge is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with deluge.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA  02110-1301, USA.
#
#    In addition, as a special exception, the copyright holders give
#    permission to link the code of portions of this program with the OpenSSL
#    library.
#    You must obey the GNU General Public License in all respects for all of
#    the code used other than OpenSSL. If you modify file(s) with this
#    exception, you may extend this exception to your version of the file(s),
#    but you are not obligated to do so. If you do not wish to do so, delete
#    this exception statement from your version. If you delete this exception
#    statement from all source files in the program, then also delete it here.
#

import urllib.parse

from deluge.log import LOG as log
from deluge.plugins.pluginbase import CorePluginBase
import deluge.component as component
import deluge.configmanager
from deluge.core.rpcserver import export

DEFAULT_PREFS = {
    "test":"NiNiNi"
}

class Core(CorePluginBase):
    def enable(self):
        self.config = deluge.configmanager.ConfigManager("showmagnet.conf", DEFAULT_PREFS)

    def disable(self):
        pass

    def update(self):
        pass

    @export
    def set_config(self, config):
        """Sets the config dictionary"""
        for key in config.keys():
            self.config[key] = config[key]
        self.config.save()

    @export
    def get_config(self):
        """Returns the config dictionary"""
        return self.config.config

    def generate_magnet(self, t_hash):
        # https://stackoverflow.com/a/12480263
        torrent_id, t_status = list(t_hash.items())[0]
        name = t_status['name']
        trackers = t_status['trackers']
        querystring = urllib.parse.urlencode(
            {
                'dn':name,
                'tr':[tr['url'] for tr in trackers]
            },
            doseq=True
        )
        res = f'magnet:?xt=urn:btih:{torrent_id}&{querystring}'
        return res


    @export
    def get_link(self, torr):
        # TODO calc magnet link
        res = component.get("Core").get_torrents_status({"id": torr}, ['trackers', 'name'])
        # Deluge2 -> deferred
        if isinstance(res,dict):
            return self.generate_magnet(res)
        else:
            res.addCallback(self.generate_magnet)
            return res
