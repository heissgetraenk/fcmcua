from asyncua.sync import Client, ua
from opc_cad_updater import CadUpdater
import time
from datetime import datetime
import FreeCADGui as Gui
from fcmcua_actuator_logic import ActuatorLogic

class OpcClient():
    def __init__(self, axis_list, actu_list ):
        # OpcClient is initialised during workbench init
        
        # list of all axis configurations
        self.axis_list = axis_list
        # list of all actuator configurations
        self.actu_list = actu_list


        self.actu_objs = []
        

    def start(self, address, poll_rate):
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
            root = client.get_root_node()
            #variables on the opc server:
            axes = []
            actuators = []

            # gather axis variables
            for n in range(len(self.axis_list)):
                # node = self.set_list[n].nodeID.text()
                axes.append(client.get_node(self.axis_list[n].nodeID.text()))

            # gather actuator variables in sets of three [open, close, block]
            for a in range(len(self.actu_list)):
                # depending on type, get one or two variables
                type = int(self.actu_list[a].typeCombo.currentText()[:1])
                open = client.get_node(self.actu_list[a].openLEdit.text() if (type == 1 or type == 2) else False)
                close = client.get_node(self.actu_list[a].closeLEdit.text() if (type == 1 or type == 3) else False)
                # if the conditional block option is set, get also the node for that
                block = client.get_node(self.actu_list[a].blockLEdit.text()) if (self.actu_list[a].blockCheck.isChecked()) else False
                # per actuator, collect all nodes to be gotten from the opc server and place them in a list-entry
                actuators.append([open, close, block])
            
            # initialize lists for the axis values coming from the opc server
            prev_axis_values = [0.0] * len(self.axis_list)
            axis_values = [0.0] * len(self.axis_list)

            # initialize lists for the actuator triggers coming from the opc server 
            # or the values from the actuator logic objects
            actu_triggers = [[False] * (len(actuators[0])) for i in range(len(self.actu_list))]
            actu_values = [False for i in range(len(self.actu_list))]
            prev_actu_values = [False for i in range(len(self.actu_list))]

            # initialize the object for updating the FreeCAD document
            upd = CadUpdater(self.axis_list, axis_values, self.actu_list, actu_values)

            # only connect if the active document contains a valid Assembly4 model
            if upd.checkModel() is None:
                # error message
                print("No Assembly4 container found in active document")

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
        except:
            print("Exception while connecting to opc server")

        # prepare benchmarking
        total_time = 0.0
        cycles = 0

        # main loop
        while self.running:
            before = datetime.now()

            # measure how long the cycle takes before sleeping
            t_start = datetime.now()
            # get axis values from server
            for v in axes:
                try:
                    axis_values[axes.index(v)] = v.get_value()
                except:
                    pass

            # get actuator trigger values from server
            for set in actuators:
                for id in set:
                    try:
                        actu_triggers[actuators.index(set)][set.index(id)] = id.get_value()
                    except:
                        # not a valid opc node
                        pass


            # get actuator target values as calculated by the actuator logic objects
            for a in range(len(self.actu_list)):
                actu_values[a] = self.actu_objs[a].get_current_pos(actu_triggers[a])

            # print(actu_values)

            # update and recompute the FreeCAD document if an axis value changed
            updated = False
            for n in range(len(self.axis_list)):
                if axis_values[n] != prev_axis_values[n]:
                    upd.updateCAD()
                    updated = True
                    break

            # update and recompute the FreeCAD document if an actuator value changed
            # but only if updateCAD has not yet been called in this loop-cycle
            if not updated:
                for m in range(len(self.actu_list)):
                    if actu_values[m] != prev_actu_values[m]:
                        upd.updateCAD()
                        break

            # remember the values of the previous pass
            for n in range(len(self.axis_list)):
                prev_axis_values[n] = axis_values[n]

            for m in range(len(self.actu_list)):
                prev_actu_values[m] = actu_values[m]

            # updateGui to prevent the loop from blocking the GUI
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

            if updated:
                total_time += time_elapsed
                cycles += 1
                if cycles > 0:
                    avg = total_time / cycles
                    print("Average Opc Cycle time [s]: ", avg)
           
        # after connection was stopped
        client.disconnect()


    def stop(self):
        self.running = False

