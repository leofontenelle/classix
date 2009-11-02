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
import cPickle
import gobject
import gtk
import os
import re
import sqlite3
import sys
import time
import threading
from . import config

import gettext
_ = gettext.gettext
## intltool-tool won't understand this:
# N_ = gettext.ngettext


gtk.gdk.threads_init()



def common_keys(dictionaries_list = []):
    """Returns a list of the keys that exist in every dictionary included in the
    provided list."""
    
    class SomeDictDoesntHaveThisKey(Exception):
        pass
    
    result = []
    
    for key in dictionaries_list[0]:
        try:
            for dictionary in dictionaries_list[1:]:
                if not dictionary.has_key(key):
                    raise SomeDictDoesntHaveThisKey
            result.append(key)
        except SomeDictDoesntHaveThisKey:
            pass
    
    return result


def difference_dict(a,b):
    """Returns a list of the items that exist in the first provided list but 
    not in the second provided list."""
    
    result = {}
    
    for element in a:
        result[element]=1
        for element in b:
            if result.has_key(element):
                del result[element]
    
    return result.keys()



def parse_cid10n4a_txt(line):
    """Accepts a line from cid10n4a.txt as argument, and returns the 
    corresponding node object.
    
    
    The following code tells more about the line syntax, but is 60% slower:
    
    # \u2020 = †
    regex = re.compile(ur'^(?P<code>[A-Z][\d]{2}(\.[\d-])?[\u2020*]?)  '
                   '(?P<title>[^|]*)\|  '
                   '(?P<inclusion>(\| [^|]*)*)?'
                   '(\\ (?P<exclusion>[^|]*(\| [^|]*)*))?')
    m = regex.match(line)
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
        self.window_in_fullscreen = False
        self.keysym_to_fullscreen = gtk.keysyms.F11

        self.progressbar = self.builder.get_object("progressbar")
        self.progressbar.hide()
    
    
    def add_node_to_search(self, node):
        self.search_liststore.append([node])
        return False # so that glib.idle_add won't repeat this callback forever.
    
    
    def _get_renderer(self, tv_column):
            return self.builder.get_object(tv_column).get_cell_renderers()[0]
    
    
    def get_value_from_liststore(self, column, cell, model, iter, user_data=None):
        
        node = model.get(iter, 0)[0]
        
        if cell == self._get_renderer("search_tvcol_code"):
            cell.set_property('text', node.code)
        elif cell == self._get_renderer("search_tvcol_title"):
            cell.set_property('text', node.title)
        else:
            raise
    
    
    def on_key_press(self, widget, event, *args):
        if event.keyval == self.keysym_to_fullscreen:
            # The "Full screen" hardware key has been pressed
            window = self.builder.get_object("main_window")
            if self.window_in_fullscreen:
                window.unfullscreen ()
            else:
                window.fullscreen ()
    
    
    def on_main_window_destroy(self, widget, data=None):
        gtk.main_quit()
    
    
    def on_search_entry_activate(self, widget, data=None):
        
        button = self.builder.get_object("search_button")
        button.emit("clicked")
    
    
    def on_search_button_clicked(self, widget, data=None):
        entry = self.builder.get_object("search_entry")
        # Strings in GTK+ are encoded in UTF-8, but the backend uses Unicode.
        search_string = entry.get_text().decode("utf-8")
        
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
        
        self.progressbar.show()
    
    
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



class HildonMainWindow(MainWindow):
    
    def __init__(self, ui_file_name):
        
        MainWindow.__init__(self, ui_file_name)
        self.keysym_to_fullscreen = gtk.keysyms.F6
        
        toolbar = self.builder.get_object("search_toolbar")
        vbox = self.builder.get_object("vbox1")
        vbox.set_child_packing(child=toolbar, expand=False, fill=True, 
            padding=0, pack_type = gtk.PACK_END)



class CommandLineInterface(gobject.GObject):
    
    def __init__(self):
        
        # Make sure the standard output accepts non-ascii encoding even
        # if it's not printing to the terminal. This is necessary, in example,
        # when the output is redirected to a text file.
        encoding = sys.getdefaultencoding()
        sys.stdout = codecs.getwriter(encoding)(sys.stdout)
        
        from optparse import OptionParser
        
        # Translators: Leave '%prog' untranslated; and keep single or double
        # quotes around the translation of 'text to be searched'.
        usage = _("usage: %prog [ OPTIONS ] \"text to be searched\" "
                  "- Search for ICD-10 codes")
        epilog=_("If you want to open the graphical user interface, just run "
            "\"classix\". If you want the results to be printed to the "
            "standard output (e.g. the terminal), specify the text to be "
            "searched as an argument between quotes.")
        parser = OptionParser(version=config.VERSION, epilog=epilog)
        parser.set_usage(usage)
        parser.add_option("-t", "--time", action="store_true", dest="time",
            help=_("shows how long it took to search the text"))
        (options, args) = parser.parse_args()
        self.time = options.time
        
        if not args:
            # e.g. the user passed "-t" without any text.
            parser.print_usage()
            sys.exit(1)
        
        # The command line parser is used for:
        # 1. get -h, --help flags, which are implicit; and
        # 2. get argv[1], which is the search string
        self.search_string = args[0].decode(encoding).lower()
    
    
    def add_node_to_search(self, node):
        # TODO: use the appropriate end-of-line for the current OS.
        sys.stdout.write("%(code)s\t%(title)s\n" % (
            {"code": node.code, "title": node.title}))
        return False
    
    
    def run(self):
        
        self.search_thread = SqliteSearch(self.search_string, self)
        self.search_thread.start()
        if self.time: self.start_time = time.time()

        gtk.main()
    
    
    def set_progress(self, fraction=None):
        if fraction == 0.0:
            import time
            if self.time:
                self.end_time = time.time()
                delta = self.end_time - self.start_time
                print gettext.ngettext(
                    "[%.04f second]", "[%.04f seconds]", delta) % delta
            gtk.main_quit()
        else:
            return False



class SearchBackend(threading.Thread):
    
    def __init__(self, search_string, frontend):
        self.stop_thread = threading.Event()
        self.search_string = search_string.lower()
        self.frontend = frontend
        threading.Thread.__init__(self)
    
    def run(self):
        raise NotImplemented
    
    def stop(self):
        self.stop_thread.set()



class SqliteSearch(SearchBackend):
    
    def __init__(self, search_string, frontend):
        
        SearchBackend.__init__(self, search_string, frontend)
        
        self.database_filename = os.path.join(config.pkgdatadir, "classix.db")
        
        self.token_list = re.compile(r"\W+", re.U).split(self.search_string)
        self.token_list = difference_dict(self.token_list, [u""])
    
    
    def run(self):
        
        conn = sqlite3.connect(self.database_filename)
        
        class StopTheThread(Exception):
            """Exception used to stop a thread"""
            pass
            
        try:
            
            self.stop_thread.clear()
            
            # Step 1: Retrieve the codes for the words searched
            #
            # Here we use a nested dictionary, because comparing dictionary
            # keys is faster than comparing list items (because the dictionaries
            # are hashed); and because we will have an arbitrary number of 
            # tokens to be searched for, and a variable number of codes for 
            # each token.
            
            codes_dict = {}
            
            for token in self.token_list:
                
                if self.stop_thread.isSet(): raise StopTheThread
                
                codes_dict[token] = {}
                
                statement = u"""SELECT code_list from word_index 
                                WHERE word LIKE ?;"""
                cursor = conn.execute(statement, [u"%" + token + u"%"])
                
                for row in cursor:
                    
                    if self.stop_thread.isSet(): raise StopTheThread
                    
                    code_list = cPickle.loads(str(row[0]))
                    
                    for item in code_list:
                        
                        if self.stop_thread.isSet(): raise StopTheThread
                        
                        # We don't want a code added to the list twice. 
                        # Using a dictionary is faster and easier than checking 
                        # if the list has an item.
                        codes_dict[token][item] = True
            
            # Step 2: Build a single code list.
            #
            # codes_dict.value() will return a list which items are 
            # dictionaries, and the dictionaries pairs are something like 
            # ("A09", True).
            codes = common_keys(codes_dict.values())
            
            if self.stop_thread.isSet(): raise StopTheThread
            
            # Dictionary keys can't be sorted, only list items.
            codes.sort()
            
            
            # Step 3: Retrieve the nodes for each code
            
            if not codes: raise StopTheThread
            
            codes_fraction = 1.0 / len(codes)
            fraction = 0.0
            
            statement = u"SELECT * FROM codes WHERE code == ?;"
            
            for code in codes:
                
                if self.stop_thread.isSet(): raise StopTheThread
                
                cursor = conn.execute(statement, [code])
                
                for row in cursor:
                    
                    if self.stop_thread.isSet(): raise StopTheThread
                    
                    node = Node(row[0], row[1], row[2], row[3])
                    gobject.idle_add(self.frontend.add_node_to_search, node)
                
                fraction = fraction + codes_fraction
                if fraction > 1.0:
                    fraction = 1.0
                gobject.idle_add(self.frontend.set_progress, fraction)
        
        except StopTheThread:
            pass
        
        finally:
            
            conn.close()
            gobject.idle_add(self.frontend.set_progress, 0.0)



class SqliteDatabaseCreator (object):
    """Imports the cid10n4a.txt file or some derivative into a SQLite3 database.
    """
    
    def __init__(self, input_file_name):
        """Instantiates the importer; accepts file names and not files.
        cid10n4a.txt here is the official file, encoded with Codepage 1252."""
        
        import codecs
        
        self.input = codecs.open(input_file_name, encoding="cp1252")
    
    
    def run(self):
    
        index = {}
    
        try:
            conn = sqlite3.connect("classix.db")
            try:
                conn.execute(u"DROP TABLE codes;")
            except sqlite3.OperationalError:
                pass
            conn.execute(u"""CREATE TABLE codes (
                code TEXT PRIMARY KEY COLLATE NOCASE,
                title TEXT NOT NULL COLLATE NOCASE,
                inclusion TEXT COLLATE NOCASE,
                exclusion TEXT COLLATE NOCASE);""")
            
            for line in self.input:
                # line is a Unicode object, not an UTF-8 string.
                node = parse_cid10n4a_txt(line)
                conn.execute(u"""INSERT INTO codes
                    (code, title, inclusion, exclusion)
                    VALUES
                    (?, ?, ?, ?);""",
                    (node.code, node.title, node.inclusion, node.exclusion))
            
            cursor = conn.execute(u"SELECT * FROM codes;")

            for row in cursor:
                node = Node(row[0], row[1], row[2], row[3])
                for attribute in [u"code", u"title", u"inclusion"]:
                    string = node.__getattribute__(attribute)
                    words = re.compile(r"\W+", re.U).split(string)
                    for raw_word in words:
                        if raw_word == u"": continue
                        word = raw_word.lower()
                        try:
                            index[word][node.code] = True
                        except KeyError:
                            index[word] = {node.code: True}

            try:
                conn.execute(u"DROP TABLE word_index;")
            except sqlite3.OperationalError:
                pass

            conn.execute(u"""CREATE TABLE word_index (
                word TEXT PRIMARY KEY COLLATE NOCASE,
                code_list TEXT NOT NULL COLLATE NOCASE);""")

            index_keys = index.keys()
            index_keys.sort()

            for key in index_keys:
                codes = index[key].keys()
                codes.sort()
                conn.execute(u"""INSERT INTO word_index (word, code_list)
                    VALUES (?, ?);""", (key, cPickle.dumps(codes)))
        finally:
             self.input.close()
             conn.commit()
             conn.close()



if __name__ == "__main__":

    classix = CommandLineInterface()
    classix.run()
