from PySide2 import QtCore, QtWidgets
import FreeCAD
import FreeCADGui
import os

from actuator_widgets import ActuatorWidgets
from fcmcua_settings import Settings
from freecad.fcmcua import ICONPATH, ACTUATORS


class ActuatorPanel:
    
    def __init__(self, widget, count):
        #number of actuators
        self.actuators = count

        #attribute for storing all actuator widgets
        self.actu_list = []

        # instance of Settings
        self.settings = Settings()

        #reference to QWidget
        self.form = widget

        #Grid Layout
        main_layout = QtWidgets.QGridLayout(self.form)
        group_layout = []
        groups = []

        if self.actuators != 0:
            for i in range(self.actuators):
                # fill list with actuator widgets
                self.actu_list.append(ActuatorWidgets())

                # fill list of group box layouts per actuator
                group_layout.append(QtWidgets.QGridLayout())

                #create a group box per actuator
                groups.append(QtWidgets.QGroupBox('Actuator' + str(i+1)))

                # begin placing widgets in the layout at row 0
                start_row = 0

                # add child-widgets to layout
                group_layout[i].addWidget(self.actu_list[i].typeLabel, start_row, 0, 1, 2)
                group_layout[i].addWidget(self.actu_list[i].typeCombo, start_row, 2, 1, 8)
                group_layout[i].addWidget(self.actu_list[i].blockCheck, start_row+1, 0, 1, 10)
                group_layout[i].addWidget(self.actu_list[i].openLabel, start_row+2, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].openLEdit, start_row+2, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].blockLabel, start_row+3, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].blockLEdit, start_row+3, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].closeLabel, start_row+4, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].closeLEdit, start_row+4, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].fcLabel, start_row+5, 0, 1, 2)
                group_layout[i].addWidget(self.actu_list[i].docLEdit, start_row+5, 3, 1, 3)
                group_layout[i].addWidget(self.actu_list[i].objLEdit, start_row+5, 6, 1, 3)
                group_layout[i].addWidget(self.actu_list[i].vectorCombo, start_row+5, 9, 1, 1)
                group_layout[i].addWidget(self.actu_list[i].openSLabel, start_row+6, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].openSpin, start_row+6, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].blockSLabel, start_row+7, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].blockSpin, start_row+7, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].closeSLabel, start_row+8, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].closeSpin, start_row+8, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].openTLabel, start_row+9, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].openTSpin, start_row+9, 5, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].closeTLabel, start_row+10, 0, 1, 5)
                group_layout[i].addWidget(self.actu_list[i].closeTSpin, start_row+10, 5, 1, 5)

                # assign layout to groupbox
                groups[i].setLayout(group_layout[i])

                # add groupbox to main layout
                main_layout.addWidget(groups[i])

            # load actuator parameters from file
            self.settings.load_actuator_settings(self.actu_list)

        else:
            # no actuator configured
            defaultLabel = QtWidgets.QLabel('No actuator configured in fcmcua.ini')
            main_layout.addWidget(defaultLabel)


    def accept(self):
        if self.actuators > 0:
            self.settings.save_actuator_settings(self.actu_list)
        FreeCADGui.Control.closeDialog() #close the dialog

    
    def reject(self):
        FreeCADGui.Control.closeDialog() #close the dialog

    
class _ActuatorSetup:
    def Activated(self):
        #create and show the panel
        baseWidget = QtWidgets.QWidget()
        panel = ActuatorPanel(baseWidget, ACTUATORS)
        FreeCADGui.Control.showDialog(panel)

    def GetResources(self):
        # icon and command information
        MenuText = QtCore.QT_TRANSLATE_NOOP(
            'FCMC_ActuatorSetup',
            'Actuator settings dialog')
        ToolTip = QtCore.QT_TRANSLATE_NOOP(
            'FCMC_ActuatorSetup',
            'Link OPC UA nodes (boolean) to FreeCAD objects')
        return {
            'Pixmap': os.path.join(ICONPATH, "fcmcua_actuator.svg"),
            'MenuText': MenuText,
            'ToolTip': ToolTip}

    def IsActive(self):
        # The command will be active if there is an active document
        return not FreeCAD.ActiveDocument is None


FreeCADGui.addCommand('FCMC_ActuatorSetup', _ActuatorSetup())