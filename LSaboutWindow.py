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

from qgis.PyQt.QtCore import QFileInfo
from qgis.PyQt.QtWidgets import QDialog, QTextBrowser, QPushButton, QVBoxLayout
from qgis.core import QgsApplication


class LSaboutWindow(QDialog):

    def __init__(self):
        QDialog.__init__(self)

        self.setMinimumWidth(600)
        self.setMinimumHeight(450)

        self.helpFile = QFileInfo(QgsApplication.qgisUserDbFilePath()).path() + "python/plugins/LiveStats/README.html"
        
        self.setWindowTitle('LiveStats')

        txt = QTextBrowser()
        txt.setReadOnly(True)
        txt.setText(open(self.helpFile, 'r').read())

        cls = QPushButton('Close')
        cls.pressed.connect(self.accept)

        lay = QVBoxLayout()
        lay.addWidget(txt)
        lay.addWidget(cls)

        self.setLayout(lay)

        self.show()
