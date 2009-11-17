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


import codecs
import gtk
import sys

from classix.baseui import ClassixUI
from classix.searchbackend import SearchBackend
from gettext import gettext as _



class MainWindow (ClassixUI):
    
    def __init__(self, ui_file_name):
        
        ClassixUI.__init__(self)
        
        self.builder = gtk.Builder()
        self.builder.add_from_file(ui_file_name)
        self.search_liststore = gtk.ListStore(object)
        
        tv = self.builder.get_object("search_treeview")
        tv.set_model(self.search_liststore)
        
        code_col = self.builder.get_object("search_tvcol_code")
        self.code_cell = gtk.CellRendererText()
        code_col.pack_start(self.code_cell)
        code_col.set_cell_data_func(self.code_cell,
            self.get_value_from_liststore)
        tv.append_column(code_col)
        
        title_col = self.builder.get_object("search_tvcol_title")
        self.title_cell = gtk.CellRendererText()
        title_col.pack_start(self.title_cell)
        title_col.set_cell_data_func(self.title_cell,
            self.get_value_from_liststore)
        tv.append_column(title_col)
        
        self.builder.connect_signals(self)
        self.window = self.builder.get_object("main_window")
        self.window.show_all()
        self.window_in_fullscreen = False
        self.keysym_to_fullscreen = gtk.keysyms.F11
        
        self.progressbar = self.builder.get_object("progressbar")
        self.progressbar.hide()
    
    
    def add_node_to_search(self, node):
        self.search_liststore.append([node])
        return False # so that glib.idle_add won't repeat this callback forever.
    
    
    def get_save_as_dialog(self, suggested_name=None):
        
        dialog = self.builder.get_object("save_as_dialog")
        if suggested_name:
            dialog.set_current_name(suggested_name)
        
        return dialog
    
    
    def get_value_from_liststore(self, column, cell, model, iter, 
                                    user_data=None):
        
        node = model.get(iter, 0)[0]
        
        if cell == self.code_cell:
            cell.set_property('text', node.code)
        elif cell == self.title_cell:
            cell.set_property('text', node.title)
        else:
            raise
    
    
    def on_key_press(self, widget, event, *args):
        if event.keyval == self.keysym_to_fullscreen:
            # The "Full screen" hardware key has been pressed
            window = self.builder.get_object("main_window")
            if self.window_in_fullscreen:
                window.unfullscreen()
            else:
                window.fullscreen()
    
    
    def on_main_window_destroy(self, widget, data=None):
        self.quit()
    
    
    def on_save_as_button_activate(self, widget, data=None):
        
        suggested_name = self.backend.search_string + ".txt"
        chooser = self.get_save_as_dialog(suggested_name=suggested_name)
        
        txt_filter = gtk.FileFilter()
        txt_filter.set_name(_("All Text Files"))
        txt_filter.add_mime_type("text/plain")
        chooser.add_filter(txt_filter)
        
        all_filter = gtk.FileFilter()
        all_filter.set_name(_("All Files"))
        all_filter.add_pattern("*")
        chooser.add_filter(all_filter)

        response = chooser.run()
        if response == gtk.RESPONSE_OK:
            filename = chooser.get_filename()
            chooser.destroy()
        else:
            chooser.destroy()
            return
        
        try:
            encoding = sys.getdefaultencoding()
            f = codecs.open(filename, mode="wb", encoding=encoding,
                             errors='ignore')
            for row in self.search_liststore:
                node = row[0]
                string = u"%(code)s\t%(title)s\n" % (
                    {"code": node.code, "title": node.title})
                f.write(string)
        except IOError, (errno, strerror):
            dialog = gtk.Dialog(\
                 title = _("Error Saving File"),
                 parent = self.window,
                 flags = gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                 buttons = (gtk.STOCK_OK, gtk.RESPONSE_ACCEPT))
            label = gtk.Label(_("It was not possible to save the search "
                "results to the text file. The reason was this input/output "
                "error: %(error_number)d - %(error_description)s") %
                    {"error_number":errno, "error_description": strerror})
            dialog.vbox.pack_start(label)
            dialog.run()
            dialog.destroy()
        finally:
            f.close()
    
    
    def on_search_entry_activate(self, widget, data=None):
        
        button = self.builder.get_object("search_button")
        button.emit("clicked")
    
    
    def on_search_button_clicked(self, widget, data=None):
        entry = self.builder.get_object("search_entry")
        # Strings in GTK+ are encoded in UTF-8, but the backend uses Unicode.
        search_string = entry.get_text().decode("utf-8")
        
        search_thread = self.backend.get_search_thread(search_string)
        
        # If the backend finds a good reason for not starting this search, e.g.
        # because the last search used the exact same terms, then it will return
        # None instead of a Thread object.
        if search_thread:
            self.search_liststore.clear()
            search_thread.start()
            
            self.progressbar.show()
            
            # This button should only be sensitive after a search is made
            save_as_button = self.builder.get_object("save_as_button")
            save_as_button.set_sensitive(True)
    
    
    def on_window_state_change(self, widget, event, *args):
        if event.new_window_state & gtk.gdk.WINDOW_STATE_FULLSCREEN:
            self.window_in_fullscreen = True
        else:
            self.window_in_fullscreen = False
    
    
    def run(self):
        gtk.main()
    
    
    def set_progress(self, fraction):
        self.progressbar.set_fraction(fraction)
        
        # Hide the progressbar if the fraction is set to zero
        if fraction == 0.0:
            self.progressbar.hide()
        return False # so that glib.idle_add won't repeat this callback forever.
