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

import pygtk
pygtk.require("2.0")
import gtk
import os
import gconf
import gettext

from common.consts import *
from common.widgets import ListPack, SinglePack, TweakPage
from common.factory import WidgetFactory

class Session(TweakPage):
    """GNOME Session control"""
    def __init__(self):
        TweakPage.__init__(self)

        self.pack_start(self.session_control_box(), False, False, 0)

        box = SinglePack(_('Splash Screen (Click On Image)'), self.splash_hbox())
        self.pack_start(box, False, False, 0)

    def change_splash_cb(self, widget, data = None):
        dialog = gtk.FileChooserDialog(_("Choose a splash image"),action = gtk.FILE_CHOOSER_ACTION_OPEN, buttons = (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL, gtk.STOCK_OPEN, gtk.RESPONSE_ACCEPT))
        filter = gtk.FileFilter()
        filter.set_name(_("PNG image (*.png)"))
        filter.add_mime_type("image/png")
        dialog.set_current_folder(self.filedir)
        dialog.add_filter(filter)

        if dialog.run() == gtk.RESPONSE_ACCEPT:
            client = gconf.client_get_default()
            filename = dialog.get_filename()
            data.set_text(os.path.basename(filename))
            self.filedir = os.path.dirname(filename)
            self.original_preview = gtk.gdk.pixbuf_new_from_file(filename)
            x = self.original_preview.get_width()
            y = self.original_preview.get_height()
            if x * 180 / y > 240:
                y = y * 240 / x
                x = 240
            else:
                x = x * 180 / y
                y = 180

            self.new_preview = self.original_preview.scale_simple(x , y, gtk.gdk.INTERP_NEAREST)
            self.image.set_from_pixbuf(self.new_preview)
            client.set_string("/apps/gnome-session/options/splash_image", filename)
        dialog.destroy()

    def splash_hbox(self):
        client = gconf.client_get_default()
        filename = client.get_string("/apps/gnome-session/options/splash_image")

        self.filedir = "/usr/share/pixmaps/splash"

        if filename:
            if filename[0] != "/":
                filename = "/usr/share/pixmaps/" + filename

            self.filedir = os.path.dirname(filename)

            try:
                f = open(filename)
            except IOError:
                print "Failed to open file '%s': No such file or directory" % filename
            else:
                self.original_preview = gtk.gdk.pixbuf_new_from_file(filename)
                x = self.original_preview.get_width()
                y = self.original_preview.get_height()

                if x * 180 / y > 240:
                    y = y * 240 / x
                    x = 240
                else:
                    x = x * 180 / y
                    y = 180

                self.new_preview = self.original_preview.scale_simple(x, y, gtk.gdk.INTERP_NEAREST)

        hbox = gtk.HBox(False, 0)
        self.button = gtk.Button()
        hbox.pack_start(self.button, True, False, 0)
        hbox.set_size_request(256, -1)

        if client.get_bool("/apps/gnome-session/options/show_splash_screen"):
            self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

        vbox = gtk.VBox(False, 2)
        self.button.add(vbox)

        alignment = gtk.Alignment(0.5, 0.5, 1, 1)
        alignment.set_size_request(240, 180)
        vbox.pack_start(alignment, False, False, 0)

        self.image = gtk.Image()
        if getattr(self, "new_preview", False):
            self.image.set_from_pixbuf(self.new_preview)
        alignment.add(self.image)

        label = gtk.Label(os.path.basename(filename))
        vbox.pack_end(label, False, False, 0)

        self.button.connect("clicked", self.change_splash_cb, label)

        return hbox

    def session_control_box(self):
        button = WidgetFactory.create("GconfCheckButton", 
                                      label = _("Automatically save open applications when logging out"), 
                                      key = "auto_save_session")
        button2 = WidgetFactory.create("GconfCheckButton", 
                                       label = _("Show logout prompt"), 
                                       key = "logout_prompt")
        button3 = WidgetFactory.create("GconfCheckButton", 
                                       label = _("Allow TCP Connections (Remote Desktop Connect)"), 
                                       key = "allow_tcp_connections")
        self.show_splash_button = WidgetFactory.create("GconfCheckButton", 
                                                       label = _("Show splash screen"), 
                                                       key = "show_splash_screen")
        self.show_splash_button.connect('toggled', self.colleague_changed)

        box = ListPack(_("Session Control"), (button, button2, button3, self.show_splash_button))
        return box

    def colleague_changed(self, widget):
        if self.show_splash_button.get_active():
            self.button.set_sensitive(True)
        else:
            self.button.set_sensitive(False)

if __name__ == "__main__":
    from utility import Test
    Test(Session)
