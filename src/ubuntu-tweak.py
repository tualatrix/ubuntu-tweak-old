#!/usr/bin/python

# Ubuntu Tweak - PyGTK based desktop configure tool
#
# Copyright (C) 2007-2008 TualatriX <tualatrix@gmail.com>
#
# Ubuntu Tweak is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Ubuntu Tweak is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ubuntu Tweak; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA

import os
import gtk
import thread
try:
    import pynotify
except:
    pass
import gobject

from common.consts import *
from common.debug import run_traceback
from common.widgets.dialogs import ErrorDialog
from common.config import TweakSettings

try:
    import dl
    libc = dl.open('/lib/libc.so.6')
    libc.call('prctl', 15, 'ubuntu-tweak', 0, 0, 0)
except:
    pass

class TweakLauncher:
    def __init__(self):
        thread.start_new_thread(self.show_splash, ())

        try:
            from common.package import update_apt_cache
        except ImportError:
            pass

        from mainwindow import MainWindow

        window = MainWindow()

    def show_splash(self):
        gtk.gdk.threads_enter()
        win = gtk.Window(gtk.WINDOW_POPUP)
        win.set_position(gtk.WIN_POS_CENTER)

        vbox = gtk.VBox(False, 0)
        image = gtk.Image()
        image.set_from_file(os.path.join(DATA_DIR, 'pixmaps/splash.png'))

        vbox.pack_start(image)
        win.add(vbox)

        win.show_all()

        while gtk.events_pending ():
            gtk.main_iteration ()

        win.destroy()
        gtk.gdk.threads_leave()

    def main(self):
        gtk.gdk.threads_enter()
        if TweakSettings.get_check_update():
            os.system("exec python updatemanager.py &")
        gtk.main()
        gtk.gdk.threads_leave()

if __name__ == "__main__":
    try:
        gobject.threads_init()
        if 'pynotify' in locals():
            pynotify.init("Basics")
        launcher = TweakLauncher()
        launcher.main()
    except:
		run_traceback('fatal')
