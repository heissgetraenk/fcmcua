from PySide2 import QtCore, QtWidgets
import FreeCAD
import FreeCADGui
import os
import json

from opc_client import OpcClient
from axis_widgets import AxisWidgets
from actuator_widgets import ActuatorWidgets
from freecad.fcmcua import ICONPATH, AXES, ACTUATORS
from fcmcua_settings import Settings


class FcmcuaPanel:
    def __init__(self,widget, axCount, actCount):
        #number of axes
        self.axes = axCount

        #number of actuators
        self.actuators = actCount

        #list for storing all axis settings widgets
        self.axis_list = []

        # list for storing all actuator settings widgets
        self.actu_list = []

        # instance of Settings
        self.settings = Settings()
        
        #reference to QWidget
        self.form = widget

        #Grid Layout
        layout = QtWidgets.QGridLayout(self.form)

        # ---- row 0: opc server address
        # Label:
        self.addrLabel = QtWidgets.QLabel("OPC UA server URL")
        #line edit to receive the address
        self.addrLEdit = QtWidgets.QLineEdit("opc.tcp://127.0.0.1:4840")
        
        # row 0, column 0, rowspan 1, colspan 4
        layout.addWidget(self.addrLabel,0,0,1,4)
        # row 0, column 4, rowspan 1, colspan 6
        layout.addWidget(self.addrLEdit,0,4,1,6)

        # ---- row 1: polling rate for updates to the CAD document
        # Label:
        self.pollLabel = QtWidgets.QLabel("Polling rate")
        #line edit to receive the address
        self.pollSpin = QtWidgets.QDoubleSpinBox()
        self.pollSpin.setRange(10, 1000)
        self.pollSpin.setValue(100)
        self.pollSpin.setSuffix(' ms')
        
        # row 1, column 0, rowspan 1, colspan 4
        layout.addWidget(self.pollLabel,1,0,1,4)
        # row 1, column 4, rowspan 1, colspan 6
        layout.addWidget(self.pollSpin,1,4,1,6) 

        # ---- row 2: connect/disconnect buttons
        self.connBtn = QtWidgets.QPushButton("Connect")
        self.disconnBtn = QtWidgets.QPushButton("Disconnect")

        # row 2, column 0, rowspan 1, colspan 5
        layout.addWidget(self.connBtn,2,0,1,5)
        # row 2, column 5, rowspan 1, colspan 5
        layout.addWidget(self.disconnBtn,2,5,1,5) 

        # ---- row 3: server state indicator
        self.compTimeLabel = QtWidgets.QLabel("Compute time: -- ms")

        # row 3, column 0, rowspan 1, colspan 5
        layout.addWidget(self.compTimeLabel, 3, 0, 1, 5)

        self.stateLabel = QtWidgets.QLabel("Server: Disconnected")
        self.stateLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        # row 3, column 7, rowspan 1, colspan 3
        layout.addWidget(self.stateLabel, 3, 7, 1, 3)

        # signal/slot connections connect/disconnect buttons
        self.connBtn.clicked.connect(self.onConnClicked)
        self.disconnBtn.clicked.connect(self.onDisconnClicked)

        for i in range(self.axes):
            # create setting widget and gather them in a list
            self.axis_list.append(AxisWidgets(i)) 

        for j in range(self.actuators):
            self.actu_list.append(ActuatorWidgets(hidden=True))

        # initialize opc client object
        self.opc = OpcClient(self.axis_list, self.actu_list)

        # load previous settings from file params.fcmc
        self.settings.load_connection_settings(self.addrLEdit, self.pollSpin, self.axis_list, self.actu_list)

    
    def onConnClicked(self):
        try:
            self.stateLabel.setText("Server: Connected")
            self.opc.start(self.addrLEdit.text(), self.pollSpin.value(), self.compTimeLabel)
        except Exception as e:
            self.stateLabel.setText("Server: Error")
            self.compTimeLabel.setText("Compute time: -- ms")
            print("[Fcmcua] Error while connecting:", e)



    def onDisconnClicked(self):
        try:
            self.stateLabel.setText("Server: Disconnected")
            self.compTimeLabel.setText("Compute time: -- ms")
            self.opc.stop()
        except Exception as e:
            self.stateLabel.setText("Server: Error")
            self.compTimeLabel.setText("Compute time: -- ms")
            print("[Fcmcua] Error while disconnecting:", e)

       
    def accept(self):
        self.settings.save_connection_settings(self.addrLEdit, self.pollSpin)
        self.opc.stop()
        FreeCADGui.Control.closeDialog() #close the dialog

    
    def reject(self):
        self.opc.stop()
        FreeCADGui.Control.closeDialog() #close the dialog


# GUI command that links the Python script
class _LinkToOpcUa:
    def Activated(self):
        #create and show the panel
        baseWidget = QtWidgets.QWidget()
        panel = FcmcuaPanel(baseWidget, AXES, ACTUATORS)
        FreeCADGui.Control.showDialog(panel)

    def GetResources(self):
        # icon and command information
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'FCMC_LinkToOpcUa',
            'Connection settings dialog')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'FCMC_LinkToOpcUa',
            'Set the server address connect to the OPC UA Server')
        return {
            'Pixmap': os.path.join(ICONPATH, "fcmcua_wb.svg"),
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        # The command will be active if there is an active document
        return not FreeCAD.ActiveDocument is None


FreeCADGui.addCommand('FCMC_LinkToOpcUa', _LinkToOpcUa())
