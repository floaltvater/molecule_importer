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


#  Author: Florian Altvater (florian.altvater@gmail.com
#  The present script was forked from Atomic Blender:
#
#  Authors           : Clemens Barth (Blendphys@root-1.de), ...
#
#  Homepage(Wiki)    : http://development.root-1.de/Atomic_Blender.php
#
#  Start of project              : 2011-12-01 by Clemens Barth
#  First publication in Blender  : 2011-12-18
#  Last modified                 : 2012-11-10
#
#  Acknowledgements 
#  ================
#
#  Blender: ideasman, meta_androcto, truman, kilon, CoDEmanX, dairin0d, PKHG, 
#           Valter, ...
#  Other: Frank Palmino
#

bl_info = {
    "name": "Import Molecules",
    "description": "Import of .xyz and .pdb files",
    "author": "Florian Altvater",
    "version": (0,1),
    "blender": (2,6),
    "location": "File -> Import -> XYZ/PDB (.xyz, .pdb)",
    "warning": "",
    "wiki_url": "",
    "tracker_url": "",
    "category": "Import-Export"
}


if "bpy" in locals():
    import imp
    imp.reload(import_molecule)
    imp.reload(export_molecule)
    print("Reloaded multifiles")
else:
    from . import import_molecule
    from . import export_molecule
    print("Imported multifiles")

import bpy
from bpy.types import Operator
from bpy_extras.io_utils import ImportHelper, ExportHelper
from bpy.props import (StringProperty,
                       BoolProperty,
                       EnumProperty,
                       IntProperty,
                       FloatProperty,
                       FloatVectorProperty,
                       PointerProperty)




# -----------------------------------------------------------------------------
#                                                                           GUI


class Style_radii(bpy.types.PropertyGroup):
    balls = FloatProperty(default=1.0)
    balls_and_sticks = FloatProperty(default=0.35)

def callback_style(self, context):
    # save last setting
    if self.last_style == 'BALL':
        self.style_radii.balls = self.scale_ballradius
    elif self.last_style == 'BAS':
        self.style_radii.balls_and_sticks = self.scale_ballradius
    
    # update current setting
    if self.style == 'BALL':
        self.scale_ballradius = self.style_radii.balls
    elif self.style == 'BAS':
        self.scale_ballradius = self.style_radii.balls_and_sticks
    
    self.last_style = self.style
    
# This is the class for the file dialog.
class ImportXYZ(Operator, ImportHelper):
    bl_idname = "molimport.xyz"
    bl_label  = "Import XYZ/PDB (*.xyz,*.pdb)"
    bl_options = {'PRESET', 'UNDO'}
    
    filename_ext = "*.pdb;*.xyz"
    filter_glob  = StringProperty(default=filename_ext, options={'HIDDEN'},)
    
    use_camera = BoolProperty(
        name="Camera", default=False,
        description="Do you need a camera?")
    use_lamp = BoolProperty(
        name="Lamp", default=False,
        description = "Do you need a lamp?")
    style = EnumProperty(
        name="Drawing style",
        description="Choose style to draw molecule",
        items=(('BALLS', "Balls", "Balls"),
               ('BAS', "Balls and Sticks" , "Balls and Sticks"),
               ('STICKS', "Sticks" , "Stick")),
               default='BAS',
               update=callback_style)
    style_radii = PointerProperty(type=Style_radii)
    last_style = StringProperty(default='BAS')
    ball = EnumProperty(
        name="Type of ball",
        description="Choose ball",
        items=(('NURBS', "NURBS", "NURBS balls"),
               ('MESH', "Mesh" , "Mesh balls"),
               ('META', "Meta" , "Metaballs")),
               default='NURBS',) 
    mesh_azimuth = IntProperty(
        name = "Azimuth", default=32, min=1,
        description = "Number of sectors (azimuth)")
    mesh_zenith = IntProperty(
        name = "Zenith", default=32, min=1,
        description = "Number of sectors (zenith)")
    scale_ballradius = FloatProperty(
        name = "Balls", default=0.35, min=0.0001,
        description = "Scale factor for all atom radii")
    scale_distances = FloatProperty (
        name = "Distances", default=1.0, min=0.0001,
        description = "Scale factor for all distances")
    radiustype = EnumProperty(
        name="Type of radius",
        description="Choose type of atom radius",
        # keep numeric identifiers for easier list access
        items=(('0', "Pre-defined", "Use pre-defined radius"),
               ('1', "Atomic", "Use atomic radius"),
               ('2', "van der Waals", "Use van der Waals radius"),
               ('3', "constant", "Use same radius for all elements")),
               default='0',)
    stick = EnumProperty(
        name="Type of stick",
        description="Choose ball",
        items=(('NURBS', "NURBS", "NURBS balls"),
               ('MESH', "Mesh" , "Mesh balls"),
               #('2', "Meta" , "Metaballs")
               ),
               default='NURBS',) 
    bond_radius = FloatProperty(
        name = "Bond radius", default=0.15, min=0.0001,
        description = "Scale factor for bond radii")
    bond_sectors = IntProperty(
        name = "Bond sectors", default=8, min=3,
        description = "Number of sectors for bond meshes")
    bond_guess = BoolProperty(
        name = "Guess bonds", default=True,
        description = "Guess bonds that are not in the file.")
    bond_material = EnumProperty(
        name="Bond material",
        description="Choose bond material",
        items=(('ATOMS', "Atoms", "Same as atoms"),
               ('GENERIC', "Generic" , "Single bond color")),
               default='ATOMS',)
    bond_color = FloatVectorProperty(
        name='Bond color', default=(0.8, 0.8, 0.8), subtype='COLOR')
    use_center = BoolProperty(
        name = "Object to origin (first frame)", default=False,
        description = "Put the object into the global origin, the first frame only")
    use_center_all = BoolProperty(
        name = "Object to origin (all frames)", default=False,
        description = "Put the object into the global origin, all frames") 
    datafile = StringProperty(
        name = "", description="Path to your custom data file",
        maxlen = 256, default = "", subtype='FILE_PATH')    
    use_all_frames = BoolProperty(
        name = "Load all frames", default=False,
        description = "Do you want to load all frames?")
    use_select_frames = BoolProperty(
        name = "Load select frames", default=False,
        description = "Load specified frames only.")
    select_frames = StringProperty(
        name = "", description="Specify which frames you want to use (e.g \"1, 3-5, 6+7, 3-5\"). If empty, first frame is used. Frames will be processed in the order specified.",
        maxlen = 256, default = "")
    skip_frames = IntProperty(
        name="", default=0, min=0,
        description="Only use every xth frame.")
    images_per_key = IntProperty(
        name="", default=1, min=1,
        description="Choose the number of images between 2 keys.")
    interpolation = EnumProperty(
        name="Interpolation Mode",
        description="Choose interpolation between keyframes",
        items=(('BEZIER', "Bezier" , "Smooth interpolation between keyframes"),
               ('LINEAR', "Linear", "Linear interpolation between keyframes"),
               ('CONSTANT', "Constant", "Step-function like interpolation")),
               default='BEZIER',)

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        col = row.column()
        col.prop(self, "style")
        
        box = layout.box()
        row = box.row()
        row.label(text="Atoms")
        row = box.row()
        col = row.column()
        col.prop(self, "ball")
        row = box.row()
        row.active = (self.ball == "MESH")
        col = row.column(align=True)        
        col.prop(self, "mesh_azimuth")
        col.prop(self, "mesh_zenith")
        row = box.row()
        row.prop(self, "radiustype")
        row = box.row()
        col = row.column()
        col.label(text="Scaling factors")
        col = row.column(align=True)
        col.prop(self, "scale_ballradius")
        col.prop(self, "scale_distances")
        
        box = layout.box()
        box.active = (self.style != "BALLS") # no bonds in balls style
        
        row = box.row()
        row.label(text="Bonds")
        row = box.row()
        #row.active = (self.style != "0") # no bonds in balls style
        col = row.column()
        col.prop(self, "stick")
        row = box.row()
        #row.active = (self.style != "0") # no bonds in balls style
        col = row.column()
        col.prop(self, "bond_radius")
        row = box.row()
        row.active = (self.stick == 'MESH') # bond sectors only for mesh
        col = row.column()
        col.prop(self, "bond_sectors")
        row = box.row()
        col = row.column()
        col.prop(self, "bond_guess")
        row = box.row()
        col = row.column()
        col.prop(self, "bond_material")
        row = box.row()
        row.active = (self.bond_material == 'GENERIC')
        col = row.column()
        col.prop(self, "bond_color")
        
        
        box = layout.box()
        row = box.row()
        row.label(text="Scene settings")
        
        row = box.row()
        row.prop(self, "use_camera")
        row.prop(self, "use_lamp")
        
        row = box.row()
        row.prop(self, "use_center")
        row = box.row()
        row.active = (self.use_all_frames or self.use_select_frames)
        row.prop(self, "use_center_all")
        
        box = layout.box()
        row = box.row()
        row.label(text="Animation/Frames")
        row = box.row()
        row.prop(self, "use_all_frames")
        row = box.row()
        row.active = self.use_all_frames
        col = row.column()
        col.label(text="Skip frames")
        col = row.column()
        col.prop(self, "skip_frames")
        row = box.row()
        row.prop(self, "use_select_frames")
        row = box.row()
        row.active = self.use_select_frames
        row.prop(self, "select_frames")
        row = box.row()
        row.active = (self.use_all_frames or self.use_select_frames)
        col = row.column()
        col.label(text="Frames/key")
        col = row.column()
        col.prop(self, "images_per_key")
        row = box.row()
        row.active = (self.use_all_frames or self.use_select_frames)
        row.prop(self, "interpolation")
        
    def execute(self, context):

        import_molecule.ALL_FRAMES[:] = []
        import_molecule.ELEMENTS[:] = []
        import_molecule.STRUCTURE[:] = []

        # This is to determine the path.
        filepath = bpy.path.abspath(self.filepath)
        
        # check if select_frames is ok, otherwise stop right here
        error_msg = ''
        frame_list = []
        if self.use_select_frames:
            try:
                for item in self.select_frames.split(','):
                    if '-' in item:
                        start, end = map(int, item.split('-'))
                        frame_list.extend(range(start, end+1))
                    elif '+' in item:
                        frame_list.extend(map(int, item.split('+'))
                    else:
                        frame_list.append(int(item))
            except (ValueError, TypeError):
                error_msg = 'Format error in the frame list. Using first frame only.'
                frame_list.append(1)
            if not frame_list:
                error_msg = 'Frame list was empty. Using first frame only.'
                frame_list.append(1)
        if error_msg: print(error_msg)
        
        # Execute main routine
        import_molecule.import_molecule(
                      self.style,
                      self.ball,
                      self.mesh_azimuth,
                      self.mesh_zenith,
                      self.scale_ballradius,
                      self.radiustype,
                      self.scale_distances,
                      self.stick,
                      self.bond_radius,
                      self.bond_sectors,
                      self.bond_guess,
                      self.bond_material,
                      self.bond_color,
                      self.use_center,
                      self.use_center_all,
                      self.use_camera,
                      self.use_lamp,
                      filepath)
        
        if use_all_frames:
            frame_list.extend(range(1, len(import_molecule.ALL_FRAMES)+1))
        # Load frames                  
        if len(import_molecule.ALL_FRAMES) > 1 and frame_list and frame_list != [1]:
            
            import_molecule.build_frames(self.images_per_key, self.skip_frames,
                                    frame_list, self.interpolation)
        
        return {'FINISHED'}


# This is the class for the file dialog of the exporter.
class ExportXYZ(Operator, ExportHelper):
    bl_idname = "molexport.xyz"
    bl_label  = "Export XYZ (*.xyz)"
    filename_ext = ".xyz"

    filter_glob  = StringProperty(
        default="*.xyz", options={'HIDDEN'},)

    atom_xyz_export_type = EnumProperty(
        name="Type of Objects",
        description="Choose type of objects",
        items=(('0', "All", "Export all active objects"),
               ('1', "Elements", "Export only those active objects which have"
                                 " a proper element name")),
               default='1',) 

    def draw(self, context):
        layout = self.layout
        row = layout.row()
        row.prop(self, "atom_xyz_export_type")

    def execute(self, context):
        export_xyz.export_xyz(self.atom_xyz_export_type, 
                              bpy.path.abspath(self.filepath))

        return {'FINISHED'}


# The entry into the menu 'file -> import'
def menu_func(self, context):
    self.layout.operator(ImportXYZ.bl_idname, text="XYZ (.xyz)")

# The entry into the menu 'file -> export'
def menu_func_export(self, context):
    self.layout.operator(ExportXYZ.bl_idname, text="XYZ (.xyz)")

def register():
    bpy.utils.register_module(__name__)
    bpy.types.INFO_MT_file_import.append(menu_func)
    bpy.types.INFO_MT_file_export.append(menu_func_export) 
    
def unregister():
    bpy.utils.unregister_module(__name__)
    bpy.types.INFO_MT_file_import.remove(menu_func)
    bpy.types.INFO_MT_file_export.remove(menu_func_export)

if __name__ == "__main__":

    register()
