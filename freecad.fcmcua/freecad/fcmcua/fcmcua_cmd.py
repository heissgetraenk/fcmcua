from PySide2 import QtCore, QtWidgets
import FreeCAD
import FreeCADGui
import os
import json

from opc_client import OpcClient
from axis_widgets import AxisWidgets
from actuator_widgets import ActuatorWidgets
from freecad.fcmcua import ICONPATH, AXES, ACTUATORS

__dir__ = os.path.dirname(__file__)
__axis_params__ = os.path.join(os.path.dirname(__file__), 'axis_params.fcmc')
__actuator_params__ = os.path.join(__dir__, 'actuator_params.fcmc')
__connection_params__ = os.path.join(__dir__, 'connection_params.fcmc')

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

        # # ---- row 2: settings column headers
        # # Label:
        # self.opcLabel = QtWidgets.QLabel("OPC UA")
        # # Label:
        # self.fcLabel = QtWidgets.QLabel("FreeCAD")

        # # row 2, column 0, rowspan 1, colspan 3
        # layout.addWidget(self.opcLabel,2,0,1,3)
        # # row 2, column 3, rowspan 1, colspan 2
        # layout.addWidget(self.fcLabel,2,3,1,2) 

        # ---- row 2: connect/disconnect buttons
        self.connBtn = QtWidgets.QPushButton("Connect")
        self.disconnBtn = QtWidgets.QPushButton("Disconnect")

        # row 2, column 0, rowspan 1, colspan 5
        layout.addWidget(self.connBtn,2,0,1,5)
        # row 2, column 5, rowspan 1, colspan 5
        layout.addWidget(self.disconnBtn,2,5,1,5) 

        # signal/slot connections connect/disconnect buttons
        self.connBtn.clicked.connect(self.onConnClicked)
        self.disconnBtn.clicked.connect(self.onDisconnClicked)

        for i in range(self.axes):
            # create setting widget and gather them in a list
            self.axis_list.append(AxisWidgets(i)) 

        for j in range(self.actuators):
            self.actu_list.append(ActuatorWidgets(hidden=True))

        # initialize opc client object
        self.opc = OpcClient(self.axis_list, self.actu_list, self.addrLEdit.text(), self.pollSpin.value())

        # load previous settings from file params.fcmc
        self.load()

    
    def onConnClicked(self):
        self.opc.start()


    def onDisconnClicked(self):
        self.opc.stop()

       
    def accept(self):
        self.save()
        FreeCADGui.Control.closeDialog() #close the dialog

    
    def reject(self):
        self.opc.stop()
        FreeCADGui.Control.closeDialog() #close the dialog
    
    
    def save(self):
        '''
        write connection parameters to file
        '''
        params = {}
        params['url'] = self.addrLEdit.text()
        params['poll'] = str(self.pollSpin.value()).replace(',', '.' )

        try:
            with open(__connection_params__, 'w') as f:
                f.write(json.dumps(params))
        except:
            pass

        params.clear()

        for e in range(len(self.axis_list)):
            entry = {}
            entry['nodeID'] = self.axis_list[e].nodeID.text()
            entry['sign'] = self.axis_list[e].sign.currentText()
            entry['multiplier'] = str(self.axis_list[e].multiSpin.value()).replace(',','.')
            entry['docName'] = self.axis_list[e].docName.text()
            entry['obj_label'] = self.axis_list[e].obj_label.text()
            entry['vector'] = self.axis_list[e].vector.currentText()
            params[str(e)] = entry
        try:
            with open(__axis_params__, 'w') as f:
                f.write(json.dumps(params))
        except:
            pass


    def load(self):
        '''
        load connection parameters from file
        '''
        try:
            # axis parameters
            with open(__axis_params__, 'r') as f:
                params = json.loads(f.read())

        except:
            pass 

        for e in range(len(self.axis_list)):
            try:
                self.axis_list[e].nodeID.setText(params[str(e)]['nodeID'])
                self.axis_list[e].sign.setCurrentText(params[str(e)]['sign'])
                self.axis_list[e].multiSpin.setValue(float(params[str(e)]['multiplier'].replace(',','.')))
                self.axis_list[e].docName.setText(params[str(e)]['docName'])
                self.axis_list[e].obj_label.setText(params[str(e)]['obj_label'])
                self.axis_list[e].vector.setCurrentText(params[str(e)]['vector'])
            except:
                break
            
        try:
            # actuator parameters
            with open(__actuator_params__, 'r') as f:
                params = json.loads(f.read())
        except:
            pass

        for e in range(len(self.actu_list)):
            try:
                self.actu_list[e].typeCombo.setCurrentText(params[str(e)]['type'])
                self.actu_list[e].blockCheck.setChecked(bool(params[str(e)]['blockOption']))
                self.actu_list[e].openLEdit.setText(params[str(e)]['nodeIdOpen'])
                self.actu_list[e].blockLEdit.setText(params[str(e)]['nodeIdBlock'])
                self.actu_list[e].closeLEdit.setText(params[str(e)]['nodeIdClose'])
                self.actu_list[e].docLEdit.setText(params[str(e)]['docName'])
                self.actu_list[e].objLEdit.setText(params[str(e)]['objLabel'])
                self.actu_list[e].vectorCombo.setCurrentText(params[str(e)]['vector'])
                self.actu_list[e].openSpin.setValue(float(params[str(e)]['openPos'].replace(',', '.' )))
                self.actu_list[e].blockSpin.setValue(float(params[str(e)]['blockPos'].replace(',', '.' )))
                self.actu_list[e].closeSpin.setValue(float(params[str(e)]['closePos'].replace(',', '.' )))
                self.actu_list[e].openTSpin.setValue(float(params[str(e)]['openTime'].replace(',', '.' )))
                self.actu_list[e].closeTSpin.setValue(float(params[str(e)]['closeTime'].replace(',', '.' )))
            except:
                break

        try:
            #poll-rate and url
            with open(__connection_params__, 'r') as f:
                params = json.loads(f.read())
            
            self.addrLEdit.setText(params['url'])
            self.pollSpin.setValue(float(params['poll'].replace(',', '.' )))
        except:
            pass


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
            'Set the server address and the path to the configuration files')
        return {
            'Pixmap': os.path.join(ICONPATH, "fcmcua_wb.svg"),
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        # The command will be active if there is an active document
        return not FreeCAD.ActiveDocument is None


FreeCADGui.addCommand('FCMC_LinkToOpcUa', _LinkToOpcUa())
