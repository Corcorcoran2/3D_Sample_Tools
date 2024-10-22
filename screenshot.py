import maya.cmds as cmds

def take_picture():
        cmds.setAttr('defaultRenderGlobals.imageFormat', 8)


        
        p = cmds.getPanel( type='modelPanel' )[-1]
       # nc = cmds.modelEditor(p, q = True, nurbsCurves = True)
      #  print(nc)
      #  ns = cmds.modelEditor(p, q = True, nurbsSurfaces = True)
      #  print(ns)
      #  cmds.modelEditor(p, e = True, nurbsCurves = False, nurbsSurfaces = False)
        temp_path = 'C:\maya_projects\\rig_factory_images\preview'
        asset_image = cmds.playblast(frame=[cmds.currentTime(q = True)], fmt = 'image', v = False, f = temp_path,wh=(600,600), orn = False, p = 100, fo = True)
       
       
       
       # self.new_image = True
       # self.asset_image.setStyleSheet('background-image: url(' + asset_image + '); background-repeat: no-repeat; background-position: center center;')
       # pm.modelEditor(p, e = True, nurbsCurves = nc, nurbsSurfaces = ns)
take_picture()