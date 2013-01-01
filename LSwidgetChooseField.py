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


class LSwidgetChooseField(QComboBox):

    def __init__(self, iface):
        QComboBox.__init__(self)
        self.iface = iface



    def rebuild(self, layer):

        # Rebuild fields menu
        previousChoosenField = self.currentText()


        self.blockSignals(True)
        self.clear() 
        if layer is not None:
            fields = layer.pendingFields()
            for key in fields:
                self.addItem(fields[key].name())
        self.addItem('$area')
        self.addItem('$length')
        self.addItem('$perimeter')
        self.blockSignals(False)

        search = self.findText(previousChoosenField)
        self.setCurrentIndex( max(0,search) )
