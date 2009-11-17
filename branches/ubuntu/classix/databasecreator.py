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
from classix.common import Node
import re
from classix.common import remove_diacritics
import sqlite3




class DatabaseCreator (object):
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
                        word = remove_diacritics(raw_word.lower())
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
