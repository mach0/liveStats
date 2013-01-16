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

        QgsMessageLog.logMessage('Loading the plugin...','LiveStats')


        # Save reference to the QGIS interface
        self.iface = iface

        #Will hold the stats bars
        self.statsBars = []

        # We have to reload the list when a project is opened/closed
        #QObject.connect(self.iface, SIGNAL("projectRead()"), self.loadFromFile)

        QObject.connect(self.iface, SIGNAL("newProjectCreated()"), self.removeStatsBars)
        QObject.connect(self.iface, SIGNAL("projectRead()"), self.loadFromFile)
        #QObject.connect(QgsProject.instance(), SIGNAL("readProject(QDomDocument &)"), self.loadFromFile)
        QObject.connect(QgsProject.instance(), SIGNAL("writeProject(QDomDocument &)"), self.saveToFile)

        # TODO : this is triggered at the moment the file is read,
        # and the layer then load one after the other
        # This makes the liveStats to compute for every layer at loading,
        # which is useless and slows down the loading

        # it is necessary to remove the stats bars when the project is closed
        # and to load them once it is completely loaded only

        # is this possible ?

        # Is this better?
        #QObject.connect(self.iface, SIGNAL("initializationCompleted()"), self.loadFromFile) 

        #projectSaved()
        



        #w And we load from file (this should only be usefull if the plugin is loaded when a file is already opened)
        self.loadFromFile()
        

    def initGui(self):
        # LiveStats Action
        # Create action that will start plugin configuration
        self.action = QAction( QIcon(":/plugins/livestats/icon.png"), u"Live Statistics", self.iface.mainWindow() )
        # connect the action to the createBar method
        QObject.connect(self.action, SIGNAL("triggered()"), self.createBar)
        # Add toolbar button and menu item
        self.iface.addToolBarIcon(self.action)
        self.iface.addPluginToMenu(u"&Live Statistics", self.action)

        self.initHelp()


    def initHelp(self):
        # Help Action
        # Create action 
        self.helpAction = QAction( QIcon(":/plugins/livestats/about.png"), u"Help", self.iface.mainWindow())
        # connect the action 
        QObject.connect(self.helpAction, SIGNAL("triggered()"), self.showHelp)
        # Add menu item
        self.iface.addPluginToMenu(u"&Live Statistics", self.helpAction)

    def showHelp(self):
        # Simply show the help window
        self.aboutWindow = LSaboutWindow()


    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(u"&Live Statistics", self.action)
        self.iface.removePluginMenu(u"&Live Statistics", self.helpAction)
        self.iface.removeToolBarIcon(self.action)
        self.removeStatsBars()

    def removeStatsBars(self):
        for statsBar in self.statsBars:
            statsBar.setParent(None)
        self.statsBars = []


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

        #EDIT THIS IS USELESS; SAVE ONLY ON FILE CLOSE !
        #QObject.connect(lsBar.dialog, SIGNAL('accepted()'), self.saveToFile)

    def removeBar(self, lsBar):
        self.iface.mainWindow().removeToolBar(lsBar)
        self.statsBars.remove(lsBar)


    def saveToFile(self):
        QgsMessageLog.logMessage('Saving to file...','LiveStats')
        saveStringsLists = []
        for statsBar in self.statsBars:
            #if statsBar.saveWith:
            saveStringsLists.append(statsBar.save())
        #TODO : sometimes there's a bug :
        # AttributeError: 'NoneType' object has no attribute 'instance'
        QgsProject.instance().writeEntry('LiveStats','SavedStats',saveStringsLists)

    def loadFromFile(self):
        QgsMessageLog.logMessage('Loading from file...','LiveStats')
        self.removeStatsBars()

        loadedStringsLists = QgsProject.instance().readListEntry('LiveStats','SavedStats')[0]
        for loadString in loadedStringsLists:
            QgsMessageLog.logMessage('Loading a stats !','LiveStats')
            newStatsBar = LSbar(self.iface, self, False)
            newStatsBar.load(loadString)
            self.addBar(newStatsBar)



    




