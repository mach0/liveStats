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


class QgsLayerComboBox(QComboBox):

    currentLayerChanged = pyqtSignal(QgsMapLayer)

    def __init__(self, iface):
        QComboBox.__init__(self)
        self.iface = iface

        self.eligibleLayers = []
        self._rebuild()
        
        self.iface.mapCanvas().layersChanged.connect(self._rebuild)
        self.currentIndexChanged.connect(self._changed)


    def setCurrentLayer(self, layer):
        try:
            i = self.eligibleLayers.index(layer)
        except ValueError:
            i = -1
        i+=1 #since we added - Current -
        self.setCurrentIndex(i)

    def currentLayer(self):
        i = self.currentIndex()
        if i<=0: #since we added - Current - at index 0
            return None
        else:
            i-=1 #since we added - Current - at index 0
            return self.eligibleLayers[i]

    def _changed(self):
        layer = self.currentLayer()
        self.currentLayerChanged.emit(layer)

    def _rebuild(self):

        QgsMessageLog.logMessage("comboBoxStart","LiveStats")

        self.blockSignals(True)

        prevLayer = self.currentLayer()
        QgsMessageLog.logMessage("set "+str(prevLayer),"LiveStats")

        self.eligibleLayers = []
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                self.eligibleLayers.append(layer)

        self.clear()
        self.addItem('- Current -')
        for layer in self.eligibleLayers:
            self.addItem(layer.name())

        QgsMessageLog.logMessage("restore "+str(prevLayer),"LiveStats")
        self.setCurrentLayer(prevLayer)

        self.blockSignals(False)