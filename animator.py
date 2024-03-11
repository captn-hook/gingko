import bpy
import bmesh
from mathutils import Vector
import math
import random

from utils import getData, equirectangularProjection, sphericalProjection, latlon_dist, sphereNormal, sphereQuat, distance
from bpyutils import createCylinder, keyframeVisible, keyframeInvisible, createCamera, new_collection

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output.tsv")
#order data by collection date

textScale = [1, 1, 1]
textLocation = [.8, .5, .15]
initialZ = 0
finalZ = .01
zSlideFrames = 15
step = 20
cam_frame_back = 10
frame_start = 1

def keyframeCam(obj, frame, location):
    # Get the target rotation
    target_quat = sphereQuat(location)

    # If the dot product is negative, negate the target quaternion
    if obj.rotation_quaternion.dot(target_quat) < 0:
        target_quat = -target_quat

    # Set the rotation and keyframe it
    obj.rotation_quaternion = target_quat
    obj.keyframe_insert(data_path="rotation_quaternion", frame=frame + cam_frame_back)
    return obj

def createText(string, location, scale, parent, col):
    # create text
    text = bpy.data.curves.new(type="FONT", name="Text")
    text.body = string
    textObj = bpy.data.objects.new(string, object_data=text)

    textObj.location = location
    textObj.scale = scale

    col.objects.link(textObj)
    textObj.parent = parent

    return textObj

def keyframeLocationsFlat(obj, frame):
    #set keyframe at 0 at frame
    obj.location = (obj.location[0], obj.location[1], initialZ)
    obj.keyframe_insert(data_path="location", frame=frame)
    #set keyframe at finalZ at frame + zSlideFrames
    obj.location = (obj.location[0], obj.location[1], finalZ)
    obj.keyframe_insert(data_path="location", frame=(frame + zSlideFrames))
    return obj

def keyframeLocations(obj, frame):
    # set keyframe to current location at frame
    obj.keyframe_insert(data_path="location", frame=frame)
    # get the normal vector of the sphere at the location
    normal = sphereNormal(obj.location)
    # move the object in the normal direction by finalZ
    obj.location = obj.location + normal * finalZ
    # set keyframe at finalZ at frame + zSlideFrames
    obj.keyframe_insert(data_path="location", frame=(frame + zSlideFrames))
    return obj


def createLine(location, name, parent=None, collection=None):
    # Create a new curve
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 6

    # Create a new object associated with the curve
    obj = bpy.data.objects.new(name, curve)

    # Set the parent object
    if parent is not None:
        obj.parent = parent

    # Add the object to the collection
    if collection is not None:
        collection.objects.link(obj)

    obj.data.bevel_depth = .3

    # Create a spline with 3 points and 2 handles
    spline = curve.splines.new('NURBS')
    spline.points.add(3)
    spline.use_endpoint_u = True
    spline.use_endpoint_v = True
    spline.points[0].co = (0, 0, 0, 1)
    spline.points[1].co = (0, 0, 0, 1)
    spline.points[2].co = (0, 0, 0, 1)
    spline.points[3].co = (0, 0, 0, 1)

    #handle 1 is the endpt of the line and handle 2 is the midpoint
    #create empties
    h1 = bpy.data.objects.new(name + "Handle1", None)
    h2 = bpy.data.objects.new(name + "Handle2", None)
    h1.location = location
    h2.location = location
    # h1.parent = obj
    # h2.parent = obj

    #link them to the collection
    if collection is not None:
        collection.objects.link(h1)
        collection.objects.link(h2)

    #set their location
    # h1.location = location
    # h2.location = location

    m = obj.modifiers.new(name + "Handle1", 'HOOK')
    xyz = Vector(spline.points[0].co[0:3])
    m.center = xyz

    m.vertex_indices_set([0])
    bpy.context.evaluated_depsgraph_get() # magic spell
    m.object = h1

    m = obj.modifiers.new(name + "Handle1.5", 'HOOK')
    xyz = Vector(spline.points[1].co[0:3])
    m.center = xyz

    m.vertex_indices_set([1])
    bpy.context.evaluated_depsgraph_get() # magic spell
    m.object = h1

    m = obj.modifiers.new(name + "Handle2", 'HOOK')
    xyz = Vector(spline.points[2].co[0:3])
    m.center = xyz

    m.vertex_indices_set([2])
    bpy.context.evaluated_depsgraph_get() # magic spell
    m.object = h2

    return obj, h1, h2  
    
def keyframeLineFirst(h1, h2, frame):
    #set keyframes for the handles
    h1.keyframe_insert(data_path="location", frame=frame)
    h2.keyframe_insert(data_path="location", frame=frame)
    return h1, h2

def keyframeLineSecond(h1, h2, frame, location, midpoint):
    #and h2 to the midpoint + some normal, in order to make an arc
    #location and midpoint are world space, convert to local space with the handle's parent
    #first make 4d vectors instead of 3d
    if h1.parent is not None:
        location = Vector((location[0], location[1], location[2], 1))
        midpoint = Vector((midpoint[0], midpoint[1], midpoint[2], 1))
        #convert to local space
        location = h1.matrix_world.inverted() @ location
        midpoint = h1.matrix_world.inverted() @ midpoint
        #set the location
        location = Vector((location[0], location[1], location[2]))
        midpoint = Vector((midpoint[0], midpoint[1], midpoint[2]))
    
    h1.location = Vector(location)
    h2.location = Vector(midpoint)
    #and set the rotation
    h1.keyframe_insert(data_path="location", frame=frame)
    h2.keyframe_insert(data_path="location", frame=frame)

    return h1, h2

def keyframeLineThird(h1, h2, frame, location, midpoint):
    #similar to the second keyframe, but not as far above the ground
    if h1.parent is not None:
        location = Vector((location[0], location[1], location[2], 1))
        midpoint = Vector((midpoint[0], midpoint[1], midpoint[2], 1))
        location = h1.matrix_world.inverted() @ location
        midpoint = h1.matrix_world.inverted() @ midpoint
        location = Vector((location[0], location[1], location[2]))
        midpoint = Vector((midpoint[0], midpoint[1], midpoint[2]))

    normal = sphereNormal(midpoint)

    h1.location = Vector(location)
    h2.location = Vector(midpoint)
    h1.keyframe_insert(data_path="location", frame=frame)
    h2.keyframe_insert(data_path="location", frame=frame)

def keyframeLineThickness(obj, frame, thickness):
    #set keyframe for bevel depth
    obj.data.bevel_depth = thickness
    obj.data.keyframe_insert(data_path="bevel_depth", frame=frame)
    return obj

labeled = []
def main(cameraEmpty):
    #collection for these objects
    if "NodeCollection" in bpy.data.collections:
        col = bpy.data.collections["NodeCollection"]
    else:
        col = new_collection("NodeCollection")
    lcol = new_collection("Lines", col)
    tcol = new_collection("Labels", col)
    location_collections = {}  # Dictionary to store collections for each location
    frame_counter = frame_start  # Start the frame counter at 0
    last_line = None  # Lines take into account the location of the NEXT node
    for i in range(len(data['Collection date'])):
        # create cylinder
        latlon = float(data['Latitude'][i]), float(data['Longitude'][i])

        if last_line is not None and latlon_dist(latlon, last_line[2]) > 3:
            frame_counter += 1
            if latlon_dist(latlon, last_line[2]) > 5:
                frame_counter += 1  
                if latlon_dist(latlon, last_line[2]) > 10:
                    frame_counter += 1

        # coords = equirectangularProjection(location[0], location[1])
        coords = sphericalProjection(latlon[0], latlon[1])
        location_name = data['Location'][i]
        
        if location_name + "Nodes" not in location_collections:
            #check if the collection exists in NodeCollection
            if location_name + "Nodes" in bpy.data.collections:
                location_collections[location_name] = bpy.data.collections[location_name + "Nodes"]
            else:
                location_collections[location_name] = new_collection(location_name + "Nodes", col)

        # spawn the cylinder in the globe a lil
        coordsback = Vector(coords) - sphereNormal(coords) * .003
        cyl = createCylinder(coordsback, str(frame_counter) + ', ' + location_name + ', ' + str(coords), collection=location_collections[location_name])

        line, h1, h2 = createLine(coords, "Line from " + location_name + " at " + str(frame_counter), cyl, lcol)
        # h1 and h2 are the handles of the line for animation, and one point of the line is always at coords


        # create text and make a child of cylinder
        if location_name not in labeled:
            text = createText(location_name, textLocation, textScale, cyl, tcol)
            keyframeVisible(text, frame_counter)
            keyframeInvisible(text, frame_counter - 1)
            labeled.append(location_name)

        # set visibility keyframes for both
        keyframeVisible(cyl, frame_counter)
        keyframeInvisible(cyl, frame_counter - 1)
        # set location keyframes for cylinder
        keyframeLocations(cyl, frame_counter)
        keyframeCam(cameraEmpty, frame_counter, coords)

        #line keyframes
        keyframeVisible(line, frame_counter)
        keyframeInvisible(line, frame_counter - 1)
        keyframeInvisible(line, frame_counter + 2, False)
        keyframeLineThickness(line, frame_counter - 2, 0)
        keyframeLineThickness(line, frame_counter - 1, 1)
        keyframeLineThickness(line, frame_counter + 1, 0)
        
        keyframeLineFirst(h1, h2, frame_counter)
        if last_line is not None:
            # get a target lat lon
            min_distance = 75
            max = 150
            i = random.randint(0, len(data['Collection date']) - 1)
            target = (float(data['Latitude'][i]), float(data['Longitude'][i]))
            target = sphericalProjection(target[0], target[1])
            last = sphericalProjection(last_line[2][0], last_line[2][1])
           
            while max < distance(target, last) < min_distance or max < distance(target, coords) < min_distance * 1.5:
                i = random.randint(0, len(data['Collection date']) - 1)
                target = (float(data['Latitude'][i]), float(data['Longitude'][i]))
                target = sphericalProjection(target[0], target[1])

            # to xyz
            target = sphericalProjection(target[0], target[1])
            # get the midpoint between the two nodes
            half = ((target[0] + last[0]) / 2, (target[1] + last[1]) / 2, (target[2] + last[2]) / 2)
            # get the midpoint between the midpoint and the last node
            midpointhalf = ((half[0] + last[0]) / 2, (half[1] + last[1]) / 2, (half[2] + last[2]) / 2)
            #ensure that midpoints are sphere radius away from 0,0,0
            ensure = 100
            if distance(midpointhalf, (0, 0, 0)) < ensure:
                #push it along normal to 110
                normal = sphereNormal(midpointhalf)
                midpointhalf = Vector(midpointhalf) + normal * (ensure - distance(midpointhalf, (0, 0, 0))) *.07

            if distance(half, (0, 0, 0)) < ensure:
                #push it along normal to 110
                normal = sphereNormal(half)
                half1 = Vector(half) + normal * (ensure - distance(half, (0, 0, 0))) *.03
                half2 = Vector(half) + normal * (ensure - distance(half, (0, 0, 0))) *.07

            last_line[0].name = "H1 from " + last_line[3] + " to " + data['Location'][i] + ", " + str(half) + "->" + str(target)
            last_line[1].name = "H2 from " + last_line[3] + " to " + data['Location'][i] + ", " + str(midpointhalf) + "->" + str(half)

            keyframeLineSecond(last_line[0], last_line[1], frame_counter, half1, midpointhalf)
            keyframeLineThird(last_line[0], last_line[1], frame_counter + 1, target, half2)

        last_line = (h1, h2, latlon, location_name)

        frame_counter += 1  # Increment the frame counter

def layout():
    new_collection("GridsCollection")
    #creates a grid of lat long points (equirectangular projection)
    for latitude in range(-90, 100, 10):
        for longitude in range(-180, 190, 20):
            #coords = equirectangularProjection(latitude, longitude)
            coords = sphericalProjection(latitude, longitude)
            createCylinder(coords, str(latitude) + ', ' + str(longitude) + ' => ' + str(coords))

cam = createCamera()
# layout()        
main(cam)