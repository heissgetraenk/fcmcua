from PySide2 import QtCore, QtWidgets

__pos_max__ = 10000
__pos_min__ = -10000
__pos_unit__ = ' mm'

__time_max__ = 100000
__time_min__ = 0
__time_unit__ = ' ms'

class ActuatorWidgets(QtWidgets.QWidget):

    def __init__(self, hidden=False):
        self.widgets = []

        #widget mode
        self.hidden = hidden

        # type
        self.typeLabel = QtWidgets.QLabel('Type')
        self.widgets.append(self.typeLabel)
        self.typeCombo = QtWidgets.QComboBox()
        self.typeCombo.addItems(['1 bidirectional (open and close)',
                                '2 unidirectional (open, return-spring on close)', 
                                '3 unidirectional (close, return-spring on open)'])
        self.widgets.append(self.typeCombo)
        self.typeCombo.currentIndexChanged.connect(self._onTypeChanged)
        # non-linear blockage
        self.blockCheck = QtWidgets.QCheckBox('Option: conditional block')
        self.blockCheck.stateChanged.connect(self._onBlockChecked)
        self.widgets.append(self.blockCheck)
        # nodeIDs (open & close)
        self.openLabel = QtWidgets.QLabel('Open NodeID')
        self.widgets.append(self.openLabel)

        self.openLEdit = QtWidgets.QLineEdit("ns=2;i=2")
        self.widgets.append(self.openLEdit)

        self.blockLabel = QtWidgets.QLabel('Block Condition NodeID')
        self.widgets.append(self.blockLabel)

        self.blockLEdit = QtWidgets.QLineEdit("ns=2;i=2")
        self.widgets.append(self.blockLEdit)

        self.closeLabel = QtWidgets.QLabel('Close NodeID')
        self.widgets.append(self.closeLabel)

        self.closeLEdit = QtWidgets.QLineEdit("ns=2;i=2")
        self.widgets.append(self.closeLEdit)

        # FreeCad object info
        self.fcLabel = QtWidgets.QLabel('FreeCAD object')
        self.widgets.append(self.fcLabel)

        self.docLEdit = QtWidgets.QLineEdit('Document')
        self.widgets.append(self.docLEdit)

        self.objLEdit = QtWidgets.QLineEdit('Object label')
        self.widgets.append(self.objLEdit)

        self.vectorCombo = QtWidgets.QComboBox()
        self.vectorCombo.addItems(['x', 'y', 'z'])
        self.widgets.append(self.vectorCombo)

        # postion spin boxes (open & close)
        self.openSLabel = QtWidgets.QLabel('Open postion')
        self.widgets.append(self.openSLabel)

        self.openSpin = QtWidgets.QDoubleSpinBox()
        self.openSpin.setRange(__pos_min__, __pos_max__)
        self.openSpin.setValue(100)
        self.openSpin.setSuffix(__pos_unit__)
        self.widgets.append(self.openSpin)
        self.openSpin.textChanged[str].connect(self._onOpenPosChanged)

        self.blockSLabel = QtWidgets.QLabel('Block postion')
        self.widgets.append(self.blockSLabel)

        self.blockSpin = QtWidgets.QDoubleSpinBox()
        self.blockSpin.setRange(__pos_min__, __pos_max__)
        self.blockSpin.setValue(50)
        self.blockSpin.setSuffix(__pos_unit__)
        self.widgets.append(self.blockSpin)
        self.blockSpin.textChanged[str].connect(self._onBlockPosChanged)

        self.closeSLabel = QtWidgets.QLabel('Close postion')
        self.widgets.append(self.closeSLabel)

        self.closeSpin = QtWidgets.QDoubleSpinBox()
        self.closeSpin.setRange(__pos_min__, __pos_max__)
        self.closeSpin.setValue(0)
        self.closeSpin.setSuffix(__pos_unit__)
        self.widgets.append(self.closeSpin)
        self.closeSpin.textChanged[str].connect(self._onClosePosChanged)

        # duration spin boxes (open & close)
        self.openTLabel = QtWidgets.QLabel('Opening duration')
        self.widgets.append(self.openTLabel)
        
        self.openTSpin = QtWidgets.QDoubleSpinBox()
        self.openTSpin.setRange(__time_min__, __time_max__)
        self.openTSpin.setValue(1000)
        self.openTSpin.setSuffix(__time_unit__)
        self.widgets.append(self.openTSpin)

        self.closeTLabel = QtWidgets.QLabel('Closing duration')
        self.widgets.append(self.closeTLabel)

        self.closeTSpin = QtWidgets.QDoubleSpinBox()
        self.closeTSpin.setRange(__time_min__, __time_max__)
        self.closeTSpin.setValue(1000)
        self.closeTSpin.setSuffix(__time_unit__)
        self.widgets.append(self.closeTSpin)

        # call _onBlockChecked once
        self._onBlockChecked()

    def _onClosePosChanged(self, value):
        '''
        closing position must be < opening position
        '''
        self.openSpin.setMinimum(float(value[:-3].replace(',', '.' )))
        self.blockSpin.setMinimum(float(value[:-3].replace(',', '.' )))

    def _onOpenPosChanged(self, value):
        '''
        closing position must be < opening position
        '''
        self.closeSpin.setMaximum(float(value[:-3].replace(',', '.' )))
        self.blockSpin.setMaximum(float(value[:-3].replace(',', '.' )))


    def _onBlockPosChanged(self, value):
        '''
        blocking position must between opening and closing position
        '''
        self.closeSpin.setMaximum(float(value[:-3].replace(',', '.' )))
        self.openSpin.setMinimum(float(value[:-3].replace(',', '.' )))

    
    def _onTypeChanged(self):
        '''
        show only relevant widgets
        '''
        if not self.hidden:
            if self.typeCombo.currentIndex() == 1:
                self.openLEdit.show()
                self.openLabel.show()
                self.closeLEdit.hide()
                self.closeLabel.hide()
            elif self.typeCombo.currentIndex() == 2:
                self.openLEdit.hide()
                self.openLabel.hide()
                self.closeLEdit.show()
                self.closeLabel.show()
            else:
                self.openLEdit.show()
                self.openLabel.show()
                self.closeLEdit.show()
                self.closeLabel.show()
        else:
            pass
    

    def _onBlockChecked(self):
        if not self.hidden:
            # print("option checkbox is checked:", self.blockCheck.isChecked())
            if self.blockCheck.isChecked():
                self.blockLabel.show()
                self.blockSLabel.show()
                self.blockLEdit.show()
                self.blockSpin.show()
            else:
                self.blockLabel.hide()
                self.blockSLabel.hide()
                self.blockLEdit.hide()
                self.blockSpin.hide()
        else:
            pass
