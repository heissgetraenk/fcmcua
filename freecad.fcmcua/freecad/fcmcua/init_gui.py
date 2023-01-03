import os
import FreeCADGui as Gui
import FreeCAD as App



class Fcmcua(Gui.Workbench):
    """
    class which gets initiated at startup of the gui
    """

    from freecad.fcmcua import ICONPATH
    MenuText = "FCMC UA"
    ToolTip = "FreeCAD Motion Control Conector OPC UA"
    Icon = os.path.join(ICONPATH, "fcmcua_wb.svg")

    def GetClassName(self):
        return "Gui::PythonWorkbench"

    def Initialize(self):
        """
        This function is called at the first activation of the workbench.
        here is the place to import all the commands
        """
        import fcmcua_cmd, fcmcua_axes_cmd, fcmcua_actuators_cmd
        self.toolbox = ['FCMC_LinkToOpcUa', 'FCMC_AxisSetup', 'FCMC_ActuatorSetup']

        self.appendToolbar("Tools", self.toolbox)
        self.appendMenu("Tools", self.toolbox)

    def Activated(self):
        '''
        code which should be computed when a user switches to this workbench
        '''
        pass

    def Deactivated(self):
        '''
        code which should be computed when this workbench is deactivated
        '''
        pass


Gui.addWorkbench(Fcmcua())
