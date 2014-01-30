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

from LSeditWidget import LSeditWidget
from LSbarWidget import LSbarWidget


class LSstat(QObject):

    settingsChanged = pyqtSignal()
    resultChanged = pyqtSignal()


    def setName(self, value):
        self.name = value
        self.settingsChanged.emit()
    def setLayer(self, value):
        self.layer = value
        self.settingsChanged.emit()
    def setExpression(self, value):
        self.expression = value
        self.settingsChanged.emit()
    def setLimittoselection(self, value):
        self.limittoselection = value
        self.settingsChanged.emit()
    def setAutoupdate(self, value):
        self.autoupdate = value
        self.settingsChanged.emit()

    @property
    def usedLayer(self):
        return self.layer if self.layer is not None else self.iface.activeLayer()


    i = 0
    def __init__(self, iface, name=None, layer=None, expression="", limittoselection=True, autoupdate=True):
        QWidget.__init__(self)

        # Save reference to the QGIS interface
        self.iface = iface

        LSstat.i += 1

        # Properties
        self.name = name if name is not None else "LiveStats #"+str(LSstat.i)
        self.layer = layer
        self.expression = expression
        self.limittoselection = limittoselection
        self.autoupdate = autoupdate

        self.settingsChanged.emit()

        self.result = 0
        self.count = 0
        self.errors = 0

        # Widgets
        self.editWidget = LSeditWidget(self.iface, self)
        self.barWidget = LSbarWidget(self.iface, self)

        # Internal signals
        self.settingsChanged.connect(self.recompute)

        # External signals
        self.iface.mapCanvas().selectionChanged.connect(self.recompute)
        self.iface.currentLayerChanged.connect(self.layerChanged)

        self.settingsChanged.emit()
        self.resultChanged.emit()

    def layerChanged(self):
        if self.layer is None:
            self.recompute()

    def showEditWidget(self):
        self.editWidget.show()

    def recompute(self):
        layer = self.usedLayer

        if layer is None:
            self.result = "No layer selected"
        elif layer.type() != QgsMapLayer.VectorLayer:
            self.result = "Not a vector layer : "+str(layer.id())
        elif layer.geometryType() != QGis.Polygon:
            self.result = "Not a polygon layer : "+str(layer.id())
        else:
            # Loop through the features
            expression = QgsExpression( self.expression )

            features = layer.selectedFeatures()
            self.result = None
            self.count = 0
            self.errors = 0
            for feature in features:
                if self.result is None:
                    self.result = expression.evaluate( feature )
                else:
                    self.result += expression.evaluate( feature )
                self.count += 1
                if expression.hasEvalError():
                    self.errors += 1

        self.resultChanged.emit()
        







