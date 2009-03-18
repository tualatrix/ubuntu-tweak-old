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
import os
import gtk
import shutil
from userdir import UserdirFile
from common.consts import *
from common.widgets import TweakPage, DirView, FlatView
from common.widgets.dialogs import WarningDialog, ErrorDialog
from common.utils import set_label_for_stock_button

(
    COLUMN_ICON,
    COLUMN_TEMPINFO,
    COLUMN_FILE,
) = range(3)


def update_dir():
    system_dir = os.path.join(os.path.expanduser("~"), ".ubuntu-tweak/templates")
    __uf = UserdirFile()
    __template_dir = __uf['XDG_TEMPLATES_DIR']
    if not __template_dir:
        __template_dir = os.path.expanduser('~/Templates')
        if not os.path.exists(__template_dir):
            os.mkdir(__template_dir)
        user_dir = __template_dir
    user_dir = __template_dir

    return system_dir, user_dir

def is_right_path():
    if (os.path.expanduser('~').strip('/') == USER_DIR.strip('/')) or os.path.isfile(USER_DIR):
        return False
    else:
        return True

SYSTEM_DIR, USER_DIR = update_dir()

class DefaultTemplates:
    """This class use to create the default templates"""
    templates = {
            "html-document.html": _("HTML document"),
            "odb-database.odb": _("ODB Database"),
            "ods-spreadsheet.ods": _("ODS Spreadsheet"),
            "odt-document.odt": _("ODT Document"),
            "plain-text-document.txt": _("Plain text document"),
            "odp-presentation.odp": _("ODP Presentation"),
            "python-script.py": _("Python script"),
            "pygtk-example.py": _("Pygtk Example"),
            "shell-script.sh": _("Shell script")
            }

    def create(self):
        if not os.path.exists(SYSTEM_DIR):
            os.makedirs(SYSTEM_DIR)
        for file, des in self.templates.items():
            realname = "%s.%s" % (des, file.split('.')[1])
            if not os.path.exists(os.path.join(SYSTEM_DIR, realname)):
                shutil.copy(os.path.join(DATA_DIR, 'templates/%s' % file), os.path.join(SYSTEM_DIR, realname))

    def remove(self):
        if not os.path.exists(SYSTEM_DIR):
            return 
        if os.path.isdir(SYSTEM_DIR): 
            for root, dirs, files in os.walk(SYSTEM_DIR, topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
                    os.rmdir(SYSTEM_DIR)
        else:
            os.unlink(SYSTEM_DIR)
        return

class EnableTemplate(DirView):
    """The treeview to display the enable templates"""
    type = _("Enabled Templates")

    def __init__(self):
        DirView.__init__(self, USER_DIR)

class DisableTemplate(FlatView):
    """The treeview to display the system template"""
    type = _("Disabled Templates")

    def __init__(self):
        FlatView.__init__(self, SYSTEM_DIR, USER_DIR)

class Templates(TweakPage):
    """Freedom added your docmuent templates"""
    def __init__(self):
        TweakPage.__init__(self, _('Manage Templates'))

        if not is_right_path():
            self.set_description(_('Templates path is wrong! The current path is point to "%s".\nPlease reset it to a folder under your Home Folder.') % USER_DIR)

            hbox = gtk.HBox(False, 0)
            self.pack_start(hbox, False, False, 0)

            button = gtk.Button(stock = gtk.STOCK_GO_FORWARD)
            button.connect('clicked', self.on_go_button_clicked)
            set_label_for_stock_button(button, _('Go And Set'))
            hbox.pack_end(button, False, False, 0)

            button = gtk.Button(stock = gtk.STOCK_EXECUTE)
            button.connect('clicked', self.on_restart_button_clicked)
            set_label_for_stock_button(button, _('Restart This Module'))
            hbox.pack_end(button, False, False, 0)
        else:
            self.create_interface()

    def create_interface(self):
        self.set_title(_('Manage Templates'))
        self.set_description(_('Here you can freely manage your document templates.\nYou can add files as templates by dragging them onto this window.\nYou can create new documents based on these templates from the Nautilus right-click menu.'))

        self.default = DefaultTemplates()
        self.config_test()

        hbox = gtk.HBox(False, 10)
        self.pack_start(hbox)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.enable_templates = EnableTemplate()
        sw.add(self.enable_templates)

        sw = gtk.ScrolledWindow()
        sw.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
        hbox.pack_start(sw)

        self.disable_templates = DisableTemplate()
        sw.add(self.disable_templates)

        hbox = gtk.HBox(False, 0)
        self.pack_start(hbox, False, False, 10)

        button = gtk.Button(_("Rebuild System Templates"))
        button.connect("clicked", self.on_rebuild_clicked)
        hbox.pack_end(button, False, False, 5)

        self.enable_templates.connect('drag_data_received', self.on_enable_drag_data_received)
        self.enable_templates.connect('deleted', self.on_enable_deleted)
        self.disable_templates.connect('drag_data_received', self.on_disable_drag_data_received)

        self.show_all()

    def on_go_button_clicked(self, widget):
        self.emit('call', 'mainwindow', 'select_module', {'name': 'userdir'})

    def on_restart_button_clicked(self, widget):
        global SYSTEM_DIR, USER_DIR 
        SYSTEM_DIR, USER_DIR = update_dir()
        if is_right_path():
            self.remove_all_children()
            self.create_interface()
        else:
            ErrorDialog(_('Templates path is still wrong, Please reset it!')).launch()

    def on_enable_deleted(self, widget):
        self.disable_templates.update_model()

    def on_enable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.disable_templates.update_model()

    def on_disable_drag_data_received(self, treeview, context, x, y, selection, info, etime):
        self.enable_templates.update_model()

    def on_rebuild_clicked(self, widget):
        dialog = WarningDialog(_('This will delete all disabled templates.\nDo you wish to continue?'))
        if dialog.run() == gtk.RESPONSE_YES:
            self.default.remove()
            self.default.create()
            self.disable_templates.update_model()
        dialog.destroy()

    def config_test(self):
        if not os.path.exists(SYSTEM_DIR):
            self.default.create()

if __name__ == "__main__":
    from utility import Test
    Test(Templates)
