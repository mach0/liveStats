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


class LSwidgetChooseLayer(QComboBox):

    def __init__(self, iface):
        QComboBox.__init__(self)
        self.iface = iface

        self.eligibleLayers = []

    def rebuild(self):
        self.eligibleLayers = []
        for layer in self.iface.legendInterface().layers():
            if layer.type() == QgsMapLayer.VectorLayer:
                self.eligibleLayers.append(layer)

        # Rebuild layer menu
        previousChoosenLayer = self.currentText()

        self.blockSignals(True)
        self.clear()   
        self.addItem('ACTIVE LAYER')
        for layer in self.eligibleLayers:
            self.addItem(layer.name())
        self.blockSignals(False)

        search = self.findText(previousChoosenLayer)
        self.setCurrentIndex( max(0,search) )

    def currentLayer(self):
        index = self.currentIndex()
        if index > 0:
            return self.eligibleLayers[index-1]
        else:
            if self.iface.activeLayer() is not None and self.iface.activeLayer().type() == QgsMapLayer.VectorLayer: 
                return self.iface.activeLayer()
            else:
                return None