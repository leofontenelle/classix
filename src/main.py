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


import gobject
import gtk
import os
import sqlite3
import stat
import threading
from . import config

gtk.gdk.threads_init()

def parse_cid10n4a_txt(line):
    """Accepts a line from cid10n4a.txt as argument, and returns the 
    corresponding node object.
    
    
    The following code tells more about the line syntax, but is 60% slower:
    
    # \u2020 = †
    regex = re.compile(ur'^(?P<code>[A-Z][\d]{2}(\.[\d-])?[\u2020*]?)  '
                   '(?P<title>[^|]*)\|  '
                   '(?P<inclusion>(\| [^|]*)*)?'
                   '(\\ (?P<exclusion>[^|]*(\| [^|]*)*))?')
    m = regex.match(line.decode('utf8'))
    code = m.group("code")
    title = m.group("title")
    inclusion = m.group("inclusion")
    exclusion = m.group("exclusion")
    if inclusion:
        inclusion = inclusion.lstrip("| ").replace("| ", "\n").rstrip("\r\n")
    if exclusion:
        exclusion = exclusion.lstrip("| ").replace("| ", "\n").rstrip("\r\n")
    node = Node(code, title, inclusion, exclusion)
    return node
    """
    
    code, sep, rest = line.partition("  ")
    title, sep, rest = rest.partition("|")
    rest = rest.lstrip("| ")
    inclusion, sep, exclusion = rest.partition("\ ")
    inclusion = inclusion.replace("| ", "\n").rstrip("\r\n")
    exclusion = exclusion.replace("| ", "\n").rstrip("\r\n")
    
    node = Node(code, title, inclusion, exclusion)
    
    return node



class Node(object):

    def __init__(self, code, title, inclusion="", exclusion="", comments="",
                    four_characters="", chapter_number="", block_start=""):

        # code without possible dagger, up to 6 characters
        self.code = code

        self.title = title
        self.inclusion = inclusion
        self.exclusion = exclusion
        self.comments = comments

        self.level = "" #FIXME

        """Codes ending with '-' are "not-terminal nodes", i.e. they have
        children codes, and thus are invalid for coding."""
        
        if "-" in self.code:
            self.place = "N" # non-terminal node (not valid for coding)
        else:
            self.place = "T" # terminal node (leaf node, valid for coding)

        if self.place == "N":
            self.type = "V" # not valid for coding
        elif u"*" in self.code:
            self.type = "N" # valid as secondary, optional code
        else:
            self.type = "P" # valid as primary code

        # X = explicitly listed in the classification (pre-combined)
        # S = derived from a subclassification (post-combined)
        self.four_characters = four_characters

        self.chapter_number = chapter_number
        self.block_star = block_start

        self.normalized_code = ""   # FIXME # without possible asterisk
        self.no_dot_code = ""       # FIXME # without dot


class MainWindow (object):

    def __init__(self, ui_file_name):
        self.builder = gtk.Builder()
        self.builder.add_from_file(ui_file_name)
        self.search_liststore = gtk.ListStore(object)

        tv = self.builder.get_object("search_treeview")
        tv.set_model(self.search_liststore)

        code_col = self.builder.get_object("search_tvcol_code")
        code_cell = gtk.CellRendererText()
        code_col.pack_start(code_cell)
        code_col.set_cell_data_func(code_cell, self.get_value_from_liststore)
        tv.append_column(code_col)

        title_col = self.builder.get_object("search_tvcol_title")
        title_cell = gtk.CellRendererText()
        title_col.pack_start(title_cell)
        title_col.set_cell_data_func(title_cell, self.get_value_from_liststore)
        tv.append_column(title_col)

        self.builder.connect_signals(self)
        self.builder.get_object("main_window").show_all()

        self.progress_container = self.builder.get_object("hbox2")
        self.progress_container.hide()

        self.progressbar = self.builder.get_object("progressbar")


    def set_progress(self, fraction):
        self.progressbar.set_fraction(fraction)

        # Hide the progressbar if the fraction is set to zero
        if fraction == 0.0:
            self.progress_container.hide()
        return False # so that glib.idle_add won't repeat this callback forever.


    def add_node_to_search(self, node):
        self.search_liststore.append([node])
        return False # so that glib.idle_add won't repeat this callback forever.
    
    
    def get_value_from_liststore(self, column, cell, model, iter, user_data=None):
        node = model.get(iter, 0)[0]
        if cell == self.builder.get_object("search_tvcol_code").get_cell_renderers()[0]:
            cell.set_property('text', node.code)
        elif cell == self.builder.get_object("search_tvcol_title").get_cell_renderers()[0]:
            cell.set_property('text', node.title)
        else:
            raise

    
    def on_main_window_destroy(self, widget, data=None):
        gtk.main_quit()
    
    
    def on_search_button_clicked(self, widget, data=None):
        entry = self.builder.get_object("search_entry")
        search_string = entry.get_text().lower()
        
        # Don't stop a search or start a new one if there's no search string.
        if not search_string:
            return
        
        # Don't stop a search or start a new one if the current search is the
        # same as the previous search. 
        try:
            if search_string == self.search_thread.search_string:
                return
        except AttributeError:
            # There's no search going on.
            pass
            
        try:
            self.search_thread.stop()
        except AttributeError:
            # There's no search going on.
            pass

        self.search_liststore.clear()
        self.search_thread = SqliteSearch(search_string, self)
        self.search_thread.start()
        
        self.progress_container.show()


    def on_stop_button_clicked(self, widget, data=None):
        try:
            self.search_thread.stop()
        except AttributeError:
            pass
        self.set_progress(0.0)



class SearchBackend(threading.Thread):

    def __init__(self, search_string, frontend):
        self.stop_thread = threading.Event()
        self.search_string = search_string.lower()
        self.frontend = frontend
        threading.Thread.__init__(self)

    def stop(self):
        self.stop_thread.set()
    
    def run(self):
        raise NotImplemented



class SqliteSearch(SearchBackend):

    def __init__(self, search_string, frontend):
        self.database_filename = os.path.join(config.pkgdatadir, "classix.db")
        SearchBackend.__init__(self, search_string, frontend)
    
    
    def run(self):
        
        try:
            self.stop_thread.clear()
            conn = sqlite3.connect(self.database_filename)
            
            cursor = conn.execute("SELECT count(code) FROM codes;")
            total = cursor.fetchone()[0] * 1.0
            fraction = 0.0
            
            cursor = conn.execute("SELECT * FROM codes;")

            # Yes, even Python can use a counter once in a while...
            i = 0
            
            for row in cursor:
                if self.stop_thread.isSet():
                    break
                
                i = i + 1
                node = Node(row[0], row[1], row[2], row[3])

                # Update the progressbar
                new_fraction = round(i / total, 2)
                if new_fraction > fraction:
                    fraction = new_fraction
                    gobject.idle_add(self.frontend.set_progress, fraction)

                if self.search_string in node.code.lower() or \
                   self.search_string in node.title.lower() or \
                   self.search_string in node.inclusion.lower():

                    gobject.idle_add(self.frontend.add_node_to_search, node)
        finally:
            conn.close()
            gobject.idle_add(self.frontend.set_progress, 0)



class SqliteDatabaseCreator (object):
    """Imports the cid10n4a.txt file or some derivative into a SQLite3 database.
    """
    
    def __init__(self, input_file_name):
        """Instantiates the importer; accepts file names and not files.
        cid10n4a.txt here is the official file, encoded with Codepage 1252."""
        
        import codecs
        
        self.input = codecs.open(input_file_name, encoding="cp1252")
    
    
    def run(self):
    
        try:
            conn = sqlite3.connect("classix.db")
            conn.execute("DROP TABLE codes;")
            conn.execute("""CREATE TABLE codes (
                code TEXT PRIMARY KEY COLLATE NOCASE,
                title TEXT NOT NULL COLLATE NOCASE,
                inclusion TEXT COLLATE NOCASE,
                exclusion TEXT COLLATE NOCASE);""")
            
            for line in self.input:
                # line is a Unicode object, not an UTF-8 string.
                node = parse_cid10n4a_txt(line)
                conn.execute("""INSERT INTO codes
                    (code, title, inclusion, exclusion)
                    VALUES
                    (?, ?, ?, ?);""",
                    (node.code, node.title, node.inclusion, node.exclusion))
        finally:
             self.input.close()
             conn.commit()
             conn.close()



if __name__ == "__main__":

    classix = MainWindow(ui_file_name="classix.ui")

    gtk.main()
    
