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
from qgis.gui import *


class LSbarWidget(QToolBar):

    def __init__(self, iface, lsStat):
        QWidget.__init__(self)

        self.iface = iface
        self.lsStat = lsStat

        # Connect the signals
        self.lsStat.settingsChanged.connect( self.refreshSettings )
        self.lsStat.resultChanged.connect( self.refreshResult )

        # Create the widgets
        self.nameWidget = QToolButton()
        self.countWidget = QLabel()
        self.resultWidget = QToolButton()

        # Connect the widgets to their actions
        self.nameWidget.pressed.connect(self.lsStat.showEditWidget)
        self.resultWidget.pressed.connect(self.lsStat.recompute)

        # Layout the widgets
        self.addWidget(self.nameWidget)
        self.addWidget(self.countWidget)
        self.addWidget(self.resultWidget)

        # Add the toolbar to the mainWindow
        self.iface.mainWindow().addToolBar( Qt.BottomToolBarArea, self )

    def refreshSettings(self):
        self.nameWidget.setText( self.lsStat.name )
        self.setWindowTitle( " '"+self.lsStat.name+"'" )

    def refreshResult(self):
        self.resultWidget.setText( str( self.lsStat.result ) )
        self.countWidget.setText( "(%i)" % self.lsStat.count )
