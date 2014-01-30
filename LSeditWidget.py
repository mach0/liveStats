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

from QgsLayerComboBox import QgsLayerComboBox


class LSeditWidget(QWidget):

    def __init__(self, iface, lsStat):
        QWidget.__init__(self)

        self.iface = iface
        self.lsStat = lsStat

        self.setWindowModality(Qt.ApplicationModal)

        # Connect the signals
        self.lsStat.settingsChanged.connect( self.refreshSettings )

        # Create the widgets
        self.nameWidget = QLineEdit()
        self.layerWidget = QgsLayerComboBox(self.iface)
        self.expressionWidget = QLineEdit()
        self.expressionEditWidget = QPushButton("...")
        self.limittoselectionWidget = QCheckBox()
        self.autoupdateWidget = QCheckBox()

        # Connect the widgets
        self.nameWidget.textChanged.connect( self.lsStat.setName )
        self.layerWidget.currentLayerChanged.connect( self.lsStat.setLayer )
        self.expressionWidget.textChanged.connect( self.lsStat.setExpression )
        self.expressionEditWidget.pressed.connect( lambda: self.expressionWidget.setText( self.runExpressioBuilderDialog() )  )

        # Layout the widgets
        layout = QGridLayout()
        self.setLayout(layout)

        l=0
        layout.addWidget(QLabel("name"),               l,0  ,  1,1 )
        layout.addWidget(self.nameWidget,              l,1  ,  1,2 )

        l+=1
        layout.addWidget(QLabel("layer"),              l,0  ,  1,1 )
        layout.addWidget(self.layerWidget,             l,1  ,  1,2 )

        l+=1
        layout.addWidget(QLabel("expression"),         l,0  ,  1,1 )
        layout.addWidget(self.expressionWidget,        l,1  ,  1,1 )
        layout.addWidget(self.expressionEditWidget,    l,2  ,  1,1 )
        
        l+=1
        layout.addWidget(QLabel("limit to selection"), l,0  ,  1,1 )
        layout.addWidget(self.limittoselectionWidget,  l,1  ,  1,2 )
        
        l+=1
        layout.addWidget(QLabel("auto-update"),        l,0  ,  1,1 )
        layout.addWidget(self.autoupdateWidget,        l,1  ,  1,2 )

    def refreshSettings(self):
        self.nameWidget.setText( self.lsStat.name )
        self.layerWidget.setCurrentLayer( self.lsStat.layer )
        self.expressionWidget.setText( self.lsStat.expression )
        self.limittoselectionWidget.setChecked( self.lsStat.limittoselection )
        self.autoupdateWidget.setChecked( self.lsStat.autoupdate )

    def refreshResult(self):
        pass

    def runExpressioBuilderDialog(self):
        dlg = QgsExpressionBuilderDialog(self.lsStat.usedLayer, self.expressionWidget.text() )
        if dlg.exec_():
            return dlg.expressionText()

