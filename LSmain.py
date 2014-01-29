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
from LSaboutWindow import LSaboutWindow


class LSmain:

    def __init__(self, iface):

        #QgsMessageLog.logMessage('Loading the plugin...','LiveStats')


        # Save reference to the QGIS interface
        self.iface = iface

        #Will hold the stats bars
        self.statsBars = []

        # We have to load the list when a project is opened
        QObject.connect(self.iface, SIGNAL("projectRead()"), self.loadFromFile)

        # We have to emtpy the list when a new project is created
        QObject.connect(self.iface, SIGNAL("newProjectCreated()"), self.removeAllBars)

        # We have to save the list when the project is written
        QObject.connect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.saveToFile)

        # TODO : this is triggered at the moment the file is read,
        # and the layer then load one after the other
        # This makes the liveStats to compute for every layer at loading,
        # which is useless and slows down the loading

        # is this possible ?
        #QObject.connect(self.iface, SIGNAL("initializationCompleted()"), self.loadFromFile) 

        #w And we load from file (this should only be usefull if the plugin is loaded when a file is already opened)
        self.loadFromFile()
        

    def initGui(self):
        # LiveStats Action

        # Create actions
        self.action = QAction( QIcon(":/plugins/livestats/icon.png"), u"Create new LiveStats", self.iface.mainWindow() )
        self.helpAction = QAction( QIcon(":/plugins/livestats/about.png"), u"Help", self.iface.mainWindow())
        self.hideAllAction = QAction( u"Hide all LiveStats", self.hideAll())
        self.showAllAction = QAction( u"Show all LiveStats", self.showAll())

        # Connect the actions
        QObject.connect(self.action, SIGNAL("triggered()"), self.createBar)
        QObject.connect(self.helpAction, SIGNAL("triggered()"), self.showHelp)
        QObject.connect(self.hideAllAction, SIGNAL("triggered()"), self.hideAll)
        QObject.connect(self.showAllAction, SIGNAL("triggered()"), self.showAll)

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
        #This creates a default new bar
        newStatsBar = LSbar(self.iface, self, True)
        self.addBar(newStatsBar)

    def addBar(self, lsBar):
        # This adds a bar to the project

        self.iface.mainWindow().addToolBar(Qt.BottomToolBarArea, lsBar)
        if lsBar.position['floating']:
            lsBar.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint);
            lsBar.move( lsBar.position['x'], lsBar.position['y'] )
            #lsBar.restoreGeometry( lsBar.storedGeometry )
            #QgsMessageLog.logMessage('Positionned ! %f ; %f' % (lsBar.position['x'], lsBar.position['y']),'LiveStats')

        # We add it to this array (usefull for looping through all bars)
        self.statsBars.append(lsBar)


    def removeBar(self, lsBar):
        self.iface.mainWindow().removeToolBar(lsBar)
        self.statsBars.remove(lsBar)


    def removeAllBars(self):
        for statsBar in self.statsBars:
            statsBar.setParent(None)
        self.statsBars = []


    def saveToFile(self):
        #QgsMessageLog.logMessage('Saving to file...','LiveStats')
        saveStringsLists = []
        for statsBar in self.statsBars:
            saveStringsLists.append(statsBar.save())

        #TODO : sometimes there's the following error : AttributeError: 'NoneType' object has no attribute 'instance'
        #if QgsProject.instance() is not None: #Don't know if it's ok to uncomment this : won't it make save silently fail sometimes ?
        QgsProject.instance().writeEntry('LiveStats','SavedStats',saveStringsLists)

    def loadFromFile(self):
        #QgsMessageLog.logMessage('Loading from file...','LiveStats')
        self.removeAllBars()

        loadedStringsLists = QgsProject.instance().readListEntry('LiveStats','SavedStats')[0]
        for loadString in loadedStringsLists:
            #QgsMessageLog.logMessage('Loading a stats !','LiveStats')
            newStatsBar = LSbar(self.iface, self, False)
            newStatsBar.load(loadString)
            self.addBar(newStatsBar)



    




