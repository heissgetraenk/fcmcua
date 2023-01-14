from asyncua.sync import Client
from opc_cad_updater import CadUpdater
import time
import FreeCADGui as Gui
from datetime import datetime
from fcmcua_actuator_logic import ActuatorLogic

class OpcClient():
    def __init__(self, axis_list, actu_list ):
        # OpcClient is initialised during workbench init
        
        # list of all axis configurations
        self.axis_list = axis_list
        # list of all actuator configurations
        self.actu_list = actu_list
        self.actu_objs = []
        

    def start(self, address, poll_rate, compT_widget):
        '''
        set-up and run a client-server connection to an opc ua server
        '''
        # opc server url and poll rate
        self.url = address
        self.poll_rate = poll_rate

        # initialize opc client with address to the server
        client = Client(url=self.url)

        # loop control variable
        self.running = True

        try:
            client.connect()

            # root = client.get_root_node()

            #variables on the opc server:
            self.axes = []
            self.actuators = []

            # gather axis variables
            for n in range(len(self.axis_list)):
                # node = self.set_list[n].nodeID.text()
                self.axes.append(client.get_node(self.axis_list[n].nodeID.text()))

            # gather actuator variables in sets of three [open, close, block]
            for a in range(len(self.actu_list)):
                # depending on type, get one or two variables
                type = int(self.actu_list[a].typeCombo.currentText()[:1])
                open = client.get_node(self.actu_list[a].openLEdit.text() if (type == 1 or type == 2) else False)
                close = client.get_node(self.actu_list[a].closeLEdit.text() if (type == 1 or type == 3) else False)
                # if the conditional block option is set, get also the node for that
                block = client.get_node(self.actu_list[a].blockLEdit.text()) if (self.actu_list[a].blockCheck.isChecked()) else False
                # per actuator, collect all nodes to be gotten from the opc server and place them in a list-entry
                self.actuators.append([open, close, block])
            
            # initialize lists for the axis values coming from the opc server
            self.prev_axis_values = [0.0] * len(self.axis_list)
            self.axis_values = [0.0] * len(self.axis_list)

            # initialize lists for the actuator triggers coming from the opc server 
            # or the values from the actuator logic objects
            self.actu_triggers = [[False] * (len(self.actuators[0])) for i in range(len(self.actu_list))]
            self.actu_values = [False for i in range(len(self.actu_list))]
            self.prev_actu_values = [False for i in range(len(self.actu_list))]

            # initialize the object for updating the FreeCAD document
            self.upd = CadUpdater(self.axis_list, self.actu_list)

            # only connect if the active document contains a valid Assembly4 model
            if self.upd.checkModel() is None:
                # error message
                print("[Fcmcua] No Assembly4 container found in active document")

                # abort communication loop
                self.running = False

                # disconnect the client and return
                client.disconnect()
                return

            # initialize one actuator logic object per set of actuator configurations in actu_list
            # pass reference to the trigger variable-sets and to each actuator's parameters
            for o in range(len(self.actu_list)):
                # gather all actuator logic objects in a list
                self.actu_objs.append(ActuatorLogic(self.actu_list[o], self.poll_rate))
        except Exception as e: 
            raise e


        # prepare benchmarking
        total_time = 0.0
        cycles = 0
        self.do_upd = False
        while not self.do_upd:
            self._poll_opc()

        # main loop
        while self.running:
            before = datetime.now()

            # measure how long the cycle takes before sleeping
            t_start = datetime.now()
            
            self.do_upd = False

            # get values from opc server
            self._poll_opc()

            # update the assembly
            self._updateCad()

            # update the Gui to prevent freeze
            Gui.updateGui()
    
            # wait for poll_rate (ms) --> calculate seconds by 1/1000.0
            # dont sleep longer than the poll rate, if the opc interaction takes a significant amount of time
            t_end = datetime.now()
            sleep = (self.poll_rate/1000) - (t_end - t_start).total_seconds()
            if sleep > 0: 
                time.sleep(sleep)

            # benchmarking
            after = datetime.now()
            time_elapsed = (after - before).total_seconds()

            if self.do_upd:
                total_time += time_elapsed
                cycles += 1
                if cycles > 0:
                    avg = total_time / cycles
                    compT_widget.setText(f"Compute time: {round(avg*1000, 1)} ms")
                    # print("Average Opc Cycle time [s]: ", avg)
           
        # after connection was stopped
        client.disconnect()


    def stop(self):
        self.running = False

    
    def _poll_opc(self):
        # get axis values from server
        # for v in self.axes:
        #     try:
        #         self.axis_values[self.axes.index(v)] = v.get_value()
        #     except:
        #         pass
        self.axis_values = list(map(self._get_value, self.axes))

        # get actuator trigger values from server
        # for set in self.actuators:
        #     for id in set:
        #         try:
        #             self.actu_triggers[self.actuators.index(set)][set.index(id)] = id.get_value()
        #         except:
        #             # not a valid opc node
        #             pass
        self.actu_triggers = list(map(self._get_act_values, self.actuators))
        # print(self.actu_triggers)
        # print(len(self.actu_list))
        # print(len(self.actu_values))


        # get actuator target values as calculated by the actuator logic objects
        for a in range(len(self.actu_list)):
            blockOption = self.actu_list[a].blockCheck.isChecked()
            self.actu_values[a] = self.actu_objs[a].get_current_pos(self.actu_triggers[a], blockOption)

        # update and recompute the FreeCAD document
        for n in range(len(self.axis_list)):
            value_changed = (self.axis_values[n] != self.prev_axis_values[n])
            speed_gr_zero = ((self.axis_list[n].spd_pos.currentText() == 'speed') and self.axis_values[n] > 0.0)
            # do update if a value changed or a speed axis/spindle has > 0
            if value_changed or speed_gr_zero:
                self.do_upd = True
                break


        # update and recompute the FreeCAD document if an actuator value changed
        # but only if updateCAD has not yet been called in this loop-cycle
        if not self.do_upd:
            for m in range(len(self.actu_list)):
                if self.actu_values[m] != self.prev_actu_values[m]:
                    self.do_upd = True
                    break

        # remember the values of the previous pass
        for n in range(len(self.axis_list)):
            self.prev_axis_values[n] = self.axis_values[n]

        for m in range(len(self.actu_list)):
            self.prev_actu_values[m] = self.actu_values[m]

    
    def _get_value(self, node):
        try:
            return node.get_value()
        except:
            # not a valid node id
            return False


    def _get_act_values(self, set):
        return list(map(self._get_value, set))

    
    def _updateCad(self):
        if self.do_upd: 
            self.upd.updateCAD(self.axis_values, self.actu_values, self.poll_rate)

