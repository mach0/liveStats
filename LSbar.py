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

from LSeditor import LSeditor
from LScomputers import *



class LSbar(QToolBar):
    count = 1

    def __init__(self, iface):
        name = "LiveView "+ str(LSbar.count)
        QToolBar.__init__(self, name)
        self.iface = iface


        self.dialog = LSeditor(self.iface, name)
        QObject.connect(self.dialog, SIGNAL('accepted()'), self.dialogAccepted)

        #initWidget
        self.nameWidget = QLabel(name)
        self.addWidget( self.nameWidget )
        self.separatorWidget = QLabel(' : ')
        self.addWidget( self.separatorWidget )
        self.displayWidget = QLabel("Click to edit")
        self.addWidget( self.displayWidget )

        LSbar.count+=1

        QObject.connect(self.iface, SIGNAL('currentLayerChanged(QgsMapLayer*)'), self.layerChanged)
        QObject.connect(self.iface.mapCanvas(), SIGNAL('selectionChanged(QgsMapLayer*)'), self.selectionChanged)

        self.dialog.show()


    def mousePressEvent(self, event):
        self.dialog.show()

    def dialogAccepted(self):
        self.nameWidget.setText( self.dialog.nameUI.text() )
        self.compute()


    def layerChanged(self):
        if self.dialog.layerUI.currentIndex() == 0:
            self.compute()
    def selectionChanged(self):
        if self.dialog.selectionUI.checkState():
            self.compute()



    def compute(self):
        #update display values


        layer = self.dialog.layerUI.currentLayer()
        if layer is None:
            self.displayWidget.setText('ERROR : no layer...')
            return

        computation = self.dialog.functionUI.currentText()
        if computation == 'Count':
            computer = LScountComputer()
        elif computation == 'Sum':
            computer = LSsumComputer()
        elif computation == 'Min':
            computer = LSminComputer()
        elif computation == 'Max':
            computer = LSmaxComputer()
        elif computation == 'Mean':
            computer = LSmeanComputer()

        fieldIndex = layer.fieldNameIndex( self.dialog.fieldUI.currentText() )
        layer.select( [ fieldIndex ], QgsRectangle(), True )

        result = 0
        if self.dialog.selectionUI.checkState():
            #Use selection
            features = layer.selectedFeatures()
            for feature in features:
                computer.addVal(self.valueForFeature(feature, fieldIndex))

        else:
            #Use all features
            feature = QgsFeature()
            while layer.nextFeature( feature ):
                computer.addVal(self.valueForFeature(feature, fieldIndex))

        self.displayWidget.setText(str(computer.result()))


    def valueForFeature(self, feature, fieldIndex):

        if self.dialog.fieldUI.currentText() == '$area':
            return feature.geometry().area()
        elif self.dialog.fieldUI.currentText() == '$length':
            return feature.geometry().length ()
        #elif self.dialog.fieldUI.currentText() == '$perimeter':
        #    return feature.geometry().length ()
        else:
            return float( feature.attributeMap()[ fieldIndex ].toDouble()[ 0 ] )#I dont understand this line (copied from statist plugin)



