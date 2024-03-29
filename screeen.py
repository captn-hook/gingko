import bpy
import bmesh
import math
import numpy as np
from mathutils import Vector, Quaternion, Matrix, Euler
import random
import sys
from importlib import reload
path = bpy.data.filepath.split("\\")
path = "\\".join(path[:-1])
sys.path.append(path)

if "utils" in locals():
    reload(utils)
else:
   from utils import *
   
if "bpyutils" in locals():
    reload(bpyutils)
else:
    from bpyutils import *

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output3.tsv")

finalZ = 1.1
step = 40
n_len = 20
frame_start = 1

def get_col(rootcol = "Screen", subcol = "Graph"):
    if rootcol in bpy.data.collections and subcol in bpy.data.collections[rootcol].children:
        return bpy.data.collections[rootcol].children[subcol]
    else:
        return None

def main():
    frame_counter = frame_start  # Start the frame counter at 0
    last_line = None  # Lines take into account the location of the NEXT node
    
    col = get_col()
    ncol = get_col("Screen", "Numbers.001") #named like Number + i + .001 # ASWELL AS A tens OBJECT AND A twentys OBJECT
    d = get_col("Key", "D") #named liked data[i]["Lineage"] + _D
    t = get_col("Key", "T") #named liked data[i]["Lineage"]

    # #should have 213 objects

    #sort all objects by their y position
    sorted_objs = sorted(col.objects, key=lambda x: x.location.y, reverse=True)
    #and save their y so we can use it later
    y_values = [o.location.y for o in sorted_objs]
    #set all x scales to 0, and shift them all up by the highest y value
    for o in sorted_objs:
        o.scale.x = 0
    seen_countries = set()
    seen_lineages = set()
    seen_i = 1
    tens_place = None
    stack_list = []
    for i in range(len(data['Date']) + 1): # we need an extra loop cus we do stuff i + 1
        # get data for this location
        if i < len(data['Date']):
            latlon = float(data['Latitude'][i]), float(data['Longitude'][i])

            lineage = data['Lineage'][i]

            country = data['Country'][i]

            color = data['Color'][i]        
        else:
            latlon = (0, 0)
            country = "End"
            lineage = "End"

        #if the next is the same, add this to the stack list and stop this iter
        if i + 1 < len(data['Date']) and data['Date'][i] == data['Date'][i + 1] and data['Country'][i + 1] == country:
            stack_list.append(i)
            continue

        #extend out timings if we are moving a lot
        if last_line is not None:
            dist = latlon_dist(latlon, last_line[0])
            max = 13329.7
            frame_counter += dist / max

        # if i + 1 < len(data['Date']) and data['Country'][i + 1] != country:
        #     #if we are moving to a new location, increment the frame counter
        #     frame_counter += 1.5

        frame = frame_counter * step  # Calculate the frame number
        stack_list.append(i)
        for j in stack_list:
            j = int(j)
            if j >= len(data['Date']):
                break

            if data['Lineage'][j] not in seen_lineages:

                #get the two objects for the key
                name = data['Lineage'][j]
                text = t.objects.get(name.replace(".", "_"))
                dot = d.objects.get(name + "_D")
                #set the dot to scale 0
                dot.scale = (0, 0, 0)
                dot.keyframe_insert(data_path="scale", frame=frame - n_len)
                dot.scale = (100.6, 100.6, 100.6)
                dot.keyframe_insert(data_path="scale", frame=frame)

                #get the mix shader on the text material
                mat = text.data.materials[0]
                mix = mat.node_tree.nodes.get("Mix Shader")
                #set the mix shader to 1
                mix.inputs[0].default_value = 1
                mix.inputs[0].keyframe_insert(data_path="default_value", frame=frame - n_len)
                mix.inputs[0].default_value = 0
                mix.inputs[0].keyframe_insert(data_path="default_value", frame=frame)

                seen_lineages.add(data['Lineage'][j])
            else:
                dot = d.objects.get(data['Lineage'][j] + "_D")

            # #get the sorted_objs[j] and scale it back to 1 over this frame
            sorted_objs[j].scale.x = 0
            sorted_objs[j].keyframe_insert(data_path="scale", frame=frame)
            sorted_objs[j].scale.x = 1
            sorted_objs[j].keyframe_insert(data_path="scale", frame=frame+step/2)

            #replace the material of sorted_objs[j] with material on its dot
            sorted_objs[j].data.materials[0] = dot.data.materials[0]

            if data['Country'][j] not in seen_countries:
                #set the last number to invisible
                if last_line is not None:
                    #last_keyframe(frame, last_num, n_len)
                    last_num = last_line[3]
                    last_keyframe(frame, last_num, n_len)

                #get Number + seen_i + .001
                new_num = ncol.objects.get("Number" + str(seen_i) + ".001")
                num_keyframe(frame, new_num, n_len)
                # if we are at a ten or twenty, we need to keyframe the tens place
                
                if seen_i == 1:
                    #last keyframe the 0 object
                    z = ncol.objects.get("zero")
                    last_keyframe(frame, z, n_len)

                if seen_i == 10:
                    tens_place = ncol.objects.get("tens")
                    num_keyframe(frame, tens_place, n_len)
                if seen_i == 20:
                    last_keyframe(frame, tens_place, n_len)
                    
                    tens_place = ncol.objects.get("twentys")
                    num_keyframe(frame, tens_place, n_len)

                if seen_i == 30:
                    last_keyframe(frame, tens_place, n_len)

                    tens_place = ncol.objects.get("thirtys")
                    num_keyframe(frame, tens_place, n_len)
                if seen_i == 40:
                    last_keyframe(frame, tens_place, n_len)

                    tens_place = ncol.objects.get("fortys")
                    num_keyframe(frame, tens_place, n_len)

                last_num = new_num
                seen_countries.add(data['Country'][j])
                seen_i = seen_i + 1

            

            last_line = (latlon, data['Country'][j], frame, last_num, tens_place)
        
        if len(stack_list) >= 1:
            stack_list = []

        frame_counter += 1  # Increment the frame counter

def num_keyframe(frame, new_num, n_len):
    #set the new number to visible
    new_num.hide_render = True
    new_num.hide_viewport = True
    new_num.keyframe_insert(data_path="hide_render", frame=frame-1)
    new_num.keyframe_insert(data_path="hide_viewport", frame=frame-1)
    new_num.hide_render = False
    new_num.hide_viewport = False
    new_num.keyframe_insert(data_path="hide_render", frame=frame)
    new_num.keyframe_insert(data_path="hide_viewport", frame=frame)

    #keyframe its X rotation
    # 90 degrees
    new_num.rotation_euler.x = math.radians(90)
    new_num.keyframe_insert(data_path="rotation_euler", frame=frame)
    # 0 degrees
    new_num.rotation_euler.x = math.radians(0)
    new_num.keyframe_insert(data_path="rotation_euler", frame=frame+n_len)

def last_keyframe(frame, last_num, n_len):
    last_num.hide_render = False
    last_num.hide_viewport = False
    last_num.keyframe_insert(data_path="hide_render", frame=frame+n_len)
    last_num.keyframe_insert(data_path="hide_viewport", frame=frame+n_len)
    last_num.hide_render = True
    # last_num.hide_viewport = True
    last_num.keyframe_insert(data_path="hide_render", frame=frame+n_len+1)
    # last_num.keyframe_insert(data_path="hide_viewport", frame=frame)'

    #keyframe its X rotation
    # 0 degrees
    last_num.rotation_euler.x = math.radians(0)
    last_num.keyframe_insert(data_path="rotation_euler", frame=frame)
    # -90 degrees
    last_num.rotation_euler.x = math.radians(-90)
    last_num.keyframe_insert(data_path="rotation_euler", frame=frame+n_len)
# # layout()        
main()
#test()