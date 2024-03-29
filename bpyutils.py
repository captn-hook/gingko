import bpy
import bmesh
import sys
#split path at last /
path = bpy.data.filepath.split("\\")
path = "\\".join(path[:-1])
sys.path.append(path)

from importlib import reload
if "utils" in locals():
    reload(utils)
else:
   from utils import *


cylinderScale = [.5, .1] #radius, height

def getPlaneIcon(colname = "PlaneIcon", objname = "Plane", parent = None, collection = None):
    #gets a new copy of the plane icon
    col = find_collection(colname)
    assert col.objects[0].name == objname, "incorrect object"
    
    #copy the object
    og = col.objects[0]
    obj = og.copy()
    obj.data = col.objects[0].data.copy()
    obj.name = objname + 'Copy'

    if parent:
        obj.parent = parent

    if collection:
        collection.objects.link(obj)

    return obj

def keyframeVisible(obj, frame):
    #set to visible
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    return obj

def keyframeInvisible(obj, frame, view=True):
    #set to invisible
    if view:
        obj.hide_viewport = True
        obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=frame)
    return obj

def createCylinder(location, name, parent=None, collection=None):
    # Create a new mesh
    mesh = bpy.data.meshes.new(name)

    # Create a new object associated with the mesh
    obj = bpy.data.objects.new(name, mesh)

    # Set the parent object
    if parent is not None:
        obj.parent = parent

    # Add the object to the collection
    if collection is not None:
        collection.objects.link(obj)

    # Create a new bmesh object
    bm = bmesh.new()

    # Create a cylinder
    bmesh.ops.create_cone(
        bm,
        cap_ends=True,
        cap_tris=False,
        segments=32,
        radius1=cylinderScale[0],
        radius2=cylinderScale[0],
        depth=cylinderScale[1],
        matrix=obj.matrix_world,
    )

    # Update the mesh with the new data
    bm.to_mesh(mesh)
    bm.free()

    # Move the object to the desired location
    obj.location = location
    #for sphere
    obj.rotation_euler = sphereRotation(location)

    return obj

def createCamera(sphereRadius):
    #creates a camera facing the origin with a empty parent at the origin.
    camera_col = new_collection("CameraCollection")
    # Create a new camera
    cam = bpy.data.cameras.new("Camera")
    empty = bpy.data.objects.new("Empty", None)
    empty.location = (0, 0, 0)
    camObj = bpy.data.objects.new("Camera", cam)
    camObj.parent = empty
    camObj.location = (0, 0, sphereRadius * 2)
    camObj.rotation_euler = (0, 0, 0)
    camObj.data.type = 'ORTHO'
    camObj.data.ortho_scale = sphereRadius

    camera_col.objects.link(empty)
    camera_col.objects.link(camObj)

    #set the camera empty to quaternion rotation
    empty.rotation_mode = 'QUATERNION'
    return empty, camObj #animator manipulates the empty

def createMarker(sphereRadius, col = None):
    #similiar to the camera, but just 2 empties

    empty_rotator = bpy.data.objects.new("Empty", None)
    empty_marker = bpy.data.objects.new("Empty", None)

    empty_marker.parent = empty_rotator

    empty_rotator.location = (0, 0, 0)
    empty_marker.location = (0, 0, sphereRadius + 10)

    if col:
        col.objects.link(empty_rotator)
        col.objects.link(empty_marker)
    else:
        bpy.context.scene.collection.objects.link(empty_rotator)
        bpy.context.scene.collection.objects.link(empty_marker)

    empty_rotator.rotation_mode = 'QUATERNION'

    return empty_rotator, empty_marker

def new_collection(name, parent=None):
    # create a new collection
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
    
    return col

def find_collection(name, fuzzy=False):
    # find a collection by name
    for col in bpy.data.collections:
        if fuzzy:
            if name in col.name:
                return col
        else:
            if col.name == name:
                return col
    return None

def check_countries(fuzzy=True):
    data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output3.tsv")
    done = []
    #for every country in the data
    for country in data['Country']:
        #check if a collection exists for the country
        if not done.count(country) > 0 and not find_collection(country, fuzzy):
            done.append(country)
            print("Couldnt find collection for: " + country)


def countryMaterials(fuzzy=False):
    #duplicate a material for every selected object
    done = []
    for obj in bpy.context.selected_objects:
        country = obj.name
        col = find_collection(country, fuzzy)
        if not done.count(country) > 0 and col:
            done.append(country)
            print("Collection for " + country + ", is: " + col.name + " with object: " + obj.name)
            mat = bpy.data.materials.new(name=country)
            #clone the old material and rename it
            mat = obj.active_material.copy()
            mat.name = country
            obj.active_material = mat
            

#check_countries(False)
#countryMaterials()

    

