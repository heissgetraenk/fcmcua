import FreeCAD as App
import math

# round values received from FreeCAD to 3 decimals
_RND_PARAM = 3

class ActuatorLogic:
    def __init__(self, params, pollRate):
        # type 1=bidirectional, 2=unidirectional (open), 3=unidirectional (close)
        self.type = int(params.typeCombo.currentText()[:1])
        # positions
        self.openPos = params.openSpin.value()
        self.closePos = params.closeSpin.value()
        self.blockPos = params.blockSpin.value()
        # blocking option
        self.blockOptionSet = params.blockCheck.isChecked()
        # times
        self.openTime =params.openTSpin.value()
        self.closeTime =params.closeTSpin.value()
        # poll rate
        self.pollRate = pollRate
        # FreeCAD document
        self.doc = params.docLEdit.text()
        # FreeCAD object label
        self.fc_obj = params.objLEdit.text()
        # FreeCAD attachment offset vector component
        self.vector = params.vectorCombo.currentText()
        # length of stroke
        self.stroke_l = self.openPos - self.closePos
        # open step width
        self.open_stw = (self.stroke_l * self.pollRate)/self.openTime
        # close step width
        self.close_stw = (self.stroke_l * self.pollRate)/self.closeTime

    
    def get_current_pos(self, triggers):
        '''
        calculate new actuator position 
        '''
        open = triggers[0]
        close = triggers[1]
        block = triggers[2]

        # get the actual postion for this actuator from FreeCAD
        pos = self._get_fc_pos()[self.vector]        

        # get opening or closing state depending on type of actuator
        state = 'opening' if ((open and not close) or (self.type == 3 and not close)) else 'holding'
        state = 'closing' if ((close and not open) or (self.type == 2 and not open)) else state
        # check if a block comes into effect
        open_hysteresis = ((state == 'opening') and ((pos < (self.blockPos + self.open_stw)) and(pos > (self.blockPos - self.open_stw)))) 
        close_hysteresis =  ((state == 'closing') and ((pos < (self.blockPos + self.close_stw)) and (pos > (self.blockPos - self.close_stw))))
        in_hysteresis = open_hysteresis or close_hysteresis
        state = 'blocking' if (in_hysteresis and self.blockOptionSet and block) else state

        # return a new value
        return self._calculate_pos(state, pos)


    def _get_fc_pos(self):
        '''
        get the current attachment offset of the corresponding LCS from the FreeCAD document
        '''
        try:    
            # get actual placement from the document
            old_X = round(App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Base.x, _RND_PARAM)
            old_Y = round(App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Base.y, _RND_PARAM)
            old_Z = round(App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Base.z, _RND_PARAM)

            # get actual rotation from the document
            rad_angle = App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Rotation.Angle
            old_angle = round(rad_angle * 180 / math.pi, _RND_PARAM)
            rot_x = round(App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Rotation.Axis.x, _RND_PARAM)
            rot_y = round(App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Rotation.Axis.y, _RND_PARAM)
            rot_z = round(App.getDocument(self.doc).getObjectsByLabel(self.fc_obj)[0].AttachmentOffset.Rotation.Axis.z, _RND_PARAM)
        except:
            print("Error while getting values from the freecad document", self.doc, self.fc_obj)

        return {'x':old_X, 'y':old_Y, 'z':old_Z, 'angle':old_angle,
                'rot_x':rot_x, 'rot_y':rot_y, 'rot_z':rot_z}
    
    
    def _calculate_pos(self, state, pos): # state: opening, closing or holding
        # get attachment offset of FreeCad document
        # print("position before incr/decr/hold:", pos)
        # check if actuator is in open or closed position
        is_almost_open = pos > (self.openPos - self.open_stw)
        is_fully_open = pos > self.openPos
        is_almost_closed = pos < (self.closePos + self.close_stw)
        is_fully_closed = pos < self.closePos
        
        if (state == 'blocking'):
            # if pos is less then one step width 
            return self.blockPos
        elif (state == 'opening' and not is_fully_open):
            # increment by step width if pos is not exactly openPos
            # if pos is less than one step width from openPos return openPos
            return self.openPos if is_almost_open else (pos + self.open_stw) 
        elif (state == 'closing' and not is_fully_closed):
            # decrement by step width if pos is not exactly closePos
            # if pos is less than one step width from closePos return closePos
            return self.closePos if is_almost_closed else (pos - self.close_stw)
        else:
            # hold position
            return pos
        

