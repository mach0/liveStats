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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *

from LSwidgetChooseField import LSwidgetChooseField
from LSwidgetChooseLayer import LSwidgetChooseLayer

class LSeditor(QDialog):

    def __init__(self, iface, name):
        QDialog.__init__(self)
        self.setWindowTitle(name)

        self.iface = iface

        self.builder = None


        self.setModal(True)

        #Set layout
        self.layout = QGridLayout()


        #Create widgets
        self.nameUI = QLineEdit(name)
        self.autoNameUI = QCheckBox()
        self.layerUI = LSwidgetChooseLayer(self.iface)
        self.fieldUI = LSwidgetChooseField(self.iface)
        self.functionUI = QComboBox()
        self.selectionUI = QCheckBox()
        self.updateUI = QComboBox()
        self.acceptUI = QPushButton('OK')
        self.cancelUI = QPushButton('Cancel')

        self.functionUI.addItem('Sum')
        self.functionUI.addItem('Mean')
        self.functionUI.addItem('Min')
        self.functionUI.addItem('Max')
        self.functionUI.addItem('Count')

        self.selectionUI.setChecked(True)

        self.updateUI.addItem('always')
        self.updateUI.addItem('on click')

        self.acceptUI.setDefault(True)


        #Layout widgets
        self.layout.addWidget(QLabel('Name'),0,0)
        self.layout.addWidget(self.nameUI,0,1)
        self.layout.addWidget(self.autoNameUI,0,2)
        self.layout.addWidget(QLabel('Layer'),1,0)
        self.layout.addWidget(self.layerUI,1,1,1,2)
        self.layout.addWidget(QLabel('Field'),2,0)
        self.layout.addWidget(self.fieldUI,2,1,1,2)
        self.layout.addWidget(QLabel('Function'),3,0)
        self.layout.addWidget(self.functionUI,3,1,1,2)
        self.layout.addWidget(QLabel('Selection only'),4,0)
        self.layout.addWidget(self.selectionUI,4,1,1,2)
        #self.layout.addWidget(QLabel('Update'),5,0)
        #self.layout.addWidget(self.updateUI,5,1)
        self.layout.addWidget(self.cancelUI,6,0)
        self.layout.addWidget(self.acceptUI,6,1)

        #Connect signals

        QObject.connect(self.autoNameUI,SIGNAL("stateChanged(int)"),self.toggleAutoName)
        QObject.connect(self.layerUI,SIGNAL("currentIndexChanged(int)"),self.createName)
        QObject.connect(self.fieldUI,SIGNAL("currentIndexChanged(int)"),self.createName)
        QObject.connect(self.functionUI,SIGNAL("currentIndexChanged(int)"),self.createName)
        QObject.connect(self.selectionUI,SIGNAL("currentIndexChanged(int)"),self.createName)

        QObject.connect(self.layerUI,SIGNAL("activated(int)"),self.choosedLayerChanged)
        QObject.connect(self.acceptUI,SIGNAL("pressed()"),self.accept)
        QObject.connect(self.cancelUI,SIGNAL("pressed()"),self.reject)

        self.setLayout(self.layout)

    def show(self):
        QDialog.show(self)

        self.layerUI.rebuild()
        self.fieldUI.rebuild( self.layerUI.currentLayer() )

    def choosedLayerChanged(self, index):
        self.fieldUI.rebuild( self.layerUI.currentLayer() )

    def toggleAutoName(self, index):
        if not self.autoNameUI.checkState():
            self.nameUI.setEnabled(True)
        else:
            self.nameUI.setEnabled(False)
            self.createName(0)

    def createName(self, index):
        if self.autoNameUI.checkState():
            func = self.functionUI.currentText()
            field = self.fieldUI.currentText()
            layer = self.layerUI.currentText()

            if self.selectionUI.checkState():
                sel = "'s sel."
            else:
                sel = ''

            name = func + ' of ' + field + ' in ' + layer + sel

            self.nameUI.setText(name)






