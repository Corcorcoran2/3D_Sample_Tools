import maya.cmds as cmds
import ComponentClass
import controls
import importlib
importlib.reload(controls)
importlib.reload(ComponentClass)

class BipedArm(ComponentClass.Component):
    def __init__(self, side, FK = False, IK = False, Stretch = False):                
        if not (FK or IK):
            cmds.error('Need one of either IK or FK')
        self.name = "arm"        
        self.position = side        
        super().__init__(self.name, self.position, state = 'biped')
                
        self.arm_joints = super().queryJoints(self.name, self.position)                   
        self.clavicle_group, self.clavicle_ctrl = self.build_clavicle()
        self.driver_chain = self.build_chain(self.arm_joints, self.name, self.position, 'biped_driver')  

        if FK:
            self.FK_chain = self.build_chain(self.driver_chain, self.name, self.position, 'biped_FK')
            self.build_FK()
        if IK:        
            self.IK_chain = self.build_chain(self.driver_chain, self.name, self.position, 'biped_IK')
            self.build_IK()  
         
        if FK and IK:
            self.build_switch()
            
    def constrain_driver(self, position):
        cmds.parentConstraint(f'arm_{side}_clavicle_biped_driver_joint', f'arm_{side}_clavicle_bind_joint')
        cmds.parentConstraint(f'arm_{side}_shoulder_biped_driver_joint', f'arm_{side}_shoulder_bind_joint')
        cmds.parentConstraint(f'arm_{side}_elbow_biped_driver_joint', f'arm_{side}_elbow_bind_joint')
        cmds.parentConstraint(f'arm_{side}_wrist_biped_driver_joint', f'arm_{side}_wrist_bind_joint')
    
    def build_chain(self, joints, name, position, type):
        
        dag_joints = [0] * 5
        joint_keywords = ['clavicle', 'shoulder', 'elbow', 'wrist', 'end']

        for joint in joints:
            for index, keyword in enumerate(joint_keywords):
                if keyword in joint:
                    dag_joints[index] = joint

        chain = cmds.duplicate(joints[0], renameChildren = True)

        filtered_chain = []
        for joint_node in chain:
            if cmds.objExists(joint_node):
                if cmds.objectType(joint_node) == 'joint' and 'arm' in joint_node:
                
                    filtered_chain.append(joint_node)
                else:
                    cmds.delete(joint_node, inputConnectionsAndNodes = False)

        if 'driver' in filtered_chain[0]:
            pass
        else:
            cmds.parent(filtered_chain[0], self.deform_node)
        print(filtered_chain)
        print(dag_joints)
        filtered_chain[0] = cmds.rename(filtered_chain[0], f'arm_{position}_clavicle_{type}_joint')
        filtered_chain[1] = cmds.rename(filtered_chain[1], f'arm_{position}_shoulder_{type}_joint')
        filtered_chain[2] = cmds.rename(filtered_chain[2], f'arm_{position}_elbow_{type}_joint')
        filtered_chain[3] = cmds.rename(filtered_chain[3], f'arm_{position}_wrist_{type}_joint')
        filtered_chain[4] = cmds.rename(filtered_chain[4], f'arm_{position}_end_{type}_joint')
        
        [cmds.parentConstraint(joint, dag_joints[index]) for index, joint in enumerate(filtered_chain)]        
        cmds.setAttr(f'{filtered_chain[0]}.visibility', 0)    
        return filtered_chain
        
    def build_clavicle(self):
        clavicle_ctrl = cmds.circle(name = f'arm_{self.side}_clavicle_biped_FK_ctrl', normal = [1,0,0], radius = 1)[0]
        controls.diamond_stick_ctrl()
        
        cmds.select('diamond_stick_ctrlShape', f'arm_{self.side}_clavicle_biped_FK_ctrl', r = True)
        cmds.parent(r = True, s = True)
        cmds.delete('diamond_stick_ctrl')
        cmds.delete(f'arm_{self.side}_clavicle_biped_FK_ctrlShape')
        cmds.rename('diamond_stick_ctrlShape', f'arm_{self.side}_clavicle_biped_FK_ctrlShape')
        
        clavicle_group = cmds.group(clavicle_ctrl, name = f'arm_{self.side}_clavicle_biped_FK_ctrl_buffer', world = True)
       
        cmds.makeIdentity(apply = False, t = 1, r = 1, s = 1)
        cmds.matchTransform(clavicle_group, self.arm_joints[0])
        if self.position == 'L':
            cmds.rotate(90, 0, 0, clavicle_ctrl)
        else:
            cmds.rotate(-90,0,0, clavicle_ctrl)
        cmds.scale(.2,.5,.2, clavicle_ctrl)
        cmds.delete(clavicle_ctrl, constructionHistory = True)
        cmds.makeIdentity(clavicle_ctrl, apply = True)
        cmds.setAttr(f'{clavicle_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{clavicle_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{clavicle_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{clavicle_ctrl}.v', keyable = False, channelBox = False)
        
        cmds.setAttr(f'arm_{self.side}_clavicle_biped_FK_ctrlShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_clavicle_biped_FK_ctrlShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_clavicle_biped_FK_ctrlShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_clavicle_biped_FK_ctrlShape.overrideColorRGB', 1, 0, 0)
        
        return clavicle_group, clavicle_ctrl
    
    def build_FK(self):
        cmds.parentConstraint(self.clavicle_ctrl, self.FK_chain[0], mo = True)
        cmds.delete(self.clavicle_ctrl, constructionHistory = True)
        cmds.setAttr(f'{self.clavicle_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{self.clavicle_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{self.clavicle_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{self.clavicle_ctrl}.v', keyable = False, channelBox = False)
        
        shoulder_ctrl = cmds.circle(name = f'arm_{self.side}_shoulder_biped_FK_ctrl', normal = [1,0,0])[0]
        shoulder_group = cmds.group(shoulder_ctrl, name = f'arm_{self.side}_shoulder_biped_FK_ctrl_buffer')
        cmds.matchTransform(shoulder_group, self.FK_chain[1])
        cmds.parentConstraint(shoulder_ctrl, self.FK_chain[1])
        cmds.delete(shoulder_ctrl, constructionHistory = True)
        cmds.setAttr(f'{shoulder_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{shoulder_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{shoulder_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{shoulder_ctrl}.v', keyable = False, channelBox = False)
        cmds.setAttr(f'arm_{self.side}_shoulder_biped_FK_ctrlShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_shoulder_biped_FK_ctrlShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_shoulder_biped_FK_ctrlShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_shoulder_biped_FK_ctrlShape.overrideColorRGB', 1, 0, 0)
        cmds.setAttr(f'arm_{self.side}_shoulder_biped_FK_ctrlShape.lineWidth', 3)
        
        elbow_ctrl = cmds.circle(name = f'arm_{self.side}_elbow_biped_FK_ctrl', normal = [1,0,0])[0]
        elbow_group = cmds.group(elbow_ctrl, name = f'arm_{self.side}_elbow_biped_FK_ctrl_buffer')
        cmds.matchTransform(elbow_group, self.FK_chain[2])
        cmds.parentConstraint(elbow_ctrl, self.FK_chain[2])
        cmds.delete(elbow_ctrl, constructionHistory = True)
        cmds.setAttr(f'{elbow_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{elbow_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{elbow_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{elbow_ctrl}.v', keyable = False, channelBox = False)
        cmds.setAttr(f'arm_{self.side}_elbow_biped_FK_ctrlShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_elbow_biped_FK_ctrlShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_elbow_biped_FK_ctrlShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_elbow_biped_FK_ctrlShape.overrideColorRGB', 1, 0, 0)
        cmds.setAttr(f'arm_{self.side}_elbow_biped_FK_ctrlShape.lineWidth', 3)
        
        wrist_ctrl = cmds.circle(name = f'arm_{self.side}_wrist_biped_FK_ctrl', normal = [1,0,0], radius = .5)[0]
        wrist_group = cmds.group(wrist_ctrl, name = f'arm_{self.side}_wrist_biped_FK_ctrl_buffer')
        cmds.matchTransform(wrist_group, self.FK_chain[3])
        cmds.parentConstraint(wrist_ctrl, self.FK_chain[3])
        cmds.delete(wrist_ctrl, constructionHistory = True)
        cmds.setAttr(f'{wrist_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{wrist_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{wrist_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{wrist_ctrl}.v', keyable = False, channelBox = False)
        cmds.setAttr(f'arm_{self.side}_wrist_biped_FK_ctrlShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_wrist_biped_FK_ctrlShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_wrist_biped_FK_ctrlShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_wrist_biped_FK_ctrlShape.overrideColorRGB', 1, 0, 0)
        cmds.setAttr(f'arm_{self.side}_wrist_biped_FK_ctrlShape.lineWidth', 3)
        
        cmds.parent(wrist_group, elbow_ctrl)
        cmds.parent(elbow_group, shoulder_ctrl)
        cmds.parent(shoulder_group, self.clavicle_ctrl)
        
        FK_group = cmds.group(self.clavicle_group, name = 'FK')
        cmds.parent(FK_group, self.control_node)
        
    def build_IK(self):
        cmds.parentConstraint(self.clavicle_ctrl, self.IK_chain[0], mo = True)
        cmds.delete(self.clavicle_ctrl, constructionHistory = True)
        cmds.setAttr(f'{self.clavicle_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{self.clavicle_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{self.clavicle_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{self.clavicle_ctrl}.v', keyable = False, channelBox = False)
        
        wrist_ctrl = cmds.circle(name = f'arm_{self.side}_wrist_biped_IK_ctrl', normal = [1,0,0])[0]
        wrist_group = cmds.group(wrist_ctrl, name = f'arm_{self.side}_wrist_biped_IK_ctrl_buffer')
        cmds.matchTransform(wrist_group, self.IK_chain[3])
        
        controls.box_ctrl()
        cmds.select('box_ctrlShape', f'arm_{self.side}_wrist_biped_IK_ctrl', r = True)
        cmds.parent(r = True, s = True)
        cmds.delete('box_ctrl')
        cmds.delete(f'arm_{self.side}_wrist_biped_IK_ctrlShape')
        cmds.rename('box_ctrlShape', f'arm_{self.side}_wrist_biped_IK_ctrlShape')

        ik_handle = cmds.ikHandle(name = f'arm_{self.side}_wrist_biped_IK_handle', startJoint = self.IK_chain[1], endEffector = self.IK_chain[3])[0]
        cmds.setAttr(f'{ik_handle}.visibility', 0)

        cmds.delete(wrist_ctrl, constructionHistory = True)
        cmds.setAttr(f'{wrist_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{wrist_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{wrist_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{wrist_ctrl}.v', keyable = False, channelBox = False)

        cmds.setAttr(f'arm_{self.side}_wrist_biped_IK_ctrlShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_wrist_biped_IK_ctrlShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_wrist_biped_IK_ctrlShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_wrist_biped_IK_ctrlShape.overrideColorRGB', 1, 0, 0)

        ik_handle_follow_constrain = cmds.group(ik_handle, name=f'arm_{self.side}_wrist_biped_IK_handle_point_constrain')
        cmds.pointConstraint(wrist_ctrl, ik_handle_follow_constrain, mo = True)

        IK_group = cmds.group(wrist_group, name = 'IK')
        cmds.parent(f'arm_{self.side}_wrist_biped_IK_handle_point_constrain', IK_group)

        shoulder_joint_position = cmds.xform(self.IK_chain[1], query = True, translation = True, worldSpace = True)
        elbow_joint_position = cmds.xform(self.IK_chain[2], query = True, translation = True, worldSpace = True)
        wrist_joint_position = cmds.xform(self.IK_chain[3], query = True, translation = True, worldSpace = True)

        curve = cmds.curve(degree = 1, point = [shoulder_joint_position, elbow_joint_position, wrist_joint_position, shoulder_joint_position], k = [0,1,2,3])
        cmds.select(f'{curve}.cv[1]')

        cmds.moveVertexAlongDirection(n = 1.5)

        pole_vector_position = cmds.pointPosition(world = True)
    
        pole_vector_ctrl = cmds.circle(name = f'arm_{self.side}_elbow_biped_IK_ctrl')[0]
        controls.box_ctrl()
        cmds.select('box_ctrlShape', f'arm_{self.side}_elbow_biped_IK_ctrl', r = True)
        cmds.parent(r = True, s = True)
        cmds.delete('box_ctrl')
        cmds.delete(f'arm_{self.side}_elbow_biped_IK_ctrlShape')
        cmds.rename('box_ctrlShape', f'arm_{self.side}_elbow_biped_IK_ctrlShape')
        pole_vector_group = cmds.group(name = f'arm_{self.side}_elbow_biped_IK_ctrl_buffer')
        cmds.setAttr(f'{pole_vector_group}.translate', pole_vector_position[0], pole_vector_position[1], pole_vector_position[2])
        cmds.poleVectorConstraint(pole_vector_ctrl, ik_handle)

        cmds.setAttr(f'{pole_vector_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{pole_vector_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{pole_vector_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{pole_vector_ctrl}.v', keyable = False, channelBox = False)
        cmds.setAttr(f'{pole_vector_ctrl}.rx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{pole_vector_ctrl}.ry', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{pole_vector_ctrl}.rz', lock = True, keyable = False, channelBox = False)
        cmds.delete(pole_vector_ctrl, constructionHistory = True)
        
        cmds.setAttr(f'arm_{self.side}_elbow_biped_IK_ctrlShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_elbow_biped_IK_ctrlShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_elbow_biped_IK_ctrlShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_elbow_biped_IK_ctrlShape.overrideColorRGB', 1, 0, 0)
        
        cmds.orientConstraint(wrist_ctrl, self.IK_chain[3], mo = True)
        cmds.parent(f'arm_{self.side}_elbow_biped_IK_ctrl_buffer', IK_group)
        cmds.parent(IK_group, self.control_node)
        
        cmds.delete(curve)        
        
    def build_switch(self):
        controls.switch_ctrl()
        switch_ctrl = cmds.rename('switch_ctrl', f'arm_{self.side}_biped_switch_ctrl')

        switch_point_constrain_group = cmds.group(switch_ctrl, name = f'arm_{self.side}_biped_switch_ctrl_point_constrain')
        switch_group = cmds.group(switch_point_constrain_group, name = f'arm_{self.side}_biped_switch_ctrl_buffer')
        cmds.matchTransform(switch_group, self.FK_chain[3], position = True)

        cmds.scale(.25,.25,.25, switch_ctrl)
        cmds.select(switch_ctrl)
        cmds.addAttr(longName = 'Switch', shortName = 'sw', attributeType = 'enum', enumName = 'IK:FK', keyable = True)
        if 'L' in self.side:
            cmds.move(7, 0, -1, switch_group, r = True)
        else:
            cmds.move(-1, 0, -1, switch_group, r = True)

        cmds.pointConstraint(f'arm_{self.side}_wrist_biped_FK_ctrl', f'arm_{self.side}_wrist_biped_IK_ctrl', switch_point_constrain_group, mo = True)

        cmds.delete(switch_ctrl, constructionHistory = True)
        cmds.setAttr(f'{switch_ctrl}.sx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.sy', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.sz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.rx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.ry', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.rz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.tx', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.ty', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.tz', lock = True, keyable = False, channelBox = False)
        cmds.setAttr(f'{switch_ctrl}.v', keyable = False, channelBox = False)
        
        FK_condition = cmds.createNode('condition', name = f'arm_{self.side}_FK_biped_switch_condition')
        cmds.setAttr(f'{FK_condition}.colorIfTrueR', 1)
        cmds.setAttr(f'{FK_condition}.colorIfFalseR', 0)
        cmds.setAttr(f'{FK_condition}.secondTerm', 1)
        IK_condition = cmds.createNode('condition', name = f'arm_{self.side}_IK_biped_switch_condition')
        cmds.setAttr(f'{IK_condition}.colorIfTrueR', 1)
        cmds.setAttr(f'{IK_condition}.colorIfFalseR', 0)
        cmds.setAttr(f'{IK_condition}.secondTerm', 0)
        
        F_FK = cmds.rename('F_FKShape', f'arm_{self.side}_biped_switch_F_FKShape')
        K_FK = cmds.rename('K_FKShape', f'arm_{self.side}_biped_switch_K_FKShape')
        I_IK = cmds.rename('I_IKShape', f'arm_{self.side}_biped_switch_I_IKShape')
        K_IK = cmds.rename('K_IKShape', f'arm_{self.side}_biped_switch_K_IKShape')
        
        cmds.connectAttr(f'{switch_ctrl}.Switch', f'{FK_condition}.firstTerm')
        cmds.connectAttr(f'{switch_ctrl}.Switch', f'{IK_condition}.firstTerm')

        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_shoulder_biped_driver_joint_parentConstraint1.arm_{self.side}_shoulder_biped_FK_jointW0')
        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_elbow_biped_driver_joint_parentConstraint1.arm_{self.side}_elbow_biped_FK_jointW0')
        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_wrist_biped_driver_joint_parentConstraint1.arm_{self.side}_wrist_biped_FK_jointW0')
        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_biped_switch_ctrl_point_constrain_pointConstraint1.arm_{self.side}_wrist_biped_FK_ctrlW0')
        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_shoulder_biped_FK_ctrlShape.visibility')
        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_elbow_biped_FK_ctrlShape.visibility')
        cmds.connectAttr(f'{FK_condition}.outColorR', f'arm_{self.side}_wrist_biped_FK_ctrl.visibility')
        
        cmds.connectAttr(f'{IK_condition}.outColorR', f'arm_{self.side}_shoulder_biped_driver_joint_parentConstraint1.arm_{self.side}_shoulder_biped_IK_jointW1')
        cmds.connectAttr(f'{IK_condition}.outColorR', f'arm_{self.side}_elbow_biped_driver_joint_parentConstraint1.arm_{self.side}_elbow_biped_IK_jointW1')
        cmds.connectAttr(f'{IK_condition}.outColorR', f'arm_{self.side}_wrist_biped_driver_joint_parentConstraint1.arm_{self.side}_wrist_biped_IK_jointW1')
        cmds.connectAttr(f'{IK_condition}.outColorR', f'arm_{self.side}_biped_switch_ctrl_point_constrain_pointConstraint1.arm_{self.side}_wrist_biped_IK_ctrlW1')
        cmds.connectAttr(f'{IK_condition}.outColorR', f'arm_{self.side}_wrist_biped_IK_ctrl.visibility')
        cmds.connectAttr(f'{IK_condition}.outColorR', f'arm_{self.side}_elbow_biped_IK_ctrl.visibility')
        
        cmds.connectAttr(f'arm_{self.side}_FK_biped_switch_condition.outColorR', f'arm_{self.side}_biped_switch_F_FKShape.visibility')
        cmds.connectAttr(f'arm_{self.side}_FK_biped_switch_condition.outColorR', f'arm_{self.side}_biped_switch_K_FKShape.visibility')
        cmds.connectAttr(f'arm_{self.side}_IK_biped_switch_condition.outColorR', f'arm_{self.side}_biped_switch_I_IKShape.visibility')
        cmds.connectAttr(f'arm_{self.side}_IK_biped_switch_condition.outColorR', f'arm_{self.side}_biped_switch_K_IKShape.visibility')
        
        cmds.setAttr(f'arm_{self.side}_biped_switch_F_FKShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_F_FKShape.overrideRGBColors', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_K_FKShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_K_FKShape.overrideRGBColors', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_I_IKShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_I_IKShape.overrideRGBColors', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_K_IKShape.overrideEnabled', 1)
        cmds.setAttr(f'arm_{self.side}_biped_switch_K_IKShape.overrideRGBColors', 1)
        if self.side == 'R':
            cmds.setAttr(f'arm_{self.side}_biped_switch_F_FKShape.overrideColorRGB', 0, 0, 1)
            cmds.setAttr(f'arm_{self.side}_biped_switch_K_FKShape.overrideColorRGB', 0, 0, 1)
            cmds.setAttr(f'arm_{self.side}_biped_switch_I_IKShape.overrideColorRGB', 0, 0, 1)
            cmds.setAttr(f'arm_{self.side}_biped_switch_K_IKShape.overrideColorRGB', 0, 0, 1)
        else:
            cmds.setAttr(f'arm_{self.side}_biped_switch_F_FKShape.overrideColorRGB', 1, 0, 0)
            cmds.setAttr(f'arm_{self.side}_biped_switch_K_FKShape.overrideColorRGB', 1, 0, 0)
            cmds.setAttr(f'arm_{self.side}_biped_switch_I_IKShape.overrideColorRGB', 1, 0, 0)
            cmds.setAttr(f'arm_{self.side}_biped_switch_K_IKShape.overrideColorRGB', 1, 0, 0)
        
        switch_node = cmds.group(switch_group, name = "Switch")
        
        cmds.parent(switch_node, self.control_node)