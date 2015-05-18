# -*- coding: utf-8 -*-

# xml_functions.py
#
# Copyright (C) 2015 Fabian Wenzelmann <fabianwenzelmann(at)posteo.de>
#
# This file is part of stura-voting.
#
# stura-voting is free software: you
# can redistribute it and/or modify it under the terms of the
# GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
#
# stura-voting is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General
# Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with stura-voting.
#
# If not, see <http://www.gnu.org/licenses/>.
#

import xml.dom.minidom as minidom
import xml.etree.ElementTree


def prettify(elem, encoding='utf-8'):
    """Return a pretty-printed XML string for the Element."""
    _str = xml.etree.ElementTree.tostring(elem, encoding)
    return minidom.parseString(_str).toprettyxml(indent=' ')


def getSingletonElement(node, elementName):
    lst = node.getElementsByTagName(elementName)
    if len(lst) != 1:
        return None
    else:
        return lst[0]
