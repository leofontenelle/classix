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



import cPickle
import gobject
import os
import re
import sqlite3
import threading

from classix import config
from classix.common import Node
from classix.common import common_keys
from classix.common import difference_dict
from classix.common import remove_diacritics



class SearchBackend(threading.Thread):
    
    def __init__(self, search_string, frontend):
        
        threading.Thread.__init__(self)
        self.stop_thread = threading.Event()
        
        self.frontend = frontend
        self.database_filename = os.path.join(config.pkgdatadir, "classix.db")
        
        temp_search_string = remove_diacritics(search_string.lower())
        token_list = re.compile(r"\W+", re.U).split(temp_search_string)
        self.token_list = difference_dict(token_list, [u""])
    
    
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
