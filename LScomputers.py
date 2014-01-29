# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LiveStatsDialog
                                 A QGIS plugin
 Display live statistics about vector selections
                             -------------------
        begin                : 2012-12-30
        copyright            : (C) 2012 by Olivier Dalang
        email                : olivier.dalang@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from PyQt4.QtCore import QVariant
from PyQt4.QtCore import QStringList
from PyQt4.QtCore import QString


class LScomputer():
    def __init__(self):
        self.formatter = lambda x: x
    def addVal(self, val):
        pass
    def result(self):
        return 0
    #@classmethod
    #def acceptsType(cls, type):
    #    return True

class LScomputerCount(LScomputer):
    def __init__(self):
        self.val = 0
    def addVal(self, val):
        self.val += 1
    def result(self):
        return str(self.val)

class LScomputerNonNull(LScomputer):
    def __init__(self):
        self.val = 0
    def addVal(self, val):
        if not val.isNull():
            self.val += 1
    def result(self):
        return str(self.val)

class LScomputerSum(LScomputer):
    def __init__(self):
        self.val = 0
    def addVal(self, val):
        val, ok = val.toDouble()
        self.val += val
    def result(self):
        return self.formatter(self.val)

class LScomputerMin(LScomputer):
    def __init__(self):
        self.val = 0
        self.first = True
    def addVal(self, val):
        val, ok = val.toDouble()
        if self.first:
            self.val = val
            self.first = False
        else:
            self.val = min(val, self.val)
    def result(self):
        return self.formatter(self.val)

class LScomputerMax(LScomputer):
    def __init__(self):
        self.val = 0
        self.first = True
    def addVal(self, val):
        val, ok = val.toDouble()
        if self.first:
            self.val = val
            self.first = False
        else:
            self.val = max(val, self.val)
    def result(self):
        return self.formatter(self.val)

class LScomputerMean(LScomputer):
    def __init__(self):
        self.val = 0
        self.count = 0
    def addVal(self, val):
        val, ok = val.toDouble()
        self.val += val
        self.count += 1
    def result(self):
        if self.count == 0:
            return '-'
        else:
            return self.formatter(self.val / self.count)
            
class LScomputerConcat(LScomputer):
    def __init__(self):
        self.val = QStringList()
    def addVal(self, val):

        convVal, ok = val.toDouble()
        if ok:
            val = self.formatter(convVal)
        else:
            val = val.toString()
        self.val.append(val)
    def result(self):
        return self.val.join(', ')

            
class LScomputerUniqueConcat(LScomputer):
    def __init__(self):
        from sets import Set
        self.val = Set()
    def addVal(self, val):

        convVal, ok = val.toDouble()
        if ok:
            val = self.formatter(convVal)
        else:
            val = val.toString()
        self.val.add(val)
    def result(self):
        returnArray = []
        return QStringList(list(self.val)).join(', ')