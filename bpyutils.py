import bpy
import bmesh
from utils import sphereRotation

cylinderScale = [1, .1] #radius, height

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

def createCamera(sphereRadius = 100):
    #creates a camera facing the origin with a empty parent at the origin.
    camera_col = new_collection("CameraCollection")
    # Create a new camera
    cam = bpy.data.cameras.new("Camera")
    empty = bpy.data.objects.new("Empty", None)
    empty.location = (0, 0, 0)
    camObj = bpy.data.objects.new("Camera", cam)
    camObj.parent = empty
    camObj.location = (0, 0, sphereRadius * 1.6)
    camObj.rotation_euler = (0, 0, 0)
    camObj.data.type = 'ORTHO'
    camObj.data.ortho_scale = sphereRadius

    camera_col.objects.link(empty)
    camera_col.objects.link(camObj)

    #set the camera empty to quaternion rotation
    empty.rotation_mode = 'QUATERNION'
    return empty #animator manipulates the empty

def new_collection(name, parent=None):
    # create a new collection
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
    
    return col