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
from mathutils import Vector, Matrix
from math import radians
from bpy.props import (
    FloatProperty,
    EnumProperty,
    BoolProperty,
    IntProperty,
    StringProperty,
    FloatVectorProperty,
    CollectionProperty,
)

bl_info = {
    "name" : "Rigidbody Bone Setup Tool",
    "author" : "dskjal",
    "version" : (0, 91),
    "blender" : (2, 80, 0),
    "location" : "View3D > Toolshelf > Rigidbody Bone",
    "description" : "Setup bones to rigidbody.",
    "warning" : "",
    "wiki_url" : "https://github.com/dskjal/Rigidbody-Bone",
    "tracker_url" : "",
    "category" : "Armature"
}

collection_name = 'rigidbody_bone'

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
    
    return o


def setup_box(amt, head_bone, hierarchy, bone_index, parent_box_object, collection):
    scn = bpy.context.scene.dskjal_rb_props
    box_radius = scn.rigid_body_bone_box_radius
    to_world = amt.matrix_world

    # create a box
    if bone_index == -1:
        # head box
        bone = hierarchy[bone_index + 1]
        tail = box_radius * to_world @ bone.y_axis
        head = to_world @ bone.head
    elif bone_index == len(hierarchy):
        # tip box
        bone = hierarchy[bone_index - 1]
        head = to_world @ bone.tail
        tail = box_radius * to_world @ bone.y_axis
    else:
        bone = hierarchy[bone_index]
        head = to_world @ bone.head
        tail = to_world @ bone.tail - head
    
    x = to_world @ bone.x_axis
    z = to_world @ bone.z_axis
    x.normalize()
    z.normalize()
    
    # create a box
    o = create_box(Vector((0, 0, 0)), tail, x, z, box_radius)
    collection.objects.link(o)
    o.location = head

    # select the box
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.data.objects[o.name].select_set(True)
    bpy.data.objects[amt.name].select_set(False)
    bpy.context.view_layer.objects.active = bpy.data.objects[o.name]

    # add rigidbody to box
    bpy.ops.rigidbody.object_add()

    if bone_index != -1:
        # create a empty
        e = bpy.data.objects.new("", object_data=None)
        collection.objects.link(e)
        e.location = head
        e.empty_display_size = 0.1

        # select the empty
        bpy.data.objects[e.name].select_set(True)
        bpy.data.objects[o.name].select_set(False)
        bpy.context.view_layer.objects.active = bpy.data.objects[e.name]

        # add rigidbody constraints to empty
        bpy.ops.rigidbody.constraint_add()
    
    # rigidbody and ik settings
    if bone_index == -1:
        # parenting
        world_tail = to_world @ head_bone.tail
        mat = head_bone.matrix.copy()
        o.location = (o.location - world_tail) @ mat
        o.parent = amt
        o.parent_type = 'BONE'
        o.parent_bone = head_bone.name
        
        # rigidbody settings
        o.rigid_body.kinematic = True
        o.rigid_body.type = 'PASSIVE'
    else:
        o.rigid_body.linear_damping = scn.rigid_body_bone_linear_damping
        o.rigid_body.angular_damping = scn.rigid_body_bone_angular_damping
        o.rigid_body.mass = scn.rigid_body_bone_mass
        e.rigid_body_constraint.type = 'GENERIC_SPRING'
        e.rigid_body_constraint.object1 = parent_box_object
        e.rigid_body_constraint.object2 = o
        e.rigid_body_constraint.use_limit_lin_x = True
        e.rigid_body_constraint.use_limit_lin_y = True
        e.rigid_body_constraint.use_limit_lin_z = True
        e.rigid_body_constraint.use_limit_ang_x = True
        e.rigid_body_constraint.use_limit_ang_y = True
        e.rigid_body_constraint.use_limit_ang_z = True
        e.rigid_body_constraint.limit_lin_x_lower = 0
        e.rigid_body_constraint.limit_lin_x_upper = 0
        e.rigid_body_constraint.limit_lin_y_lower = 0
        e.rigid_body_constraint.limit_lin_y_upper = 0
        e.rigid_body_constraint.limit_lin_z_lower = 0
        e.rigid_body_constraint.limit_lin_z_upper = 0
        e.rigid_body_constraint.spring_type = 'SPRING1' # Blender 2.7
        
        #spring settings
        e.rigid_body_constraint.use_spring_ang_x = scn.rigid_body_bone_use_x_angle
        e.rigid_body_constraint.use_spring_ang_y = scn.rigid_body_bone_use_y_angle
        e.rigid_body_constraint.use_spring_ang_z = scn.rigid_body_bone_use_z_angle
        e.rigid_body_constraint.spring_stiffness_ang_x = scn.rigid_body_bone_x_stiffness
        e.rigid_body_constraint.spring_stiffness_ang_y = scn.rigid_body_bone_y_stiffness
        e.rigid_body_constraint.spring_stiffness_ang_z = scn.rigid_body_bone_z_stiffness
        e.rigid_body_constraint.spring_damping_ang_x = scn.rigid_body_bone_x_damping
        e.rigid_body_constraint.spring_damping_ang_y = scn.rigid_body_bone_y_damping
        e.rigid_body_constraint.spring_damping_ang_z = scn.rigid_body_bone_z_damping

        # deselect the empty
        bpy.context.scene.objects[e.name].select_set(False)

        # add copylocation and track to to a bone
        if bone_index > 0:
            ik_bone = hierarchy[bone_index-1]
            c = ik_bone.constraints.new(type='COPY_LOCATION')
            c.name = 'RigidBody_Bone_CL'
            c.target = parent_box_object
            
            c = ik_bone.constraints.new(type='DAMPED_TRACK')
            c.name = 'RigidBody_Bone_DT'
            c.target = o

    # Place here for avoiding 'ERROR: no vertices to define Convex Hull collision shape with'
    o.rigid_body.collision_shape = 'CONVEX_HULL'

    # deselect box
    bpy.context.scene.objects[o.name].select_set(False)
    
    # select armature
    #bpy.context.scene.objects.active = amt
    bpy.context.scene.objects[amt.name].select_set(True)
    
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

def get_rigidbody_collection(collection_name):
    if bpy.context.scene.collection.children.find(collection_name) != -1:
        return bpy.data.collections[collection_name]

    if bpy.data.collections.find(collection_name) != -1:
        collection = bpy.data.collections[collection_name]
    else:
        collection = bpy.data.collections.new(collection_name)
    bpy.context.scene.collection.children.link(collection)
    return collection

#-------------------------------------------- UI ------------------------------------------        
class DSKJAL_OT_free_rigidbody_cache(bpy.types.Operator):
    bl_idname = "dskjal.freerigidbodycache"
    bl_label = "Free Rigidbody Cache"

    def execute(self, context):
        if bpy.context.scene.rigidbody_world == None:
            return {'FINISHED'}

        o = bpy.context.active_object
        old_mode = o.mode
        bpy.ops.object.mode_set(mode='OBJECT')

        rw = bpy.context.scene.rigidbody_world
        col = rw.collection
        const = rw.constraints

        bpy.ops.rigidbody.world_remove()
        bpy.ops.rigidbody.world_add()

        rw = bpy.context.scene.rigidbody_world
        rw.collection = col
        rw.constraints = const
        
        bpy.ops.object.mode_set(mode=old_mode)

        return {'FINISHED'}

class DSKJAL_OT_RigidbodyBoneSetupButton(bpy.types.Operator):
    bl_idname = "dskjal.rigidbodybonesetup"
    bl_label = "Setup Rigidbody"

    @classmethod
    def poll(self, context):
        o = context.active_object
        return o and o.type == 'ARMATURE' and o.mode == 'POSE'

    def execute(self, context):
        amt = bpy.context.active_object     
        selected_bones = bpy.context.selected_pose_bones
        active = bpy.context.active_pose_bone

        selected_bones.remove(active)
        bone_trees = analyze_bone_relationship(selected_bones, active)

        collection = get_rigidbody_collection(collection_name)
        for tree in bone_trees:
            o = None
            for i in range(len(tree)+2):
                o = setup_box(amt, active, tree, i-1, o, collection)

        bpy.context.view_layer.objects.active = amt
        bpy.ops.object.mode_set(mode='POSE')

        # restore selected
        for b in selected_bones:
            bpy.context.active_object.pose.bones[b.name].bone.select = True
        
        active.bone.select = True

        return {'FINISHED'}

class DSKJAL_OT_RigidbodyBoneSetupRemove(bpy.types.Operator):
    bl_idname = "dskjal.rigidbodyboneremove"
    bl_label = "Remove Rigidbody Bone"

    def execute(self, context):
        # remove IK
        for amt in [o for o in bpy.data.objects if o.type == 'ARMATURE']:
            for b in amt.pose.bones:
                dels = [c for c in b.constraints if 'RigidBody_Bone_' in c.name]
                for c in dels:
                    b.constraints.remove(c)

        # remove objects
        c = get_rigidbody_collection(collection_name)
        for o in c.objects:
            c.objects.unlink(o)
            if o.data == None:
                # empty
                bpy.data.objects.remove(o)
            else:
                # collision mesh
                mesh = o.data
                bpy.data.objects.remove(o)
                bpy.data.meshes.remove(mesh)

        bpy.context.scene.collection.children.unlink(c)
        bpy.data.collections.remove(c)

        # remove rigidbody world
        if bpy.context.scene.rigidbody_world != None:
            old_mode = bpy.context.active_object.mode
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.rigidbody.world_remove()
            bpy.ops.object.mode_set(mode=old_mode)
        
        return {'FINISHED'}


class DSKJAL_PT_RigidbodyBoneSetupUI(bpy.types.Panel):
    bl_label = "Rigidbody Bone Setup Tool"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rigidbody Bone"       

    def draw(self, context):
        scn = context.scene.dskjal_rb_props
        col = self.layout.column()
        col.operator("dskjal.rigidbodyboneremove")
        col.separator()
        col.label(text="Ribid Body Bone Settings:")
        col.prop(scn, "rigid_body_bone_box_radius")
        col.separator()
        col.label(text="Rigid Body Dynamics:")
        col.prop(scn, "rigid_body_bone_mass")  
        col.prop(scn, "rigid_body_bone_linear_damping")  
        col.prop(scn, "rigid_body_bone_angular_damping") 

        # spring settings
        col.separator()
        col.label(text="Springs:")
        row = col.row(align=True)
        row.prop(scn, "rigid_body_bone_use_x_angle", toggle=True)
        row.prop(scn, "rigid_body_bone_x_stiffness")
        row.prop(scn, "rigid_body_bone_x_damping")
        row = col.row(align=True)
        row.prop(scn, "rigid_body_bone_use_y_angle", toggle=True)
        row.prop(scn, "rigid_body_bone_y_stiffness")
        row.prop(scn, "rigid_body_bone_y_damping")
        row = col.row(align=True)
        row.prop(scn, "rigid_body_bone_use_z_angle", toggle=True)
        row.prop(scn, "rigid_body_bone_z_stiffness")
        row.prop(scn, "rigid_body_bone_z_damping")


        col.separator()
        col.operator("dskjal.rigidbodybonesetup")
        col.separator()


        col.separator()
        col.separator()
        col.label(text="Shortcuts:")
        col.operator("dskjal.freerigidbodycache")
        col.operator("screen.frame_jump", text="", icon='REW').end = False
        col.label(text="Rigid Body Cache")
        row = col.row(align=True)
        scn = context.scene
        if hasattr(scn, "rigidbody_world") and hasattr(scn.rigidbody_world, "point_cache"):
            row.prop(scn.rigidbody_world.point_cache, "frame_start")
            row.prop(scn.rigidbody_world.point_cache, "frame_end")



#---------------------------------------- Register ---------------------------------------------
class DSKJAL_RB_Props(bpy.types.PropertyGroup):
    # variables
    rigid_body_bone_box_radius : bpy.props.FloatProperty(name="Rigidbody box size", default=0.01, min=0.001)
    rigid_body_bone_mass : bpy.props.FloatProperty(name="Box mass", default=1, min=0.001)
    rigid_body_bone_linear_damping : bpy.props.FloatProperty(name="Damping Translation", default=0.9, min=0.001, max=1.0)
    rigid_body_bone_angular_damping : bpy.props.FloatProperty(name="Damping Rotation", default=0.9, min=0.001, max=1.0)

    # spring variables
    rigid_body_bone_use_x_angle : bpy.props.BoolProperty(name="X Angle", default=False)
    rigid_body_bone_use_y_angle : bpy.props.BoolProperty(name="Y Angle", default=False)
    rigid_body_bone_use_z_angle : bpy.props.BoolProperty(name="Z Angle", default=False)
    rigid_body_bone_x_stiffness : bpy.props.FloatProperty(name="Stiffness", default=10.0, min=0.001)
    rigid_body_bone_y_stiffness : bpy.props.FloatProperty(name="Stiffness", default=10.0, min=0.001)
    rigid_body_bone_z_stiffness : bpy.props.FloatProperty(name="Stiffness", default=10.0, min=0.001)
    rigid_body_bone_x_damping : bpy.props.FloatProperty(name="Damping", default=0.9, min=0.001, max=1.0)
    rigid_body_bone_y_damping : bpy.props.FloatProperty(name="Damping", default=0.9, min=0.001, max=1.0)
    rigid_body_bone_z_damping : bpy.props.FloatProperty(name="Damping", default=0.9, min=0.001, max=1.0)

classes = (
    DSKJAL_OT_free_rigidbody_cache,
    DSKJAL_OT_RigidbodyBoneSetupButton,
    DSKJAL_OT_RigidbodyBoneSetupRemove,
    DSKJAL_PT_RigidbodyBoneSetupUI,
    DSKJAL_RB_Props
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Scene.dskjal_rb_props = bpy.props.PointerProperty(type=DSKJAL_RB_Props)

def unregister():
    #if bpy.context.scene.get('dskjal_rb_props'): del bpy.context.scene.dskjal_rb_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()