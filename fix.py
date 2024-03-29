import bpy
import csv
import math
from mathutils import Matrix
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

# loop through the selection list
for obj in bpy.context.selected_objects:
    # get the object's name
    name = obj.name
    # get its lat and long from data by name
    try:
        i = data['Country'].index(name)
    except ValueError:      
        print("no location for", name)
        continue
        
    lat = float(data['Latitude'][i])
    lon = float(data['Longitude'][i])
    xyz = sphericalProjection(lat, lon)

    # set the object's origin
    bpy.context.view_layer.objects.active = obj
    bpy.context.scene.cursor.location = xyz
    bpy.ops.object.origin_set(type='ORIGIN_CURSOR')
    #remove object from selection
    obj.select_set(False)
    bpy.context.view_layer.objects.active = None

    # mw = obj.matrix_world
    # imw = mw.inverted()
    # me = obj.data
    # #convert xyz to a matrix
    # origin = Matrix.Translation(tuple(xyz))
    # local_origin = imw @ origin
    # neg_local_origin = [-x for x in local_origin]
    # me.transform(Matrix.Translation(neg_local_origin))
    # mw.translation += (origin - mw.translation)

# #get the active object
# obj = bpy.context.active_object
# #get its name
# name = obj.name
# #get its lat and long from data by name
# i = data['Location'].index(name)
# lat = float(data['Latitude'][i])
# lon = float(data['Longitude'][i])
# xyz = sphericalProjection(lat, lon)

# #set the 3d cursor to the xyz
# bpy.context.scene.cursor.location = xyz