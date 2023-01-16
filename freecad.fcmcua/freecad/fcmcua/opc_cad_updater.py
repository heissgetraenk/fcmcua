import FreeCAD as App
import math

# uncomment to calculate and display compute times
# from datetime import datetime

# round values received from FreeCAD to 3 decimals
_RND_PARAM = 3

class CadUpdater():
    """
    Update the values of the given FreeCAD documents
    """
    def __init__(self, axis_list, actu_list):
        self.axis_list = axis_list
        self.actu_list = actu_list

        # variables used in calculating compute times
        self.cycles = 0
        self.total_rec = self.total_upd = 0.0


    def updateCAD(self, axis_values, actu_values, poll_rate):
        '''method to interact with FreeCAD model'''
        self.axis_values = axis_values
        self.actu_values = actu_values
        
        # uncomment to calculate and display compute times
        # b_upd = datetime.now()
        
        # loop counter as an index for the values-list 
        itr = 0

        # iterate through all axis settings entries and update them
        for obj in self.axis_list:
            self._updateAxis(obj, itr, poll_rate)
            itr += 1

        # reset loop counter
        itr = 0
        
        # iterate through all actuator settings entries and update them
        for obj in self.actu_list:
            self._updateActuator(obj, itr)
            itr += 1

        self._recompute()
        
        # uncomment to calculate and display compute times
        # a_rec = a_upd = datetime.now()
        # rec_cyc = (a_rec - b_rec).total_seconds()
        # upd_cyc = (a_upd - b_upd).total_seconds()

        # self.total_rec += rec_cyc
        # self.total_upd += upd_cyc
        # self.cycles += 1
        # if self.cycles > 0:
        #     avg_rec = self.total_rec / self.cycles
        #     avg_upd = self.total_upd / self.cycles
            # print("Average recompute time [s]: ", avg_rec)
            # print("Average updateCAD time [s]: ", avg_upd)

    def _getFcValues(self, doc, obj):
            try:    
                # get actual placement from the document
                old_X = round(App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Base.x, _RND_PARAM)
                old_Y = round(App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Base.y, _RND_PARAM)
                old_Z = round(App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Base.z, _RND_PARAM)

                # get actual rotation from the document
                rad_angle = App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Rotation.Angle
                old_angle = round(rad_angle * 180 / math.pi, _RND_PARAM)
                rot_x = round(App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Rotation.Axis.x, _RND_PARAM)
                rot_y = round(App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Rotation.Axis.y, _RND_PARAM)
                rot_z = round(App.getDocument(doc).getObjectsByLabel(obj)[0].AttachmentOffset.Rotation.Axis.z, _RND_PARAM)
            except Exception as e:
                print("[Fcmcua] Error while getting values from the freecad document", e)

            return {'old_X':old_X, 'old_Y':old_Y, 'old_Z':old_Z, 'old_angle':old_angle,
                    'rot_x':rot_x, 'rot_y':rot_y, 'rot_z':rot_z}


    def _updateAxis(self, obj, itr, poll_rate):
        # extract document name and LCS label
        doc = obj.docName.text()
        fc_obj = obj.obj_label.text()

        # get previous values
        prev = self._getFcValues(doc, fc_obj)

        #calculate and set new placement vector values
        try:    
            # get the multiplier for the given axis
            multi = self.axis_list[itr].multiSpin.value()

            # is the value coming from opc a position or a spindle/speed value?
            if obj.spd_pos.currentText() == 'pos':
                # positional value in [mm] or [deg]
                val = multi * self.axis_values[itr]
            else:
                # spindle/speed value in [deg] or [mm]?
                if obj.vector.currentText() == 'deg':
                    # spindle speed:
                    # multiplier * speed [360°/s] * poll_rate [ms]
                    val = multi * (6 * self.axis_values[itr]) * (poll_rate/1000)
                else:
                    # value from opc is a speed value driving a linear axis:
                    # multiplier is interpreted as gear ratio: e.g. 1 revolution = 10 mm --> multi = 10.0
                    # multi [mm] * speed [1/min] * poll_rate [ms]
                    val = multi * (self.axis_values[itr] / 60) * (poll_rate/1000)

            # update the LCS Placement: 
            # update positional axes by assigning them the received value
            # update speed axes by incrementing them with the calculated value 
            if obj.spd_pos.currentText() == 'pos':
                # positional axis:
                # Assign vector components with previous values except for 
                # vectors with a corresponding opc variable (marked by obj.vector.currentText() = 'x/y/z/°').
                # Factor in pos/neg sign where applicable.
                x = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'x' else prev['old_X']
                y = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'y' else prev['old_Y']
                z = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'z' else prev['old_Z']

                #new angle
                angle = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'deg' else prev['old_angle']

                # update the axis values in the freecad document
                App.getDocument(doc).getObjectsByLabel(fc_obj)[0].AttachmentOffset = App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(prev['rot_x'], prev['rot_y'], prev['rot_z']), angle))
            else:
                # speed axis:
                # Assign vector components with previous values except for 
                # vectors with a corresponding opc variable (marked by obj.vector.currentText() = 'x/y/z/°').
                # Increment those by the new value and factor in pos/neg sign where applicable.
                x = (prev['old_X'] + (val if obj.sign.currentText() == '+' else (-val))) if obj.vector.currentText() == 'x' else prev['old_X']
                y = (prev['old_Y'] + (val if obj.sign.currentText() == '+' else (-val))) if obj.vector.currentText() == 'y' else prev['old_Y']
                z = (prev['old_Z'] + (val if obj.sign.currentText() == '+' else (-val))) if obj.vector.currentText() == 'z' else prev['old_Z']

                # new angle
                angle = (prev['old_angle'] + (val if obj.sign.currentText() == '+' else (-val))) if obj.vector.currentText() == 'deg' else prev['old_angle']

                # update the axis values in the freecad document
                App.getDocument(doc).getObjectsByLabel(fc_obj)[0].AttachmentOffset = App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(prev['rot_x'], prev['rot_y'], prev['rot_z']), angle))

        except Exception as e:
            print("[Fcmcua] Error while setting values in the freecad document", e)

   
    def _updateActuator(self, obj, itr):
        # extract document name and LCS label
        doc = obj.docLEdit.text()
        fc_obj = obj.objLEdit.text()

        # get previous values
        prev = self._getFcValues(doc, fc_obj)
                
        try:    
            #new placement vector value:
            val = self.actu_values[itr]

            # Assign vector components with previous values except for 
            # vectors with a corresponding opc variable (marked by obj.vector.currentText() = 'x/y/z/°').
            x = val if obj.vectorCombo.currentText() == 'x' else prev['old_X']
            y = val if obj.vectorCombo.currentText() == 'y' else prev['old_Y']
            z = val if obj.vectorCombo.currentText() == 'z' else prev['old_Z']

            #update the actuator values in the freecad document
            App.getDocument(doc).getObjectsByLabel(fc_obj)[0].AttachmentOffset = App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(prev['rot_x'], prev['rot_y'], prev['rot_z']), prev['old_angle']))

        except Exception as e:
            print("[Fcmcua] Error while setting values in the freecad document", e)

    def _recompute(self):
        '''
        If the active document contains an Assembly4 model, only recompute the model
        else the whole document
        '''
        model = self.checkModel()

        # _checkModel returns the Asm4 model container
        # or None if there is no known container in the active document
        if model is not None:
            model.recompute(True)

    def checkModel(self):
        '''
        checks and returns whether there is an Asm4 Assembly Model in the active document
        '''

        #
        # This method is borrowed straight from Zolko's Asm4 workbench v0.12 (Asm4_libs.py).
        #

        retval = None
        if App.ActiveDocument:
            model = App.ActiveDocument.getObject('Model')
            # the current (as per v0.12) assembly container
            if model and model.TypeId=='App::Part' \
                    and model.Type == 'Assembly'   \
                    and model.getParentGeoFeatureGroup() is None:
                retval = model
            else:
                # former Assembly compatibility check:
                assy = App.ActiveDocument.getObject('Assembly')
                if assy and assy.TypeId=='App::Part'  \
                        and assy.Type == 'Assembly'   \
                        and assy.getParentGeoFeatureGroup() is None:
                    retval = assy
                else:
                    # last chance, very old Asm4 Model
                    if  model   and model.TypeId=='App::Part'  \
                                and model.getParentGeoFeatureGroup() is None:
                        retval = model
        return retval


