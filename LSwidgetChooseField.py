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
from qgis.core import QgsMapLayer


class LSwidgetChooseField(QComboBox):

    def __init__(self, iface):
        QComboBox.__init__(self)
        self.iface = iface

    def rebuild(self, layer, previousFieldName):

        self.blockSignals(True)
        self.clear() 
        self.addItem('$area')
        self.addItem('$length')
        #self.addItem('$perimeter')

        if layer is None:
            layer = self.iface.activeLayer()
            if layer is not None and layer.type() != QgsMapLayer.VectorLayer:
                layer = None                

        if layer is not None:
            fields = layer.fields()
            for field in fields:
                self.addItem(field.name())
        self.blockSignals(False)

        if previousFieldName is not None:
            search = self.findText(previousFieldName)
            self.setCurrentIndex(max(0, search))
