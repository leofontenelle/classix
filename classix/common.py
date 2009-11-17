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



import re
import unicodedata



combining_chars_re = \
    re.compile(u'[\u0300-\u036f\u1dc0-\u1dff\u20d0-\u20ff\ufe20-\ufe2f]',re.U)



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



def remove_diacritics(unistr):
    """Receives an unicode string and returns it without diacritics."""
    
    return combining_chars_re.sub(u'', unicodedata.normalize('NFD', unistr))
    
    """Alternative implementation, 7 times slower:
    
    nkfd_form = unicodedata.normalize('NFKD', unistr)
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])
    """



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



