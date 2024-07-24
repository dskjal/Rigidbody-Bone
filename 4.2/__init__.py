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
    "version" : (0, 92),
    "blender" : (2, 80, 0),
    "location" : "View3D > Toolshelf > Rigidbody Bone",
    "description" : "Setup bones to rigidbody.",
    "warning" : "",
    "wiki_url" : "https://github.com/dskjal/Rigidbody-Bone",
    "tracker_url" : "",
    "category" : "Armature"
}

collection_name = 'rigidbody_bone'
suffix = '_rigidbody_bone'

def create_box(head, tail, x, z, box_radius, name):
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

    m = bpy.data.meshes.new(f'{name}')
    m.from_pydata(verts, [], faces)
    m.update(calc_edges=True)
    
    o = bpy.data.objects.new(f'{name}',object_data=m)
    
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
        bone_name = f"head"
    elif bone_index == len(hierarchy):
        # tip box
        bone = hierarchy[bone_index - 1]
        head = to_world @ bone.tail
        tail = box_radius * to_world @ bone.y_axis
        bone_name = f"tail"
    else:
        bone = hierarchy[bone_index]
        head = to_world @ bone.head
        tail = to_world @ bone.tail - head
        bone_name = f"{bone.name}"
    
    x = to_world @ bone.x_axis
    z = to_world @ bone.z_axis
    x.normalize()
    z.normalize()
    
    # create a box
    o = create_box(Vector((0, 0, 0)), tail, x, z, box_radius, f"{bone_name}{suffix}")
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
        if bone_index == 0:
            # tail
            spring_name = f'{hierarchy[0].parent.name}-{bone_name}'
        elif bone_index == len(hierarchy):
            # tail
            spring_name = f'{hierarchy[bone_index-1].name}-tail'
        else:
            spring_name = f'{hierarchy[bone_index-1].name}-{bone_name}'

        # create a empty
        e = bpy.data.objects.new(spring_name, object_data=None)
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
            # c = ik_bone.constraints.new(type='COPY_LOCATION')
            # c.name = 'RigidBody_Bone_CL'
            # c.target = parent_box_object
            
            c = ik_bone.constraints.new(type='DAMPED_TRACK')
            c.name = 'RigidBody_Bone_DT'
            c.target = o

    # Place here for avoiding 'ERROR: no vertices to define Convex Hull collision shape with'
    o.rigid_body.collision_shape = 'CONVEX_HULL'

    # Collections
    o.rigid_body.collision_collections = scn.rigid_body_bone_collision_collections

    # deselect box
    bpy.context.scene.objects[o.name].select_set(False)
    
    # select armature
    #bpy.context.scene.objects.active = amt
    bpy.context.scene.objects[amt.name].select_set(True)
    
    return o

# return a list of parent to child bone relashinship list
# This function does not support ramified bones.
# return [ [parent, child1, child2], [parent2, child21, child22], ... ]
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
        # remove constraints
        for amt in [o for o in bpy.data.objects if o.type == 'ARMATURE']:
            for b in amt.pose.bones:
                dels = [c for c in b.constraints if 'RigidBody_Bone_' in c.name]
                for c in dels:
                    b.constraints.remove(c)

        # remove rigidbody
        active_object = bpy.context.active_object
        old_mode = active_object.mode
        bpy.ops.object.mode_set(mode='OBJECT')
        active_object.select_set(False)

        # deselect all 
        #for o in bpy.context.selected_objects:
        #    o.select_set(False)

        c = get_rigidbody_collection(collection_name)

        # EXCEPTION_ACCESS_VIOLATION fix
        # call constraint_remove() first
        for o in [o for o in c.objects if o.type == 'EMPTY']:
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.context.view_layer.update()
            print(f"\n{o.name}")
            if o.rigid_body_constraint:
                print("bpy.ops.rigidbody.constraint_remove()")
                bpy.ops.rigidbody.constraint_remove()
            o.select_set(False)

        for o in c.objects:
            bpy.context.view_layer.objects.active = o
            o.select_set(True)
            bpy.context.view_layer.update()
            print(f"\n{o.name}")
            if o.rigid_body:
                print("bpy.ops.rigidbody.object_remove()")
                bpy.ops.rigidbody.object_remove()
            o.select_set(False)

        bpy.context.view_layer.objects.active = active_object
        bpy.ops.object.mode_set(mode=old_mode)
        
        # remove objects
        for o in c.objects:
            c.objects.unlink(o)
            if o.data:
                # collision mesh
                mesh = o.data
                bpy.data.objects.remove(o)
                bpy.data.meshes.remove(mesh)
            else:
                # empty
                bpy.data.objects.remove(o)

        bpy.context.scene.collection.children.unlink(c)
        bpy.data.collections.remove(c)

        return {'FINISHED'}


class DSKJAL_PT_RigidbodyBoneSetupUI(bpy.types.Panel):
    bl_label = "Rigidbody Bone"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Rigidbody Bone"       

    def draw(self, context):
        scn = context.scene.dskjal_rb_props
        col = self.layout.column()
        col.operator("dskjal.rigidbodyboneremove")
        col.separator()

        # gen settings
        col.prop(scn, 'is_gen_settings_open', text='Generation Settings', icon='TRIA_DOWN' if scn.is_gen_settings_open else 'TRIA_RIGHT', emboss=False)
        if scn.is_gen_settings_open:
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

            # collision collections
            col.separator()
            col.label(text="Collision Collections:")
            col = self.layout.column(align=True)
            row = col.row(align=True)
            for i in range(20):
                row.prop(scn, "rigid_body_bone_collision_collections", index=i, text='', toggle=True)
                if i == 4:
                    row.separator()
                elif i == 9:
                    row = col.row(align=True)
                elif i == 14:
                    row.separator()

            col = self.layout.column(align=True)
            col.separator()
            col.operator("dskjal.rigidbodybonesetup")

        # bone rb settings
        col.separator()
        col.separator()
        col.prop(scn, 'is_bone_rb_settings_open', text='Bone Settings', icon='TRIA_DOWN' if scn.is_bone_rb_settings_open else 'TRIA_RIGHT', emboss=False)
        o = context.active_object
        if scn.is_bone_rb_settings_open and o and o.type == 'ARMATURE' and o.mode == 'POSE':
            if bpy.data.objects.find(f"{bpy.context.active_pose_bone.name}{suffix}") != -1:
                col.use_property_split = True
                bo = bpy.data.objects[f"{bpy.context.active_pose_bone.name}{suffix}"]
                col.label(text="Rigid Body:")
                col.prop(bo.rigid_body, "mass")
                col.prop(bo.rigid_body, "linear_damping", text='Damping Tanslation')
                col.prop(bo.rigid_body, "angular_damping", text='Damping Rotation')

                col.label(text="Collision Collections:")
                col = self.layout.column(align=True)
                row = col.row(align=True)
                for i in range(20):
                    row.prop(bo.rigid_body, "collision_collections", index=i, text='', toggle=True)
                    if i == 4:
                        row.separator()
                    elif i == 9:
                        row = col.row(align=True)
                    elif i == 14:
                        row.separator()
                col = self.layout.column(align=True)


                def print_spring_settings(bone, is_parent):
                    def get_spring_object(bone, is_parent):
                        if is_parent:
                            if bpy.data.objects.find(f"head-{bone.name}") != -1:
                                return bpy.data.objects[f"head-{bone.name}"]
                            if bpy.data.objects.find(f"{bone.parent.name}-{bone.name}") != -1:
                                return bpy.data.objects[f"{bone.parent.name}-{bone.name}"]
                        else:
                            if bpy.data.objects.find(f"{bone.name}-tail") != -1:
                                return bpy.data.objects[f"{bone.name}-tail"]
                            if bpy.data.objects.find(f"{bone.name}-{bone.parent.name}") != -1:
                                return bpy.data.objects[f"{bone.name}-{bone.parent.name}"]
                        return None
                    
                    spring = get_spring_object(bone, is_parent=is_parent)
                    if spring != None:
                        col.label(text="Limits Angular:")
                        col.use_property_split = True
                        for prop in ["use_limit_ang_x", "limit_ang_x_lower", "limit_ang_x_upper", "use_limit_ang_y", "limit_ang_y_lower", "limit_ang_y_upper", "use_limit_ang_z", "limit_ang_z_lower", "limit_ang_z_upper"]:
                            col.prop(spring.rigid_body_constraint, prop)

                        col.label(text="Spring Angular:")
                        col.use_property_split = True
                        for prop in ["use_spring_ang_x", "spring_stiffness_ang_x", "spring_damping_ang_x", "use_spring_ang_y", "spring_stiffness_ang_y", "spring_damping_ang_y", "use_spring_ang_z", "spring_stiffness_ang_z", "spring_damping_ang_z"]:
                            col.prop(spring.rigid_body_constraint, prop)

                col.label(text="Spring Parent:")
                print_spring_settings(bpy.context.active_pose_bone, is_parent=True)

                col.label(text="Spring Child:")
                print_spring_settings(bpy.context.active_pose_bone, is_parent=False)

                col.use_property_split = False


        # short cuts
        col.separator()
        col.separator()
        col.separator()
        col.label(text="Shortcuts:")
        col.label(text="Gravity:")
        row = col.row(align=True)
        row.prop(bpy.context.scene, "use_gravity", text="Gravity", toggle=True)
        row.prop(bpy.context.scene, "gravity", text="")

        col.separator()
        col.label(text="Jump to first frame:")
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

    # collision collections
    rigid_body_bone_collision_collections : bpy.props.BoolVectorProperty(size=20, name="Collision Collection", default=(True, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False, False,))

    # ui
    is_gen_settings_open : bpy.props.BoolProperty(name='is_gen_settings_open', default=True)
    is_bone_rb_settings_open : bpy.props.BoolProperty(name='is_bone_rb_settings_open', default=True)

classes = (
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
    #if hasattr(bpy.context.scene, 'dskjal_rb_props'): del bpy.context.scene.dskjal_rb_props
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()