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
import locale

from LSeditor import LSeditor
from LScomputers import *



class LSbar(QToolBar):
    count = 0

    def __init__(self, iface, showDialog):
        QToolBar.__init__(self)
        self.iface = iface
        LSbar.count+=1

        # LiveStatBar's properties
        self.name = "LiveStat "+ str(LSbar.count)
        self.autoName = 0
        self.layer = None
        self.fieldName = '$area'
        self.functionName = 'Sum'
        self.selectedOnly = 2
        self.precision = 3
        self.suffix = ''
        self.factor = '1'
        self.separator = 2
        self.saveWith = 2
        #self.position = Qt.BottomToolBarArea

        # LiveStatBar's dialog
        self.dialog = LSeditor(self.iface)
        QObject.connect(self.dialog, SIGNAL('accepted()'), self.dialogAccepted)

        # We connect the bar to some events that may trigger an update
        QObject.connect(self.iface, SIGNAL('currentLayerChanged(QgsMapLayer*)'), self.layerChanged)
        QObject.connect(self.iface.mapCanvas(), SIGNAL('selectionChanged(QgsMapLayer*)'), self.selectionChanged)


        # Setup the bar GUI
        self.setWindowTitle(self.name)

        # Create widgets
        self.nameWidget = QLabel(self.name);
        self.displayWidget = QLabel("Click to edit")

        # Layout widgets
        self.addWidget( self.nameWidget )
        self.addWidget( self.displayWidget )


        self.setMinimumSize( self.sizeHint() )



        # We display the dialog at creatin (if required)
        if showDialog:
            self.dialog.show(self)


    def mousePressEvent(self, event):
        # We want the dialog to display on a simple click
        self.dialog.show(self)
        

    def dialogAccepted(self):
        # When the dialog is accepted, we update the bar's attribute to correspond to the dialog's input
        self.name = self.dialog.nameUI.text()
        self.autoName = self.dialog.autoNameUI.checkState()
        self.layer = self.dialog.layerUI.currentLayer()
        self.fieldName = self.dialog.fieldUI.currentText()
        self.functionName = self.dialog.functionUI.currentText()
        self.selectedOnly = self.dialog.selectionUI.checkState()
        self.precision = self.dialog.precisionUI.value()
        self.suffix = self.dialog.suffixUI.text()
        self.factor = self.dialog.factorUI.text()
        self.separator = self.dialog.separatorUI.checkState()
        self.saveWith = self.dialog.saveUI.checkState()

        self.setObjectName(self.name)
        # And we recompute the bar
        self.compute()


    def layerChanged(self):
        # When the active layer changed, we trigger an update (but only if the bar displays stats of the -CURRENT- layer)
        if self.layer is None:
            self.compute()
    def selectionChanged(self):
        # When the current selection changes, we trigger an update (but only if the bar displays stats of the selection)
        if self.selectedOnly:
            self.compute()

    def compute(self):
        # This recompoutes the bar
        #QgsMessageLog.logMessage('COMPUTE','LiveStats')

        #Set the name
        self.nameWidget.setText( self.name )

        #Get the layer.
        if self.layer is not None:
            layer = self.layer
        else:
            # If the layer is None, it means we display the activeLayer
            activeLayer = self.iface.activeLayer()
            if activeLayer is None or activeLayer.type() != QgsMapLayer.VectorLayer:
                self.setText('NO LAYER')
                return
            layer = activeLayer

       

        #Prepare the computer
        if self.functionName == 'Count':
            computer = LScountComputer()
        elif self.functionName == 'Sum':
            computer = LSsumComputer()
        elif self.functionName == 'Min':
            computer = LSminComputer()
        elif self.functionName == 'Max':
            computer = LSmaxComputer()
        elif self.functionName == 'Mean':
            computer = LSmeanComputer()

        # Do some weird stuff to get the field and the freatures later on
        # This is a bit cryptic (I copied it from statist plugin)
        fieldIndex = layer.fieldNameIndex( self.fieldName )
        layer.select( [ fieldIndex ], QgsRectangle(), True )

        if self.fieldName not in ['$area', '$length'] and fieldIndex == -1:
            self.setText('NO FIELD')
            return

        #Do the actual computation
        if self.selectedOnly:
            # We loop through the selection
            features = layer.selectedFeatures()
            for feature in features:
                computer.addVal(self.valueForFeature(feature, fieldIndex))

        else:
            # We loop through all features
            feature = QgsFeature()
            while layer.nextFeature( feature ):
                computer.addVal(self.valueForFeature(feature, fieldIndex))

        # And we finally display the result in the widget
        result = computer.result()
        result *= float(self.factor)
        result = self.formatNumber(result)
        result = result+self.suffix
        self.displayWidget.setText(result)

        self.setText(result)


    def setText(self, text):
        self.displayWidget.setText(text + ' : ')
        #Resize the widget
        self.setMinimumSize( self.sizeHint() )




    def valueForFeature(self, feature, fieldIndex):
        # This returns the value for a feature and a fieldIndex

        if self.fieldName == '$area':
            return feature.geometry().area()
        elif self.fieldName == '$length':
            return feature.geometry().length ()
        else:
            # This is a bit cryptic (I copied it from statist plugin)
            return float( feature.attributeMap()[ fieldIndex ].toDouble()[ 0 ] )


    def save(self):
        # This returns this bar's attributes as a QString to be stored in the file
        returnStringList = QStringList()

        returnStringList.append( self.name )
        returnStringList.append( str(self.autoName) ) 
        if self.layer is None:
            returnStringList.append( '' )
        else:
            returnStringList.append( self.layer.id() )
        returnStringList.append( self.fieldName )
        returnStringList.append( self.functionName )
        returnStringList.append( str(self.selectedOnly) ) 
        returnStringList.append( str(self.precision) )
        returnStringList.append( self.suffix )
        returnStringList.append( self.factor )
        returnStringList.append( str(self.separator) )
        #returnStringList.append( str(self.position) )

        return returnStringList.join('*|*')

    def load(self, string):
        # This sets this bar's attributes from a QString to be loaded
        loadStringList = string.split('*|*')

        self.name = loadStringList[0]
        self.autoName = int(loadStringList[1])
        self.layer = None
        for l in self.iface.legendInterface().layers():
            if l.id() == loadStringList[2]:
                self.layer = l
        self.fieldName = loadStringList[3]
        self.functionName = loadStringList[4]
        self.selectedOnly = int(loadStringList[5])
        self.precision = int(loadStringList[6])
        self.suffix = loadStringList[7]
        self.factor = loadStringList[8]
        self.separator = int(loadStringList[9])
        self.saveWith = 2
        #self.position = int(loadStringList[11])

        self.compute()

    def formatNumber(self, number):
        if self.precision == 0:
            result = locale.format('%d', number, self.separator)
        else:
            result = locale.format('%.'+str(self.precision)+'f', number, self.separator)
        return result



