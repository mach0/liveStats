# -*- coding: utf-8 -*-
"""
/***************************************************************************
 LiveStats
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
 This script initializes the plugin, making it known to QGIS.
"""


def name():
    return "Live Statistics"


def description():
    return "LiveStats allows to display simple statistics about vector data in small toolbars that provide real-time feedback."


def version():
    return "Version 0.2"


def icon():
    return "icon.png"


def qgisMinimumVersion():
    return "1.8"

def author():
    return "Olivier Dalang"

def email():
    return "olivier.dalang@gmail.com"

def classFactory(iface):
    # load LiveStats class from file LiveStats
    from LSliveStats import LSliveStats
    return LSliveStats(iface)
