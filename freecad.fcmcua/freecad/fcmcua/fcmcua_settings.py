import os
import json

__dir__ = os.path.dirname(__file__)
__axis_params__ = os.path.join(__dir__, 'axis_params.fcmc')
__actuator_params__ = os.path.join(__dir__, 'actuator_params.fcmc')
__connection_params__ = os.path.join(__dir__, 'connection_params.fcmc')

class Settings:

    def save_connection_settings(self, addrLEdit, pollSpin):
        '''
        write connection parameters to file
        '''
        params = {}
        params['url'] = addrLEdit.text()
        params['poll'] = str(pollSpin.value()).replace(',', '.' )

        try:
            with open(__connection_params__, 'w') as f:
                f.write(json.dumps(params))
        except Exception as e:
            print("[Fcmcua] Error while saving to file:", e)
    

    def load_connection_settings(self, addrLEdit, pollSpin, axis_list, actu_list):
        '''
        load connection parameters from file
        '''
        self.load_axis_settings(axis_list)

        self.load_actuator_settings(actu_list)

        try:
            #poll-rate and url
            with open(__connection_params__, 'r') as f:
                params = json.loads(f.read())
        except Exception as e:
            print("[Fcmcua] Error while loading from file:", e)
            
        try:
            addrLEdit.setText(params['url'])
            pollSpin.setValue(float(params['poll'].replace(',', '.' )))
        except Exception as e:
            print("[Fcmcua] Error while applying loaded settings:", e)


    def save_axis_settings(self, axis_list):
        '''
        write axis parameters to file
        '''
        params = {}

        for e in range(len(axis_list)):
            entry = {}
            entry['nodeID'] = axis_list[e].nodeID.text()
            entry['sign'] = axis_list[e].sign.currentText()
            entry['multiplier'] = str(axis_list[e].multiSpin.value()).replace(',','.')
            entry['docName'] = axis_list[e].docName.text()
            entry['obj_label'] = axis_list[e].obj_label.text()
            entry['vector'] = axis_list[e].vector.currentText()
            entry['spd_pos'] = axis_list[e].spd_pos.currentText()
            params[str(e)] = entry
        try:
            with open(__axis_params__, 'w') as f:
                f.write(json.dumps(params))
        except Exception as e:
            print("[Fcmcua] Error while saving to file:", e)


    def load_axis_settings(self, axis_list):
        '''
        load axis parameters from file
        '''
        try:
            with open(__axis_params__, 'r') as f:
                params = json.loads(f.read())
        except Exception as e:
            print("[Fcmcua] Error while loading from file:", e)

        for e in range(len(axis_list)):
            try:
                axis_list[e].nodeID.setText(params[str(e)]['nodeID'])
                axis_list[e].sign.setCurrentText(params[str(e)]['sign'])
                axis_list[e].multiSpin.setValue(float(params[str(e)]['multiplier'].replace(',','.')))
                axis_list[e].docName.setText(params[str(e)]['docName'])
                axis_list[e].obj_label.setText(params[str(e)]['obj_label'])
                axis_list[e].vector.setCurrentText(params[str(e)]['vector'])
                axis_list[e].spd_pos.setCurrentText(params[str(e)]['spd_pos'])
            except Exception as e:
                print("[Fcmcua] Error while applying loaded settings:", e)


    def save_actuator_settings(self, actu_list):
        '''
        save actuator parameters to file
        '''
        params = {}

        for e in range(len(actu_list)):
            entry = {}

            # add all widget values to entry dict
            entry['type'] = actu_list[e].typeCombo.currentText()
            entry['blockOption'] = str(actu_list[e].blockCheck.isChecked())
            entry['nodeIdOpen'] = actu_list[e].openLEdit.text()
            entry['nodeIdBlock'] = actu_list[e].blockLEdit.text()
            entry['nodeIdClose'] = actu_list[e].closeLEdit.text()
            entry['docName'] = actu_list[e].docLEdit.text()
            entry['objLabel'] = actu_list[e].objLEdit.text()
            entry['vector'] = actu_list[e].vectorCombo.currentText()
            entry['openPos'] = str(actu_list[e].openSpin.value()).replace(',', '.' )
            entry['blockPos'] = str(actu_list[e].blockSpin.value()).replace(',', '.' )
            entry['closePos'] = str(actu_list[e].closeSpin.value()).replace(',', '.' )
            entry['openTime'] = str(actu_list[e].openTSpin.value()).replace(',', '.' )
            entry['closeTime'] = str(actu_list[e].closeTSpin.value()).replace(',', '.' )

            # add entry dict to params dict with actuator-No. as key
            params[str(e)] = entry
        
        try:
            with open(__actuator_params__, 'w') as f:
                f.write(json.dumps(params))
        except Exception as e:
            print("[Fcmcua] Error while saving to file:", e)


    def load_actuator_settings(self, actu_list):
            '''
            load actuator parameters from file
            '''
            try:
                with open(__actuator_params__, 'r') as f:
                    params = json.loads(f.read())
            except Exception as e:
                print("[Fcmcua] Error while loading from file:", e)

            for e in range(len(actu_list)):
                try:
                    actu_list[e].typeCombo.setCurrentText(params[str(e)]['type'])
                    actu_list[e].blockCheck.setChecked(params[str(e)]['blockOption'] == 'True')
                    actu_list[e].openLEdit.setText(params[str(e)]['nodeIdOpen'])
                    actu_list[e].blockLEdit.setText(params[str(e)]['nodeIdBlock'])
                    actu_list[e].closeLEdit.setText(params[str(e)]['nodeIdClose'])
                    actu_list[e].docLEdit.setText(params[str(e)]['docName'])
                    actu_list[e].objLEdit.setText(params[str(e)]['objLabel'])
                    actu_list[e].vectorCombo.setCurrentText(params[str(e)]['vector'])
                    actu_list[e].openSpin.setValue(float(params[str(e)]['openPos'].replace(',', '.' )))
                    actu_list[e].closeSpin.setValue(float(params[str(e)]['closePos'].replace(',', '.' )))
                    actu_list[e].blockSpin.setValue(float(params[str(e)]['blockPos'].replace(',', '.' )))
                    actu_list[e].openTSpin.setValue(float(params[str(e)]['openTime'].replace(',', '.' )))
                    actu_list[e].closeTSpin.setValue(float(params[str(e)]['closeTime'].replace(',', '.' )))
                except Exception as e:
                    print("[Fcmcua] Error while applying loaded settings:", e)
