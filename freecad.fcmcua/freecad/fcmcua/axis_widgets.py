from PySide2 import QtCore, QtWidgets

__min_multi__ = 0.0
__max_multi__ = 1000.0
__default_multi__ = 1.0

class AxisWidgets(QtWidgets.QWidget):
    '''
    Storage class for the individual widgets in a settings entry
    '''
    def __init__(self, id):
        self.id= id
        self.widgets=[]
        #node LineEdit
        self.nodeID = QtWidgets.QLineEdit("ns=2;i=2")
        self.widgets.append(self.nodeID)

        #opc variable LineEdit
        # self.var = QtWidgets.QLineEdit("Variable " + str(self.id))
        # self.widgets.append(self.var)

        # equals Label
        self.equals = QtWidgets.QLabel("=")
        self.widgets.append(self.equals)
        # math sign comboBox
        self.sign = QtWidgets.QComboBox()
        self.sign.addItems(["+", "-"])
        self.widgets.append(self.sign)
        # multiplier spinBox
        self.multiSpin = QtWidgets.QDoubleSpinBox()
        self.multiSpin.setValue(__default_multi__)
        self.multiSpin.setRange(__min_multi__, __max_multi__)
        self.widgets.append(self.multiSpin)
        # docName LineEdit
        self.docName = QtWidgets.QLineEdit("Document")
        self.widgets.append(self.docName)
        # object label LineEdit
        self.obj_label = QtWidgets.QLineEdit("Object Label")
        self.widgets.append(self.obj_label)
        # vector component comboBox
        self.vector = QtWidgets.QComboBox()
        self.vector.addItems(["x", "y", "z", "deg"])
        self.widgets.append(self.vector)
        # speed/pos axis comboBox
        self.spd_pos = QtWidgets.QComboBox()
        self.spd_pos.addItems(["pos", "speed"])
        self.widgets.append(self.spd_pos)