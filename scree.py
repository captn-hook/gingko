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

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output4.tsv")

def simple_material(obj, color):
    #creates a material for the object, and a rgb node connected to a material output
    # Create a new material
    mat = bpy.data.materials.new(name=obj.name + "Material")
    obj.data.materials.append(mat)
    # Set the material to shadeless
    mat.use_nodes = True
    #get the nodes
    nodes = mat.node_tree.nodes
    #clear the nodes
    for node in nodes:
        nodes.remove(node)
    #create a mix shader node
    output = nodes.new(type='ShaderNodeOutputMaterial')
    # Create a new rgb node
    rgb = nodes.new(type='ShaderNodeRGB')
    rgb.outputs[0].default_value = hex_to_rgb(stringtohex(color))
    # Connect the rgb node to the output node
    mat.node_tree.links.new(rgb.outputs[0], output.inputs[0])
    return mat

def stringtohex(string):
    #converts a string of 6 characters to a hex number for hex_to_rgb
    return int(string, 16)

def srgb_to_linearrgb(c):
    if   c < 0:       return 0
    elif c < 0.04045: return c/12.92
    else:             return ((c+0.055)/1.055)**2.4

def hex_to_rgb(h,alpha=1):
    r = (h & 0xff0000) >> 16
    g = (h & 0x00ff00) >> 8
    b = (h & 0x0000ff)
    return tuple([srgb_to_linearrgb(c/0xff) for c in (r,g,b)] + [alpha])

#for every unique in Color column, create sample object with that color
for color in set(data["Color"]):
    #create a sphere
    bpy.ops.mesh.primitive_uv_sphere_add(radius=0.1, location=(0, 0, 0))
    #get the sphere
    sphere = bpy.context.active_object
    #create a material for the sphere
    simple_material(sphere, color)
    #create a collection for the sphere
    col = bpy.data.collections.new(color)
    bpy.context.scene.collection.children.link(col)
    #link the sphere to the collection
    col.objects.link(sphere)
