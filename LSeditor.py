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

    def __init__(self, iface):
        QDialog.__init__(self)

        self.iface = iface

        self.setModal(True)

        #Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)


        #Create widgets
        self.nameUI = QLineEdit()
        self.autoNameUI = QCheckBox()

        self.layerUI = LSwidgetChooseLayer(self.iface)
        self.fieldUI = LSwidgetChooseField(self.iface)
        self.functionUI = QComboBox()
        self.selectionUI = QCheckBox()

        self.precisionUI = QSpinBox()
        self.suffixUI = QLineEdit()
        self.factorUI = QLineEdit()
        self.separatorUI = QCheckBox()

        self.saveUI = QCheckBox()
        self.acceptUI = QPushButton('OK')
        self.cancelUI = QPushButton('Cancel')


        #Setup widgets
        self.nameUI.setMinimumWidth(300)

        self.functionUI.addItems(['Sum','Mean','Min','Max','Count'])
        self.selectionUI.setChecked(True)


        self.precisionUI.setRange(0,10)
        self.factorUI.setValidator(QDoubleValidator())

        self.saveUI.setChecked(True)
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

        self.layout.addWidget(QLabel('Precision, suffix, factor, separator'),5,0)
        subLayout = QGridLayout()
        subLayout.addWidget(self.precisionUI,0,0)
        subLayout.addWidget(self.suffixUI,0,1)
        subLayout.addWidget(self.factorUI,0,2)
        subLayout.addWidget(self.separatorUI,0,3)
        subLayout.setColumnStretch(0,1)
        subLayout.setColumnStretch(1,1)
        subLayout.setColumnStretch(2,1)
        subLayout.setColumnStretch(3,0)
        self.layout.addLayout(subLayout,5,1,1,2)

        self.layout.addWidget(QLabel('Save with project'),8,0)
        self.layout.addWidget(self.saveUI,8,1,1,2)
        self.layout.addWidget(self.cancelUI,9,0)
        self.layout.addWidget(self.acceptUI,9,1,1,2)


        #Connect signals
        # These are just for autoname
        QObject.connect(self.autoNameUI,SIGNAL("stateChanged(int)"),self.toggleAutoName)
        QObject.connect(self.layerUI,SIGNAL("currentIndexChanged(int)"),self.createName)
        QObject.connect(self.fieldUI,SIGNAL("currentIndexChanged(int)"),self.createName)
        QObject.connect(self.functionUI,SIGNAL("currentIndexChanged(int)"),self.createName)
        QObject.connect(self.selectionUI,SIGNAL("stateChanged(int)"),self.createName)

        # This makes the fields comboBox refresh when the user chooses a different layer
        QObject.connect(self.layerUI,SIGNAL("activated(int)"),self.choosedLayerChanged)

        # Confirm or cancel
        QObject.connect(self.acceptUI,SIGNAL("pressed()"),self.accept)
        QObject.connect(self.cancelUI,SIGNAL("pressed()"),self.reject)

    def show(self, bar):
        self.nameUI.setText( bar.name )
        self.autoNameUI.setCheckState( bar.autoName )
        self.layerUI.rebuild( bar.layer )
        self.fieldUI.rebuild( bar.layer, bar.fieldName )
        self.functionUI.setCurrentIndex( max(0,self.functionUI.findText(bar.functionName)) )
        self.selectionUI.setCheckState( bar.selectedOnly )
        self.precisionUI.setValue( bar.precision )
        self.suffixUI.setText( bar.suffix )
        self.factorUI.setText( bar.factor )
        self.separatorUI.setCheckState( bar.separator )
        self.saveUI.setCheckState( bar.saveWith )

        QDialog.show(self)

    def choosedLayerChanged(self, index):
        self.fieldUI.rebuild( self.layerUI.currentLayer(), None )

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





