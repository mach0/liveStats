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

from qgis.PyQt.QtWidgets import QDialog, QGridLayout, QLineEdit, QCheckBox, \
    QComboBox, QPushButton, QSpinBox, QLabel, QMessageBox
from qgis.PyQt.QtGui import QDoubleValidator
from qgis.gui import QgsSearchQueryBuilder

from .LSwidgetChooseField import LSwidgetChooseField
from .LSwidgetChooseLayer import LSwidgetChooseLayer


class LSeditor(QDialog):
    def __init__(self, iface, bar):
        QDialog.__init__(self)
        self.iface = iface
        self.bar = bar
        self.setModal(True)

        # Set layout
        self.layout = QGridLayout()
        self.setLayout(self.layout)

        # Create widgets
        self.nameUI = QLineEdit()
        self.autoNameUI = QCheckBox('Auto')
        self.layerUI = LSwidgetChooseLayer(self.iface)
        self.fieldUI = LSwidgetChooseField(self.iface)
        self.functionUI = QComboBox()
        self.filterUI = QLineEdit()
        self.filterDialogUI = QPushButton('editor')
        self.selectionUI = QCheckBox()
        self.precisionUI = QSpinBox()
        self.suffixUI = QLineEdit()
        self.factorUI = QLineEdit()
        self.separatorUI = QCheckBox()
        self.acceptUI = QPushButton('OK')
        self.deleteUI = QPushButton('Delete')
        self.cloneUI = QCheckBox('Copy')

        # Setup widgets
        self.nameUI.setMinimumWidth(300)
        self.autoNameUI.setChecked(True)
        self.functionUI.addItems(['Sum', 'Mean', 'Min', 'Max', 'NonNull', 'Count', 'Concat', 'UniqueConcat'])
        self.selectionUI.setChecked(True)
        self.precisionUI.setRange(-10, 10)
        self.factorUI.setValidator(QDoubleValidator())
        self.acceptUI.setDefault(True)

        # Layout widgets
        self.layout.addWidget(QLabel('Name'), 0, 0)
        self.layout.addWidget(self.nameUI, 0, 1)
        self.layout.addWidget(self.autoNameUI, 0, 2)
        self.layout.addWidget(QLabel('Layer'), 1, 0)
        self.layout.addWidget(self.layerUI, 1, 1, 1, 2)
        self.layout.addWidget(QLabel('Function'), 2, 0)
        self.layout.addWidget(self.functionUI, 2, 1, 1, 2)
        self.layout.addWidget(QLabel('Field'), 3, 0)
        self.layout.addWidget(self.fieldUI, 3, 1, 1, 2)
        self.layout.addWidget(QLabel('Filter (where)'), 4, 0)
        self.layout.addWidget(self.filterUI, 4, 1)
        self.layout.addWidget(self.filterDialogUI, 4, 2)
        self.layout.addWidget(QLabel('Selection only'), 5, 0)
        self.layout.addWidget(self.selectionUI, 5, 1, 1, 2)
        self.layout.addWidget(QLabel('Precision, suffix, factor, separator'), 6, 0)
        subLayout = QGridLayout()
        subLayout.addWidget(self.precisionUI, 0, 0)
        subLayout.addWidget(self.suffixUI, 0, 1)
        subLayout.addWidget(self.factorUI, 0, 2)
        subLayout.addWidget(self.separatorUI, 0, 3)
        subLayout.setColumnStretch(0, 1)
        subLayout.setColumnStretch(1, 1)
        subLayout.setColumnStretch(2, 1)
        subLayout.setColumnStretch(3, 0)
        self.layout.addLayout(subLayout, 6, 1, 1, 2)
        self.layout.addWidget(self.deleteUI, 9, 0)
        self.layout.addWidget(self.acceptUI, 9, 1)
        self.layout.addWidget(self.cloneUI, 9, 2)

        # Connect signals
        # These are just for autoname
        self.autoNameUI.stateChanged.connect(self.toggleAutoName)
        self.layerUI.currentIndexChanged.connect(self.createName)
        self.fieldUI.currentIndexChanged.connect(self.createName)
        self.filterUI.textChanged.connect(self.createName)
        self.filterUI.textChanged.connect(self.createName)
        self.selectionUI.stateChanged.connect(self.createName)
        # This makes the fields comboBox refresh when the user chooses a different layer
        self.layerUI.activated.connect(self.choosedLayerChanged)
        # This opens the filter builder
        self.filterDialogUI.pressed.connect(self.displayFilterBuilder)
        # Confirm or delete
        self.acceptUI.pressed.connect(self.accept)
        self.deleteUI.pressed.connect(self.delete)

    def show(self, bar):
        self.setWindowTitle(bar.name)
        self.nameUI.setText(bar.name)
        self.autoNameUI.setCheckState(bar.autoName)
        self.layerUI.rebuild(bar.layer)
        self.fieldUI.rebuild(bar.layer, bar.fieldName)
        self.filterUI.setText(bar.filter)
        self.functionUI.setCurrentIndex(max(0, self.functionUI.findText(bar.functionName)))
        self.selectionUI.setCheckState(bar.selectedOnly)
        self.precisionUI.setValue(bar.precision)
        self.suffixUI.setText(bar.suffix)
        self.factorUI.setText(bar.factor)
        self.separatorUI.setCheckState(bar.separator)
        self.cloneUI.setCheckState(False)
        self.createName(0)

        QDialog.show(self)
        self.nameUI.setFocus()
        self.nameUI.selectAll()

    def choosedLayerChanged(self, index):
        currentLayer = self.layerUI.currentLayer()
        if currentLayer is None:
            currentLayer = self.iface.activeLayer()
        self.fieldUI.rebuild(currentLayer, None)

    def toggleAutoName(self, index):
        if not self.autoNameUI.checkState():
            self.nameUI.setEnabled(True)
        else:
            self.nameUI.setEnabled(False)
            self.createName(0)

    def displayFilterBuilder(self):
        expDlg = QgsSearchQueryBuilder(self.layerUI.currentLayer())
        expDlg.setSearchString(self.filterUI.text())
        if expDlg.exec_():
            self.filterUI.setText(expDlg.searchString())

    def createName(self, index):
        if self.autoNameUI.checkState():
            func = self.functionUI.currentText()
            field = self.fieldUI.currentText()
            layer = self.layerUI.currentText()
            filt = self.filterUI.text()

            if self.selectionUI.checkState():
                sel = "'s selection"
            else:
                sel = ''
            if filt != '':
                filt = ' ('+filt+')'

            name = func + ' of ' + field + ' in ' + layer + sel + filt

            self.nameUI.setText(name)

    def delete(self):
        deleteDialog = QMessageBox()
        deleteDialog.setText('Are you sure you want to delete this LiveStat ?')
        deleteDialog.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        deleteDialog.setModal(True)
        
        if deleteDialog.exec_() == QMessageBox.Ok:
            self.reject()
            self.bar.dialogDelete()
