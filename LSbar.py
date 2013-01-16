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
    count = 0

    def __init__(self, iface, mainClass, showDialog):
        QToolBar.__init__(self)
        self.iface = iface
        self.mainClass = mainClass
        LSbar.count+=1


        # LiveStatBar's properties
        self.name = "LiveStat "+ str(LSbar.count)
        self.autoName = 0
        self.layer = None
        self.fieldName = '$area'
        self.filter = ''
        self.functionName = 'Sum'
        self.selectedOnly = 2
        self.precision = 3
        self.suffix = ''
        self.factor = '1'
        self.separator = 2
        self.saveWith = 2

        self.position = {}
        self.position['floating'] = 0
        self.position['x'] = 0
        self.position['y'] = 0

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

        # If the clone box is checked, we create a new bar and apply the settings on the new bar
        makeClone = self.dialog.cloneUI.checkState()
        if makeClone:
            newStatsBar = LSbar(self.iface, self.mainClass, False)
            self.mainClass.addBar(newStatsBar)
            bar = newStatsBar
        else:
            bar = self

        # When the dialog is accepted, we update the bar's attribute to correspond to the dialog's input
        bar.name = self.dialog.nameUI.text()
        bar.autoName = self.dialog.autoNameUI.checkState()
        bar.layer = self.dialog.layerUI.currentLayer()
        bar.fieldName = self.dialog.fieldUI.currentText()
        bar.filter = self.dialog.filterUI.text()
        bar.functionName = self.dialog.functionUI.currentText()
        bar.selectedOnly = self.dialog.selectionUI.checkState()
        bar.precision = self.dialog.precisionUI.value()
        bar.suffix = self.dialog.suffixUI.text()
        bar.factor = self.dialog.factorUI.text()
        bar.separator = self.dialog.separatorUI.checkState()
        bar.saveWith = self.dialog.saveUI.checkState()

        bar.setObjectName(self.name)

        # And we recompute the bar
        self.compute()
        if makeClone:
            # If it's a clone, we update it 
            bar.compute()
        


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

        try:
            #Get the layer.
            if self.layer is not None:
                layer = self.layer
            else:
                # If the layer is None, it means we display the activeLayer
                activeLayer = self.iface.activeLayer()
                if activeLayer is None or activeLayer.type() != QgsMapLayer.VectorLayer:
                    raise NoLayerError()
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
            else:
                raise NoComputerError()

            #Get the field index for the field that is being comuputed
            computeFieldIndex = layer.fieldNameIndex( self.fieldName )

            #Not really clear what this does...
            layer.select( layer.pendingAllAttributesList() )


            if self.filter != '':
                expression = QgsExpression(self.filter)
                expression.prepare(layer.pendingFields())
                if expression.hasParserError():
                    raise ParserError(expression.parserErrorString())
            else:
                expression = None

            if self.fieldName not in ['$area', '$length'] and computeFieldIndex == -1:
                raise NoFieldError()

            def getFeatures():
                if self.selectedOnly:
                    return layer.selectedFeatures()
                else:
                    # The layer is an iterator that returns a QgsFeature on next(), so just return the layer
                    return layer

            # Loop the features.
            for feature in getFeatures():

                if expression is not None:
                    result = expression.evaluate(feature, layer.pendingFields())
                    if expression.hasEvalError():
                          raise EvalError(expression.evalErrorString())
                          continue
                    if not result.toBool():
                        continue
                self.valueForFeature(feature, computer, computeFieldIndex)


            result = computer.result()            

            # And we finally display the result in the widget
            self.locale = QLocale()
            if not self.separator:
                self.locale.setNumberOptions(QLocale.OmitGroupSeparator)
            result *= float(self.factor)
            result = self.locale.toString(result, 'f', self.precision)
            result = result+self.suffix
            self.displayWidget.setText(result)

            self.setText(result)

        except NoLayerError as e:
            self.setText('NO LAYER !')
            return
        except ParserError as e:
            self.setText('PARSER ERROR : '+str(e))
            return
        except NoComputerError as e:
            self.setText('NO COMPUTER !')
            return
        except NoFieldError as e:
            self.setText('NO FIELD !')
            return
        except NoGeometryError as e:
            self.setText('NO GEOMETRY !')
            return
        except EvalError as e:
            self.setText('EVAL ERROR : '+str(e))
            return



    def setText(self, text):
        self.nameWidget.setText( self.name )
        self.displayWidget.setText(text)

        #Resize the widget
        self.setMinimumSize( self.sizeHint() )
        
        #TODO : there are some glitches when text length increases and the toolbar is docked on a side
        #but none of this works :/
        #self.updateGeometry()
        #self.update()
        #self.repaint()
        #self.iface.mainWindow().updateGeometry()
        #self.iface.mainWindow().update()
        #self.iface.mainWindow().repaint()


    def valueForFeature(self, feature, computer, computeFieldIndex):
        # This returns the value for a feature and a computeFieldIndex
        if self.fieldName == '$area':
            if feature.geometry() is None:
                # This happens for instance when a CSV layer is selected.
                # They are considered as vector layer (!!) but their features have no geometry
                raise NoGeometryError()
            val = feature.geometry().area()

        elif self.fieldName == '$length':
            if feature.geometry() is None:
                # This happens for instance when a CSV layer is selected.
                # They are considered as vector layer (!!) but their features have no geometry
                raise NoGeometryError()
            val = feature.geometry().length()  
        else:
            # This is a bit cryptic (I copied it from statist plugin)
            val = float( feature.attributeMap()[ computeFieldIndex ].toDouble()[ 0 ] )

        computer.addVal(  val  )

    def save(self):
        # This returns this bar's attributes as a QString to be stored in the file
        returnStringList = QStringList()

        # Statistics attributes
        returnStringList.append( self.name ) #0
        returnStringList.append( str(self.autoName) )  #1
        if self.layer is None:
            returnStringList.append( '' ) #2
        else:
            returnStringList.append( self.layer.id() ) #2
        returnStringList.append( self.fieldName ) #3
        returnStringList.append( self.filter ) #4
        returnStringList.append( self.functionName ) #5
        returnStringList.append( str(self.selectedOnly) ) #6
        returnStringList.append( str(self.precision) ) #7
        returnStringList.append( self.suffix ) #8
        returnStringList.append( self.factor ) #9
        returnStringList.append( str(self.separator) ) #10

        # Position attributes
        #returnStringList.append( str(self.saveGeometry()) ) #11
        returnStringList.append( str(int(self.isFloating())) ) #11
        returnStringList.append( str(self.pos().x()) ) #12
        returnStringList.append( str(self.pos().y()) ) #13

        return returnStringList.join('*|*')

    def load(self, string):
        # This sets this bar's attributes from a QString to be loaded
        loadStringList = string.split('*|*')

        # Statistics attributes
        self.name = loadStringList[0] #0
        self.autoName = int(loadStringList[1]) #1
        self.layer = None #2
        for l in self.iface.legendInterface().layers():
            if l.id() == loadStringList[2]:
                self.layer = l #2
        self.fieldName = loadStringList[3] #3
        self.filter = loadStringList[4] #4
        self.functionName = loadStringList[5] #5
        self.selectedOnly = int(loadStringList[6]) #6
        self.precision = int(loadStringList[7]) #7
        self.suffix = loadStringList[8] #8
        self.factor = loadStringList[9] #9
        self.separator = int(loadStringList[10]) #10

        # Position attributes
        #self.storedGeometry = loadStringList[11].toAscii() #11
        self.position['floating'] = bool(int(loadStringList[11]))
        self.position['x'] = int(loadStringList[12])
        self.position['y'] = int(loadStringList[13])

        self.saveWith = 2

        self.compute()

class NoLayerError(Exception):
    pass
class ParserError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)
class NoComputerError(Exception):
    pass
class NoGeometryError(Exception):
    pass
class NoFieldError(Exception):
    pass
class EvalError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return str(self.msg)





