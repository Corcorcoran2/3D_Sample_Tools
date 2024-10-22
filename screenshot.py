#Simple tool for taking viewport screenshots. This will be called automatically when a screenshot is taken
#in my pose library tool to give a visual indicator of the current animation.

import maya.cmds as cmds

def take_picture():
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8) 
        p = cmds.getPanel( type='modelPanel' )[-1]
        temp_path = 'C:\maya_projects\\rig_factory_images\preview'
        asset_image = cmds.playblast(frame=[cmds.currentTime(q = True)], fmt = 'image', v = False, f = temp_path,wh=(600,600), orn = False, p = 100, fo = True)
take_picture()
