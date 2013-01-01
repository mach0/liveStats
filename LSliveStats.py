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
import locale

import resources_rc

from LSbar import LSbar


class LSliveStats:

    def __init__(self, iface):
        
        locale.setlocale(locale.LC_ALL, "")

        QgsMessageLog.logMessage('Loading...','LiveStats')

        # Save reference to the QGIS interface
        self.iface = iface

        #Will hold the stats bars
        self.statsBars = []

        # We have to reload the list when a project is opened/closed
        QObject.connect(self.iface, SIGNAL("projectRead()"), self.loadFromFile) 

        #w And we load from file (this should only be usefull if the plugin is loaded when a file is already opened)
        self.loadFromFile()
        

    def initGui(self):
        # Create action that will start plugin configuration
        self.action = QAction(
            QIcon(":/plugins/livestats/icon.png"),
            u"Live Statistics", self.iface.mainWindow())
        # connect the action to the createBar method
        QObject.connect(self.action, SIGNAL("triggered()"), self.createBar)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Live Statistics", self.action)

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Live Statistics", self.action)
        self.iface.removeToolBarIcon(self.action)
        self.removeStatsBars()

    def removeStatsBars(self):
        for statsBar in self.statsBars:
            statsBar.setParent(None)
        self.statsBars = []


    def createBar(self):
        #This creates a default new bar
        newStatsBar = LSbar(self.iface, True)
        self.addBar(newStatsBar)

    def addBar(self, lsBar):
        # This adds a bar to the project
        self.iface.mainWindow().addToolBar(Qt.BottomToolBarArea, lsBar)
        self.statsBars.append(lsBar)
        QObject.connect(lsBar.dialog, SIGNAL('accepted()'), self.saveToFile)

    def saveToFile(self):
        saveStringsLists = []
        for statsBar in self.statsBars:
            saveStringsLists.append(statsBar.save())
        QgsProject.instance().writeEntry('LiveStats','SavedStats',saveStringsLists)

    def loadFromFile(self):
        self.removeStatsBars()

        loadedStringsLists = QgsProject.instance().readListEntry('LiveStats','SavedStats')[0]
        for loadString in loadedStringsLists:
            newStatsBar = LSbar(self.iface, False)
            newStatsBar.load(loadString)
            self.addBar(newStatsBar)

    




