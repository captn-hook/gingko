import bpy 

for obj in bpy.context.selected_objects:
    obj.name = obj.name + '_O'