#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (C) 2009 Leonardo Ferreira Fontenelle <leonardof@gnome.org>
# 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
# 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.



import gtk
import hildon

from classix.gtkui import MainWindow



class HildonMainWindow(MainWindow):
    
    def __init__(self, ui_file_name):
        
        MainWindow.__init__(self, ui_file_name)
        self.keysym_to_fullscreen = gtk.keysyms.F6
        
        toolbar = self.builder.get_object("search_toolbar")
        vbox = self.builder.get_object("vbox1")
        vbox.set_child_packing(child=toolbar, expand=False, fill=True, 
            padding=0, pack_type = gtk.PACK_END)
        
        # For some reason it's not working automagically in Maemo.
        save_as_button = self.builder.get_object("save_as_button")
        save_as_button.connect("clicked", self.on_save_as_button_clicked)
    
    
    def get_save_as_dialog(self, suggested_name=None):
        
        dialog = hildon.FileChooserDialog(parent = self.window,
            action = gtk.FILE_CHOOSER_ACTION_SAVE)
        if suggested_name:
            dialog.set_current_name(suggested_name)
        
        return dialog
