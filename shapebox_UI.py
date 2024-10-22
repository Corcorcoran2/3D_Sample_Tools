#UI for bringing in common custom nurbs shapes, like boxes, pyramids, sticks, etc. Saves time on having to NURBS curve
#edit, as well as maintains consistency between shapes in the rig.
import maya.cmds as cmds
import controls

class ShapeBoxUI():
    def __init__(self):
        self.create_UI()
    
    def delete_shapebox_UI(self):
        if cmds.window('main_window', query = True, exists = True):
            cmds.deleteUI('main_window')
            
    def create_script(self):
        current_selection = cmds.optionMenu('shape_combo_box', query = True, value = True)
        if current_selection == 'Switch':
            controls.switch_ctrl()
        if current_selection == 'Box':
            controls.box_ctrl()
        if current_selection == 'Diamond Stick':
            controls.diamond_stick_ctrl()
        if current_selection == 'World':
            controls.world_ctrl()
        if current_selection == 'Pyramid':
            controls.pyramid_ctrl()
    
    def create_UI(self):
        self.delete_shapebox_UI()
        cmds.window('main_window',  sizeable = False, title = 'Shape Box', width = 400, height = 100)
        cmds.formLayout('main_form_layout')
        cmds.button('create_button', command = lambda *args: self.create_script(), label = 'Create', width = 100)
        cmds.button('cancel_button', command = lambda *args: self.cancel_script(), label = 'Cancel', width = 100)
        
        combo_box = cmds.optionMenu('shape_combo_box', label="Choose Shape:")
        cmds.menuItem(label="Switch")
        cmds.menuItem(label="Box")
        cmds.menuItem(label="Diamond Stick")
        cmds.menuItem(label="World")
        cmds.menuItem(label="Pyramid")

        cmds.formLayout('main_form_layout', edit = True, attachForm = [('create_button', 'right', 110), ('create_button', 'bottom', 5)])
        cmds.formLayout('main_form_layout', edit = True, attachForm = [('cancel_button', 'right', 5), ('cancel_button', 'bottom', 5)])
        cmds.formLayout('main_form_layout', edit = True, attachForm = [('shape_combo_box', 'left', 5), ('shape_combo_box', 'top', 10)])
        
        cmds.showWindow()
        
ShapeBoxUI()      
