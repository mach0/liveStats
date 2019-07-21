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
from qgis.PyQt.QtCore import Qt
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction
from qgis.core import QgsProject

# don't delete following import
from . import resources_rc

from .LSbar import LSbar
from .LSaboutWindow import LSaboutWindow


class LSmain:
    def __init__(self, iface):
        # QgsMessageLog.logMessage('Loading the plugin...','LiveStats')
        # Save reference to the QGIS interface
        self.iface = iface
        # Will hold the stats bars
        self.statsBars = []
        # We have to load the list when a project is opened
        self.iface.projectRead.connect(self.loadFromFile)
        # We have to emtpy the list when a new project is created
        self.iface.newProjectCreated.connect(self.removeAllBars)
        # We have to save the list when the project is written
        QgsProject.instance().writeProject.connect(self.saveToFile)

        # TODO : this is triggered at the moment the file is read,
        # and the layer then load one after the other
        # This makes the liveStats to compute for every layer at loading,
        # which is useless and slows down the loading

        # is this possible ?
        # And we load from file (this should only be useful if the plugin is loaded when a file is already opened)
        self.loadFromFile()

    def initGui(self):
        # LiveStats Action

        # Create actions
        self.action = QAction(QIcon(":/plugins/livestats/img/icon.png"),
                              u"Create new LiveStats", self.iface.mainWindow())
        self.helpAction = QAction(QIcon(":/plugins/livestats/img/about.png"),
                                  u"Help", self.iface.mainWindow())
        self.hideAllAction = QAction(u"Hide all LiveStats", self.hideAll())
        self.showAllAction = QAction(u"Show all LiveStats", self.showAll())

        # Connect the actions
        self.action.triggered.connect(self.createBar)
        self.helpAction.triggered.connect(self.showHelp)
        self.hideAllAction.triggered.connect(self.hideAll)
        self.showAllAction.triggered.connect(self.showAll)

        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Live Statistics", self.action)
        self.iface.addPluginToMenu(u"&Live Statistics", self.helpAction)
        self.iface.addPluginToMenu(u"&Live Statistics", self.showAllAction)
        self.iface.addPluginToMenu(u"&Live Statistics", self.hideAllAction)

    def showHelp(self):
        # Simply show the help window
        self.aboutWindow = LSaboutWindow()

    def showAll(self):
        # Simply show the help window
        for statsBar in self.statsBars:
            statsBar.show()

    def hideAll(self):
        # Simply show the help window
        for statsBar in self.statsBars:
            statsBar.hide()

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Live Statistics", self.action)
        self.iface.removePluginMenu(u"&Live Statistics", self.helpAction)
        self.iface.removePluginMenu(u"&Live Statistics", self.showAllAction)
        self.iface.removePluginMenu(u"&Live Statistics", self.hideAllAction)
        self.iface.removeToolBarIcon(self.action)
        self.removeAllBars()

    def createBar(self):
        # This creates a default new bar
        newStatsBar = LSbar(self.iface, self, True)
        self.addBar(newStatsBar)

    def addBar(self, lsBar):
        # This adds a bar to the project
        self.iface.mainWindow().addToolBar(Qt.BottomToolBarArea, lsBar)
        if lsBar.position['floating']:
            lsBar.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
            lsBar.move(lsBar.position['x'], lsBar.position['y'])
        # We add it to this array (useful for looping through all bars)
        self.statsBars.append(lsBar)

    def removeBar(self, lsBar):
        self.iface.mainWindow().removeToolBar(lsBar)
        self.statsBars.remove(lsBar)

    def removeAllBars(self):
        for statsBar in self.statsBars:
            statsBar.setParent(None)
        self.statsBars = []

    def saveToFile(self):
        # QgsMessageLog.logMessage('Saving to file...','LiveStats')
        saveStringsLists = []
        for statsBar in self.statsBars:
            saveStringsLists.append(statsBar.save())

        # TODO : sometimes there's the following error : AttributeError: 'NoneType' object has no attribute 'instance'
        # if QgsProject.instance() is not None:
        # Don't know if it's ok to uncomment this : won't it make save silently fail sometimes ?
        QgsProject.instance().writeEntry('LiveStats', 'SavedStats', saveStringsLists)

    def loadFromFile(self):
        # QgsMessageLog.logMessage('Loading from file...','LiveStats')
        self.removeAllBars()

        loadedStringsLists = QgsProject.instance().readListEntry('LiveStats', 'SavedStats')[0]
        for loadString in loadedStringsLists:
            # QgsMessageLog.logMessage('Loading a stats !','LiveStats')
            newStatsBar = LSbar(self.iface, self, False)
            newStatsBar.load(loadString)
            self.addBar(newStatsBar)
