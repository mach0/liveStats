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
"""
# Import the PyQt and QGIS libraries
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *

import resources_rc

from LSbar import LSbar


class LSliveStats:

    def __init__(self, iface):
        # Save reference to the QGIS interface
        self.iface = iface

        #Will hold the stats bars
        self.statsBars = []
        

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/livestats/icon.png"),
            u"Live Statistics", self.iface.mainWindow())
        # connect the action to the run method
        QObject.connect(self.action, SIGNAL("triggered()"), self.run)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Live Statistics", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Live Statistics", self.action)
        self.iface.removeToolBarIcon(self.action)

        for statsBar in self.statsBars:
            statsBar.setParent(None)
        self.statsBars = []

    # run method that performs all the real work
    def run(self):

        # Create the dialog and keep reference
        newStatsBar = LSbar(self.iface)

        self.iface.mainWindow().addToolBar(Qt.BottomToolBarArea, newStatsBar)
        self.statsBars.append(newStatsBar)


