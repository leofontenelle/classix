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

from classix.common import remove_diacritics, difference_dict



class BagOfWordsCreator(object):
    
    def __init__(self):
        pass
        
    
    def get_bag_of_words(self, unistr):
        
        temp_string = remove_diacritics(unistr.lower())
        token_list = re.compile(r"\W+", re.U).split(temp_string)
        
        return difference_dict(token_list, [u""])