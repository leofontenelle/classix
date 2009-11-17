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
import time

from classix.baseui import ClassixUI
from classix import config
from classix.searchbackend import SearchBackend
from gettext import ngettext
from gettext import gettext as _
from optparse import OptionParser



class CommandLineInterface(ClassixUI):
    
    def __init__(self):
        
        ClassixUI.__init__(self)
        
        # Make sure the standard output accepts non-ascii encoding even
        # if it's not printing to the terminal. This is necessary, in example,
        # when the output is redirected to a text file.
        encoding = sys.getdefaultencoding()
        sys.stdout = codecs.getwriter(encoding)(sys.stdout)
        
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
        return False # so that glib.idle_add won't repeat this callback forever.
    
    
    def run(self):
        
        search_thread = self.backend.get_search_thread(self.search_string)
        if self.time: self.start_time = time.time()
        search_thread.start()
        
        
        gtk.main()
    
    
    def set_progress(self, fraction=None):
        if fraction == 0.0:
            import time
            if self.time:
                self.end_time = time.time()
                delta = self.end_time - self.start_time
                print ngettext(
                    "[%.04f second]", "[%.04f seconds]", delta) % delta
            self.quit()
        else:
            return False # so that glib.idle_add won't repeat this callback forever.
