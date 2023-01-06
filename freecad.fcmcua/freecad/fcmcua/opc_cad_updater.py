import FreeCAD as App
from datetime import datetime
import math

# round values received from FreeCAD to 3 decimals
_RND_PARAM = 3

class CadUpdater():
    """
    Update the values of the given FreeCAD documents
    """
    def __init__(self, axis_list, axis_values, actu_list, actu_values):
        self.axis_list = axis_list
        self.axis_values = axis_values
        self.actu_list = actu_list
        self.actu_values = actu_values


    def updateCAD(self):
        '''method to interact with FreeCAD model'''

        print("update CAD")
        # loop counter as an index for the values-list 
        itr = 0

        # iterate through all axis settings entries
        for obj in self.axis_list:
            self._updateAxis(obj, itr)
            itr += 1

        # reset loop counter
        itr = 0
        
        # iterate through all actuator settings entries
        for obj in self.actu_list:
            self._updateActuator(obj, itr)
            itr += 1

        #recompute the CAD model
        before = datetime.now()
        App.ActiveDocument.recompute()
        after = datetime.now()
        difference = after - before
        time_elapsed = difference.total_seconds()
        print('This recompute took:', time_elapsed)

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
            except:
                print("Error while getting values from the freecad document", doc, obj)

            return {'old_X':old_X, 'old_Y':old_Y, 'old_Z':old_Z, 'old_angle':old_angle,
                    'rot_x':rot_x, 'rot_y':rot_y, 'rot_z':rot_z}


    def _updateAxis(self, obj, itr):
        # get values already in FreeCAD
        doc = obj.docName.text()
        fc_obj = obj.obj_label.text()
        prev = self._getFcValues(doc, fc_obj)
                
        try:    
            #use previous values except for assigned opc variables (marked by n.vector.currentText() = 'x/y/z/°')
            #factor in pos/neg sign where applicable

            #new placement vector values:
            multi = self.axis_list[itr].multiSpin.value()
            val = multi * self.axis_values[itr]            
            x = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'x' else prev['old_X']
            y = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'y' else prev['old_Y']
            z = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'z' else prev['old_Z']

            #new angle
            angle = (val if obj.sign.currentText() == '+' else (-val)) if obj.vector.currentText() == 'deg' else prev['old_angle']

            #update the axis values in the freecad document
            App.getDocument(doc).getObjectsByLabel(fc_obj)[0].AttachmentOffset = App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(prev['rot_x'], prev['rot_y'], prev['rot_z']), angle))

        except:
            fc_values = [x, y, z, angle]
            print("Error while setting values in the freecad document", doc, fc_obj, fc_values)

   
    def _updateActuator(self, obj, itr):
        # get values already in FreeCAD
        doc = obj.docLEdit.text()
        fc_obj = obj.objLEdit.text()
        prev = self._getFcValues(doc, fc_obj)
                
        try:    
            #use previous values except for assigned opc variables (marked by n.vector.currentText() = 'x/y/z')
            #new placement vector values:
            val = self.actu_values[itr]
            x = val if obj.vectorCombo.currentText() == 'x' else prev['old_X']
            y = val if obj.vectorCombo.currentText() == 'y' else prev['old_Y']
            z = val if obj.vectorCombo.currentText() == 'z' else prev['old_Z']

            #update the actuator values in the freecad document
            App.getDocument(doc).getObjectsByLabel(fc_obj)[0].AttachmentOffset = App.Placement(App.Vector(x,y,z),App.Rotation(App.Vector(prev['rot_x'], prev['rot_y'], prev['rot_z']), prev['old_angle']))

        except:
            fc_values = [x, y, z, prev['old_angle']]
            print("Error while setting values in the freecad document", doc, fc_obj, fc_values)
