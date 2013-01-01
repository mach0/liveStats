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



class LScomputer():
    def __init__(self):
        pass
    def addVal(self, val):
        pass
    def result(self):
        return 0
class LScountComputer(LScomputer):
    def __init__(self):
        self.val = 0
    def addVal(self, val):
        self.val += 1
    def result(self):
        return self.val
class LSsumComputer(LScomputer):
    def __init__(self):
        self.val = 0
    def addVal(self, val):
        self.val += val
    def result(self):
        return self.val
class LSminComputer(LScomputer):
    def __init__(self):
        self.val = 0
        self.first = True
    def addVal(self, val):
        if self.first:
            self.val = val
            self.first = False
        else:
            self.val = min(val, self.val)
    def result(self):
        return self.val
class LSmaxComputer(LScomputer):
    def __init__(self):
        self.val = 0
        self.first = True
    def addVal(self, val):
        if self.first:
            self.val = val
            self.first = False
        else:
            self.val = max(val, self.val)
    def result(self):
        return self.val
class LSmeanComputer(LScomputer):
    def __init__(self):
        self.val = 0
        self.count = 0
    def addVal(self, val):
        self.val += val
        self.count += 1
    def result(self):
        if self.count == 0:
            return 'div by 0 !'
        else:
            return self.val / self.count