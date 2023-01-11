from PySide2 import QtCore, QtWidgets
import FreeCAD
import FreeCADGui
import os
import json

from axis_widgets import AxisWidgets
from freecad.fcmcua import ICONPATH, AXES

__dir__ = os.path.dirname(__file__)
__axis_params__ = os.path.join(__dir__, 'axis_params.fcmc')

class AxisPanel:

    def __init__(self, widget, count):
        #number of axes
        self.axes = count

        #attribute for storing all settings widgets
        self.axis_list = []

        # some variables
        self.poll_rate = 50
        
        #reference to QWidget
        self.form = widget

        #Grid Layout
        layout = QtWidgets.QGridLayout(self.form)

        # ---- row 0: settings column headers
        # OPC UA side:
        self.opcLabel = QtWidgets.QLabel("Node Id")
        # FreeCad side:
        self.multiLabel = QtWidgets.QLabel("Factor")
        self.docLabel = QtWidgets.QLabel("Document")
        self.objLabel = QtWidgets.QLabel("LCS")
        self.vectorLabel = QtWidgets.QLabel("Offset")
        self.typeLabel = QtWidgets.QLabel("Type")

        # row 0, column 0, rowspan 1, colspan 3
        layout.addWidget(self.opcLabel,0,0,1,3)
        # row 0, column 4, rowspan 1, colspan 1
        layout.addWidget(self.multiLabel,0,4,1,1)
        # row 0, column 5, rowspan 1, colspan 2
        layout.addWidget(self.docLabel,0,5,1,2)
        # row 0, column 7, rowspan 1, colspan 2
        layout.addWidget(self.objLabel,0,7,1,2)
        # row 0, column 9, rowspan 1, colspan 2
        layout.addWidget(self.vectorLabel,0,9,1,1)
        # row 0, column 5, rowspan 1, colspan 2
        layout.addWidget(self.typeLabel,0,10,1,1)

        # ---- row 1..n: settings widgets
        for i in range(self.axes):
            # create setting widget and gather them in a list
            self.axis_list.append(AxisWidgets(i)) 
            # starting column index
            col = 0 
            # list of column widths 
            col_spans = [2,1,1,1,2,2,1,1] 
            # add widgets to layout with their respective column width, increment the column index accordingly
            for w in range(len(self.axis_list[0].widgets)):
                layout.addWidget(self.axis_list[i].widgets[w],1+i,col,1,col_spans[w])
                col += col_spans[w]

        #load previous settings from file params.fcmc
        self.load()

    def save(self):
        '''
        write axis parameters to file
        '''
        params = {}
        # params['url'] = self.address
        # params['poll'] = str(self.poll_rate)

        for e in range(len(self.axis_list)):
            entry = {}
            entry['nodeID'] = self.axis_list[e].nodeID.text()
            entry['sign'] = self.axis_list[e].sign.currentText()
            entry['multiplier'] = str(self.axis_list[e].multiSpin.value()).replace(',','.')
            entry['docName'] = self.axis_list[e].docName.text()
            entry['obj_label'] = self.axis_list[e].obj_label.text()
            entry['vector'] = self.axis_list[e].vector.currentText()
            entry['spd_pos'] = self.axis_list[e].spd_pos.currentText()
            params[str(e)] = entry
        try:
            with open(__axis_params__, 'w') as f:
                f.write(json.dumps(params))
        except:
            pass


    def load(self):
        '''
        load axis parameters from file
        '''
        try:
            with open(__axis_params__, 'r') as f:
                params = json.loads(f.read())

            # self.address = params['url']
            # self.poll_rate = float(params['poll'].replace(',', '.' ))

            for e in range(len(self.axis_list)):
                try:
                    self.axis_list[e].nodeID.setText(params[str(e)]['nodeID'])
                    self.axis_list[e].sign.setCurrentText(params[str(e)]['sign'])
                    self.axis_list[e].multiSpin.setValue(float(params[str(e)]['multiplier'].replace(',','.')))
                    self.axis_list[e].docName.setText(params[str(e)]['docName'])
                    self.axis_list[e].obj_label.setText(params[str(e)]['obj_label'])
                    self.axis_list[e].vector.setCurrentText(params[str(e)]['vector'])
                    self.axis_list[e].spd_pos.setCurrentText(params[str(e)]['spd_pos'])
                except:
                    break
        except:
            pass

    def accept(self):
        self.save()
        FreeCADGui.Control.closeDialog() #close the dialog

    
    def reject(self):
        FreeCADGui.Control.closeDialog() #close the dialog
    

class _AxisSetup:
    def Activated(self):
        #create and show the panel
        baseWidget = QtWidgets.QWidget()
        panel = AxisPanel(baseWidget, AXES)
        FreeCADGui.Control.showDialog(panel)

    def GetResources(self):
        # icon and command information
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'FCMC_AxisSetup',
            'Axis settings dialog')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'FCMC_AxisSetup',
            'Link OPC UA nodes (non-boolean) to FreeCAD objects')
        return {
            'Pixmap': os.path.join(ICONPATH, "fcmcua_axes.svg"),
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        # The command will be active if there is an active document
        return not FreeCAD.ActiveDocument is None


FreeCADGui.addCommand('FCMC_AxisSetup', _AxisSetup())
