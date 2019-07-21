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

from qgis.PyQt.QtCore import QLocale
from qgis.PyQt.QtWidgets import QToolBar, QLabel
from qgis.core import QgsMapLayer, QgsProject, QgsExpression

from .LSeditor import LSeditor
from .LScomputers import LScomputerConcat, LScomputerCount, LScomputerMax, LScomputerMean, \
    LScomputerMin, LScomputerSum, LScomputerUniqueConcat, LScomputerNonNull


class LSbar(QToolBar):
    count = 0

    def __init__(self, iface, mainClass, showDialog):
        QToolBar.__init__(self)
        self.iface = iface
        self.mainClass = mainClass
        LSbar.count += 1
        # LiveStatBar's properties
        self.name = "LiveStat %i" % LSbar.count
        self.autoName = 2
        self.layer = None
        self.fieldName = '$area'
        self.filter = ''
        self.functionName = 'Sum'
        self.selectedOnly = 2
        self.precision = 2
        self.suffix = '   '
        self.factor = '1'
        self.separator = 2
        self.position = {}
        self.position['floating'] = 0
        self.position['x'] = 0
        self.position['y'] = 0
        # LiveStatBar's dialog
        self.dialog = LSeditor(self.iface, self)
        self.dialog.accepted.connect(self.dialogAccepted)
        # We connect the bar to some events that may trigger an update
        self.iface.currentLayerChanged.connect(self.layerChanged)
        self.iface.mapCanvas().selectionChanged.connect(self.selectionChanged)
        # Setup the bar GUI
        self.setWindowTitle(self.name)
        # Create widgets
        self.nameWidget = QLabel(self.name)
        self.displayWidget = QLabel("Click to edit")
        # Layout widgets
        self.addWidget(self.nameWidget)
        self.addWidget(self.displayWidget)
        self.setMinimumSize(self.sizeHint())
        # We display the dialog at creation (if required)
        if showDialog:
            self.dialog.show(self)

    def showEvent(self, QShowEvent):
        QToolBar.showEvent(self, QShowEvent)
        self.compute()

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
        bar.setWindowTitle('LiveStat "'+bar.name+'"')

        # And we recompute the bar
        self.compute()
        if makeClone:
            # If it's a clone, we update it 
            bar.compute()

    def dialogDelete(self):
        self.mainClass.removeBar(self)        

    def layerChanged(self):
        # When the active layer changed, trigger an update (but only if the bar displays stats of the -CURRENT- layer)
        if self.isVisible() and self.layer is None:
            self.compute()
    
    def selectionChanged(self):
        # When the current selection changes, we trigger an update (but only if the bar displays stats of the selection)
        if self.isVisible() and self.selectedOnly:
            self.compute()

    def compute(self):
        # This recomputes the bar
        # QgsMessageLog.logMessage('COMPUTE','LiveStats')

        try:
            # Get the layer.
            if self.layer is not None:
                layer = self.layer
            else:
                # If the layer is None, it means we display the activeLayer
                activeLayer = self.iface.activeLayer()
                if activeLayer is None or activeLayer.type() != QgsMapLayer.VectorLayer:
                    raise NoLayerError()
                layer = activeLayer

            # Prepare the computer
            if self.functionName == 'Count':
                computer = LScomputerCount()
            elif self.functionName == 'NonNull':
                computer = LScomputerNonNull()
            elif self.functionName == 'Sum':
                computer = LScomputerSum()
            elif self.functionName == 'Min':
                computer = LScomputerMin()
            elif self.functionName == 'Max':
                computer = LScomputerMax()
            elif self.functionName == 'Mean':
                computer = LScomputerMean()
            elif self.functionName == 'Concat':
                computer = LScomputerConcat()
            elif self.functionName == 'UniqueConcat':
                computer = LScomputerUniqueConcat()
            else:
                raise NoComputerError()

            def formatter(result):
                # And we finally display the result in the widget
                self.locale = QLocale()
                if not self.separator:
                    self.locale.setNumberOptions(QLocale.OmitGroupSeparator)
                result *= float(self.factor)
                if self.precision < 0:
                    pow10 = 10**(-self.precision)
                    result = self.locale.toString(float(pow10*round(result/pow10)), 'f', 0)
                else:
                    result = self.locale.toString(result, 'f', self.precision)
                result = result+self.suffix
                return result
            computer.formatter = formatter

            # Get the field index for the field that is being comuputed
            computeFieldName = self.fieldName

            # Not really clear what this does...
            # layer.select( layer.pendingAllAttributesList() )

            if self.filter != '':
                expression = QgsExpression(self.filter)
                expression.prepare(layer.fields())
                if expression.hasParserError():
                    raise ParserError(expression.parserErrorString())
            else:
                expression = None

            if self.fieldName not in ['$area', '$length'] and layer.fieldNameIndex(computeFieldName) == -1:
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
                    result = expression.evaluate(feature, layer.fields())
                    if expression.hasEvalError():
                        raise EvalError(expression.evalErrorString())
                        continue
                    if not result.toBool():
                        continue
                self.valueForFeature(feature, computer, computeFieldName)

            result = computer.result()

            # self.displayWidget.setText(result)

            self.setText(result)

        except NoLayerError as e:
            self.setText('---')
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
        self.nameWidget.setText(self.name + ' : ')
        self.displayWidget.setText(text)

        # Resize the widget
        self.setMinimumSize(self.sizeHint())
        
        # TODO : there are some glitches when text length increases and the toolbar is docked on a side
        # but none of this works :/
        # self.updateGeometry()
        # self.update()
        # self.repaint()
        # self.iface.mainWindow().updateGeometry()
        # self.iface.mainWindow().update()
        # self.iface.mainWindow().repaint()

    def valueForFeature(self, feature, computer, computeFieldName):
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
            val = feature.attribute(computeFieldName)

        computer.addVal(val)

    def save(self):
        # This returns this bar's attributes as a QString to be stored in the file
        returnStringList = []

        # Statistics attributes
        returnStringList.append(self.name)  # 0
        returnStringList.append(str(self.autoName))  # 1
        if self.layer is None:
            returnStringList.append('')  # 2
        else:
            returnStringList.append(self.layer.id())  # 2
        returnStringList.append(self.fieldName)  # 3
        returnStringList.append(self.filter)  # 4
        returnStringList.append(self.functionName)  # 5
        returnStringList.append(str(self.selectedOnly))  # 6
        returnStringList.append(str(self.precision))  # 7
        returnStringList.append(self.suffix)  # 8
        returnStringList.append(self.factor)  # 9
        returnStringList.append(str(self.separator))  # 10

        # Position attributes
        returnStringList.append(str(int(self.isFloating())))  # 11
        returnStringList.append(str(self.pos().x()))  # 12
        returnStringList.append(str(self.pos().y()))  # 13

        return '*|*'.join(returnStringList)

    def load(self, string):
        # This sets this bar's attributes from a QString to be loaded
        loadStringList = string.split('*|*')

        try:
            # Statistics attributes
            self.name = loadStringList[0]  # 0
            self.autoName = int(loadStringList[1])  # 1
            self.layer = None  # 2
            layers = [lay for lay in QgsProject.instance().mapLayers().values()]
            for l in layers:
                if l.id() == loadStringList[2]:
                    self.layer = l  # 2
            self.fieldName = loadStringList[3]  # 3
            self.filter = loadStringList[4]  # 4
            self.functionName = loadStringList[5]  # 5
            self.selectedOnly = int(loadStringList[6])  # 6
            self.precision = int(loadStringList[7])  # 7
            self.suffix = loadStringList[8]  # 8
            self.factor = loadStringList[9]  # 9
            self.separator = int(loadStringList[10])  # 10

            # Position attributes
            # self.storedGeometry = loadStringList[11].toAscii() #11
            self.position['floating'] = bool(int(loadStringList[11]))
            self.position['x'] = int(loadStringList[12])
            self.position['y'] = int(loadStringList[13])
        except IndexError as e:
            # On plugin update, if attributes are added, this allows to load as much as possible...
            # Remaining attributes will be defaults
            pass

        self.setWindowTitle('LiveStat "'+self.name+'"')

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
