# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import mathutils

bl_info = {
    "name" : "Rigidbody Bone Setup Tool",             
    "author" : "dskjal",                  
    "version" : (1,0),                  
    "blender" : (2, 79, 0),              
    "location" : "View3D > Toolshelf > Rigidbody Bone",   
    "description" : "Setup bones to rigidbody.",   
    "warning" : "",
    "wiki_url" : "https://github.com/dskjal/Rigidbody-Bone",                    
    "tracker_url" : "",                 
    "category" : "Armature"                   
}

def create_box(head, tail, x, z, box_radius):
    verts = []
    verts.extend([ head + x*box_radius + z*box_radius,
                   head - x*box_radius + z*box_radius,
                   head - x*box_radius - z*box_radius,
                   head + x*box_radius - z*box_radius,
                   tail + x*box_radius + z*box_radius,
                   tail - x*box_radius + z*box_radius,
                   tail - x*box_radius - z*box_radius,
                   tail + x*box_radius - z*box_radius ])
    
    faces = []
    faces.extend([ [0, 1, 2, 3],
                   [0, 3, 7, 4],
                   [0, 4, 5, 1],
                   [1, 5, 6, 2],
                   [3, 2, 6, 7],
                   [4, 7, 6, 5] ])

    m = bpy.data.meshes.new('rigidbody_bone')
    m.from_pydata(verts, [], faces)
    m.update(calc_edges=True)
    
    o = bpy.data.objects.new('rigidbody_bone',object_data=m)
    
    bpy.context.scene.objects.link(o)
    o.layers = [i==(bpy.context.scene.rigid_body_bone_layer-1) for i in range(len(o.layers))]
    
    return o


def setup_box(amt, head_bone, hierarchy, bone_index, parent_box_object):
    box_radius = bpy.context.scene.rigid_body_bone_box_radius
    # create a box
    if bone_index == -1:
        # head box
        bone = hierarchy[bone_index + 1]
        tail = box_radius * bone.y_axis
        head = bone.head + tail
    elif bone_index == len(hierarchy):
        # tip box
        bone = hierarchy[bone_index - 1]
        head = bone.tail
        tail = box_radius * bone.y_axis
    else:
        bone = hierarchy[bone_index]
        head = bone.head
        tail = bone.tail - bone.head
    
    x = bone.x_axis
    z = bone.z_axis
    
    o = create_box(mathutils.Vector((0, 0, 0)), tail, x, z, box_radius)

    # set origin
    o.location = head
    
    # select the box
    bpy.context.scene.objects[amt.name].select = False
    bpy.context.scene.objects.active = o
    bpy.context.scene.objects[o.name].select = True
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # rigidbody
    bpy.ops.rigidbody.object_add()
    o.rigid_body.collision_shape = 'CONVEX_HULL'
    bpy.ops.rigidbody.constraint_add()
    o.rigid_body_constraint.object1 = o
    
    # rigidbody and ik settings
    if bone_index == -1:
        # parenting
        bpy.ops.object.select_all(action='DESELECT')
        bpy.context.scene.objects[o.name].select = True
        bpy.context.scene.objects[amt.name].select = True
        bpy.context.scene.objects.active = amt
        bpy.ops.object.mode_set(mode='POSE')
        bpy.ops.pose.select_all(action='DESELECT')
        head_bone.bone.select = True
        bpy.ops.object.parent_set(type='BONE')
        
        bpy.ops.object.mode_set(mode='OBJECT')
        bpy.context.scene.objects[amt.name].select = False
        bpy.context.scene.objects.active = o
        o.select = True
        
        # rigidbody settings
        o.rigid_body.kinematic = True
        o.rigid_body_constraint.type = 'FIXED'
    else:
        o.rigid_body_constraint.type = 'GENERIC_SPRING'
        o.rigid_body_constraint.object2 = parent_box_object
        o.rigid_body.linear_damping = bpy.context.scene.rigid_body_bone_linear_damping
        o.rigid_body.angular_damping = bpy.context.scene.rigid_body_bone_angular_damping
        o.rigid_body.mass = bpy.context.scene.rigid_body_bone_mass
        o.rigid_body_constraint.use_limit_lin_x = True
        o.rigid_body_constraint.use_limit_lin_y = True
        o.rigid_body_constraint.use_limit_lin_z = True
        o.rigid_body_constraint.use_limit_ang_x = True
        o.rigid_body_constraint.use_limit_ang_y = True
        o.rigid_body_constraint.use_limit_ang_z = True
        o.rigid_body_constraint.limit_lin_x_lower = 0
        o.rigid_body_constraint.limit_lin_x_upper = 0
        o.rigid_body_constraint.limit_lin_y_lower = 0
        o.rigid_body_constraint.limit_lin_y_upper = 0
        o.rigid_body_constraint.limit_lin_z_lower = 0
        o.rigid_body_constraint.limit_lin_z_upper = 0
        
        # add a bone to ik
        if bone_index > 0:
            ik_bone = hierarchy[bone_index-1]
            c = ik_bone.constraints.new('IK')
            c.name = 'RigidBody_Bone_IK'
            c.target = o
            c.chain_count = 1
    
    # deselect box
    bpy.context.scene.objects[o.name].select = False
    
    # select armature
    bpy.context.scene.objects.active = amt
    bpy.context.scene.objects[amt.name].select = True
    
    return o

# return a list of parent to child bone relashinship list
# This function does not support ramified bones.
# e.g. [ [parent, child1, child2], [parent2, child21, child22] ]
def analyze_bone_relationship(selected_bones, active_bone):
    bone_trees = []
    
    # find leaf bones
    parent_bones = [b.parent for b in selected_bones if b.parent != None]
    for b in selected_bones:
        if not b in parent_bones:
            bone_trees.append([b])
    
    # create tree
    for l in bone_trees:
        b = l[0]
        while b.parent != None and b.parent != active_bone:
            l.insert(0, b.parent)
            b = b.parent
        
        if b != l[0]:
            l.insert(0, b)
    
    return bone_trees


#-------------------------------------------- UI ------------------------------------------
class RigidbodyBoneSetupButton(bpy.types.Operator):
    bl_idname = "dskjal.rigidbodybonesetup"
    bl_label = "Setup Rigidbody"

    @classmethod
    def poll(self, context):
        o = context.active_object
        return o and o.type == 'ARMATURE' and o.mode == 'POSE'

    def execute(self, context):            
        selected_bones = bpy.context.selected_pose_bones
        active = bpy.context.active_pose_bone

        selected_bones.remove(active)
        bone_trees = analyze_bone_relationship(selected_bones, active)

        for tree in bone_trees:
            o = None
            for i in range(len(tree)+2):
                o = setup_box(bpy.context.active_object, active, tree, i-1, o)

        bpy.ops.object.mode_set(mode='POSE')

        # restore selected
        for b in selected_bones:
            bpy.context.active_object.pose.bones[b.name].bone.select = True
        
        active.bone.select = True

        return {'FINISHED'}

class RigidbodyBoneSetupRemove(bpy.types.Operator):
    bl_idname = "dskjal.rigidbodyboneremove"
    bl_label = "Remove Setted up Rigidbody"

    def execute(self, context):
        # remove IK
        for amt in [o for o in bpy.data.objects if o.type == 'ARMATURE']:
            for b in amt.pose.bones:
                for c in b.constraints:
                    if 'RigidBody_Bone_IK' in c.name:
                        b.constraints.remove(c)
                        break

        # remove objects
        for o in [o for o in bpy.data.objects if o.type == 'MESH' and 'rigidbody_bone' in o.name]:
            context.scene.objects.unlink(o)
            mesh = o.data
            bpy.data.objects.remove(o)
            bpy.data.meshes.remove(mesh)
        return {'FINISHED'}


class RigidbodyBoneSetupUI(bpy.types.Panel):
    bl_label = "Rigidbody Bone Setup Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "TOOLS"
    bl_category = "Rigidbody Bone"       

    def draw(self, context):
        scn = context.scene
        self.layout.prop(scn, "rigid_body_bone_layer")
        self.layout.prop(scn, "rigid_body_bone_box_radius")
        self.layout.separator()
        self.layout.prop(scn, "rigid_body_bone_mass")  
        self.layout.prop(scn, "rigid_body_bone_linear_damping")  
        self.layout.prop(scn, "rigid_body_bone_angular_damping")                
        self.layout.separator()
        self.layout.operator("dskjal.rigidbodybonesetup")
        self.layout.separator()
        self.layout.operator("dskjal.rigidbodyboneremove")


#---------------------------------------- Register ---------------------------------------------
classes = (
    RigidbodyBoneSetupButton,
    RigidbodyBoneSetupRemove,
    RigidbodyBoneSetupUI
)

def register():
    # variables
    bpy.types.Scene.rigid_body_bone_layer = bpy.props.IntProperty(name="Rigidbody Layer", default=20, min=1, max=20)
    bpy.types.Scene.rigid_body_bone_box_radius = bpy.props.FloatProperty(name="Rigidbody box size", default=0.05, min=0.001)
    bpy.types.Scene.rigid_body_bone_mass = bpy.props.FloatProperty(name="Box mass", default=1, min=0.001)
    bpy.types.Scene.rigid_body_bone_linear_damping = bpy.props.FloatProperty(name="Damping Translation", default=0.9, min=0.001, max=1.0)
    bpy.types.Scene.rigid_body_bone_angular_damping = bpy.props.FloatProperty(name="Damping Rotation", default=0.9, min=0.001, max=1.0)

    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Scene.rigid_body_bone_layer
    del bpy.types.Scene.rigid_body_bone_box_radius
    del bpy.types.Scene.rigid_body_bone_mass
    del bpy.types.Scene.rigid_body_bone_linear_damping
    del bpy.types.Scene.rigid_body_bone_angular_damping

if __name__ == "__main__":
    register()