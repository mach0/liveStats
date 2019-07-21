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

from qgis.PyQt.QtWidgets import QComboBox
from qgis.core import QgsProject, QgsMapLayer


class LSwidgetChooseLayer(QComboBox):

    def __init__(self, iface):
        QComboBox.__init__(self)
        self.iface = iface

        self.eligibleLayers = []

    def rebuild(self, previousLayer):

        self.eligibleLayers = []
        layers = [lay for lay in QgsProject.instance().mapLayers().values()]
        for layer in layers:
            if layer.type() == QgsMapLayer.VectorLayer:
                self.eligibleLayers.append(layer)

        previousIndex = 0
        self.blockSignals(True)
        self.clear()   
        self.addItem('[active]')
        i = 1
        for layer in self.eligibleLayers:
            self.addItem(layer.name())
            if layer is previousLayer:
                previousIndex = i
            i += 1
        self.blockSignals(False)

        self.setCurrentIndex(previousIndex)

    def currentLayer(self):
        index = self.currentIndex()
        if index > 0:
            return self.eligibleLayers[index-1]
        else: 
            return None
