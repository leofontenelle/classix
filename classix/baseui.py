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



class ClassixUI(gobject.GObject):
    def __init__(self, ui_file_name=None):
        raise NotImplemented
    
    def add_node_to_search(self, node):
        raise NotImplemented
    
    def run(self):
        raise NotImplemented
    
    def set_progress(self, fraction=None):
        raise NotImplemented
