import bpy
import bmesh
from mathutils import Vector
import os
import csv
import math
import geopandas as gpd
import random

def countryData(path):
    data = gpd.read_file(path, engine='pyogrio', use_arrow=True, layer='ADM_0')
    return data

def getData(path):
    sep = '\t'
    data = {}
    with open(path, 'r') as f:
        reader = csv.reader(f, delimiter=sep)
        headers = next(reader)
        for h in headers:
            data[h] = []
        for row in reader:
            for i in range(len(row)):
                data[headers[i]].append(row[i])

    # Convert 'Collection date' to integers
    data['Collection date'] = list(map(int, data['Collection date']))

    # Pair each 'Collection date' with its corresponding data row
    data_pairs = list(zip(data['Collection date'], *[data[h] for h in headers if h != 'Collection date']))

    # Sort these pairs
    data_pairs.sort()

    # Unzip them back into separate lists
    data['Collection date'], *other_data = zip(*data_pairs)

    # Assign the sorted data back to their respective keys
    for i, h in enumerate(headers):
        if h != 'Collection date':
            data[h] = other_data[i-1]

    return data

def ls(path):
    return os.listdir(path)

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output.tsv")
# cData = countryData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\gadm_410-levels.gpkg")
#order data by collection date
def plot_country_meshes(data):
    if "CountryCollection" in bpy.data.collections:
        countriescol = bpy.data.collections["CountryCollection"]
    else:
        countriescol = new_collection("CountryCollection")

    for index, row in data.iterrows():
        country_name = row['COUNTRY']
        print(f"Plotting {country_name}... {index}/{len(data)}")
        print(f"{index/len(data)*100:.2f}% complete")

        countrycol = new_collection(country_name, countriescol)

        multipolygon = row['geometry'].geoms
        #sort by area
        sortedMultipolygons = sorted(multipolygon, key=lambda x: x.area, reverse=True)

        for polygon in sortedMultipolygons:
            # Create a new mesh
            mesh = bpy.data.meshes.new(country_name)

            # Create a new object associated with the mesh
            obj = bpy.data.objects.new(country_name, mesh)

            # Link the new object to the collection
            countrycol.objects.link(obj)

            #bmesh
            bm = bmesh.new()        

            polygon = polygon.simplify(0.05, preserve_topology=True)

            for vertex in polygon.exterior.coords:
                xyz = sphericalProjection(vertex[1], vertex[0])
                bm.verts.new(xyz)

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            bm.faces.new(bm.verts)

            bm.to_mesh(mesh)
            bm.free()

    return countriescol

textScale = [1, 1, 1]
textLocation = [.8, .5, .15]
cylinderScale = [1, .1] #radius, height
initialZ = 0
finalZ = .001
zSlideFrames = 15
step = 20
cam_frame_back = 10
frame_start = 1
def keyframeVisible(obj, frame):
    #set to visible
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame * step)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame * step)
    return obj

def keyframeInvisible(obj, frame, view=True):
    #set to invisible
    if view:
        obj.hide_viewport = True
        obj.keyframe_insert(data_path="hide_viewport", frame=frame * step)
    obj.hide_render = True
    obj.keyframe_insert(data_path="hide_render", frame=frame * step)
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
        bpy.context.collection.objects.unlink(obj)

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
    camObj.location = (0, 0, sphereRadius * 1.4)
    camObj.rotation_euler = (0, 0, 0)
    camObj.data.type = 'ORTHO'
    camObj.data.ortho_scale = sphereRadius

    camera_col.objects.link(empty)
    camera_col.objects.link(camObj)

    #set the camera empty to quaternion rotation
    empty.rotation_mode = 'QUATERNION'
    return empty #animator manipulates the empty

def keyframeCam(obj, frame, location):
    # Get the target rotation
    target_quat = sphereQuat(location)

    # If the dot product is negative, negate the target quaternion
    if obj.rotation_quaternion.dot(target_quat) < 0:
        target_quat = -target_quat

    # Set the rotation and keyframe it
    obj.rotation_quaternion = target_quat
    obj.keyframe_insert(data_path="rotation_quaternion", frame=frame * step + cam_frame_back)
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
    obj.keyframe_insert(data_path="location", frame=frame * step)
    #set keyframe at finalZ at frame + zSlideFrames
    obj.location = (obj.location[0], obj.location[1], finalZ)
    obj.keyframe_insert(data_path="location", frame=(frame + zSlideFrames) * step)
    return obj

def keyframeLocations(obj, frame):
    # set keyframe to current location at frame
    obj.keyframe_insert(data_path="location", frame=frame)
    # get the normal vector of the sphere at the location
    normal = sphereNormal(obj.location)
    # move the object in the normal direction by finalZ
    obj.location = obj.location + normal * finalZ
    # set keyframe at finalZ at frame + zSlideFrames
    obj.keyframe_insert(data_path="location", frame=(frame + zSlideFrames) * step)
    return obj

def equirectangularProjection(lat, lon):
    #converts lat (=90 to -90) and lon (=180 to -180) to x, y, z
    x = lon
    y = lat
    return (x, y)

def sphericalProjection(lat, lon, radius=100):
    # Convert latitude and longitude into radians
    lat_rad = math.radians(90 - lat) # convert from latitude to inclination (theta)
    lon_rad = math.radians(lon)

    # Convert lat/lon (spherical coordinates) to cartesian coordinates
    x = radius * math.sin(lat_rad) * math.cos(lon_rad)
    y = radius * math.sin(lat_rad) * math.sin(lon_rad)
    z = radius * math.cos(lat_rad)

    return (x, y, z)

def sphereNormal(location1, location2=(0, 0, 0)):
    #returns the normal vector of the surface point 1 of a sphere at point 2
    return Vector(location1) - Vector(location2)

def sphereRotation(location):
    #returns the x, y, z euler of a normal vector
    normal = sphereNormal(location)
    return normal.to_track_quat('Z', 'Y').to_euler()

def sphereQuat(location):
    #returns the quaternion of a normal vector
    normal = sphereNormal(location)
    return normal.to_track_quat('Z', 'Y')

def createLine(location, name, parent=None, collection=None):
    # Create a new curve
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 2

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
    h1.keyframe_insert(data_path="location", frame=frame * step)
    h2.keyframe_insert(data_path="location", frame=frame * step)
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
    h1.keyframe_insert(data_path="location", frame=frame * step)
    h2.keyframe_insert(data_path="location", frame=frame * step)

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
    h1.keyframe_insert(data_path="location", frame=frame * step)
    h2.keyframe_insert(data_path="location", frame=frame * step)

def latlon_dist(latlon1, latlon2):
    #returns the real distance between two latlon points
    #One degree of latitude equals approximately 364,000 feet (69 miles),
    #One-degree of longitude equals 288,200 feet (54.6 miles)
    lat = 69
    lon = 54.6
    return math.sqrt((latlon1[0] - latlon2[0])**2 * lat**2 + (latlon1[1] - latlon2[1])**2 * lon**2) / 1000

def distance(p1, p2):
    #returns the distance between two 3d points
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

def keyframeLineThickness(obj, frame, thickness):
    #set keyframe for bevel depth
    obj.data.bevel_depth = thickness
    obj.data.keyframe_insert(data_path="bevel_depth", frame=frame * step)
    return obj

labeled = []
def main(cameraEmpty):
    #collection for these objects
    col = new_collection("NodeCollection")
    lcol = new_collection("Lines", col)
    tcol = new_collection("Labels", col)
    location_collections = {}  # Dictionary to store collections for each location
    frame_counter = frame_start  # Start the frame counter at 0
    last_line = None  # Lines take into account the location of the NEXT node
    for i in range(len(data['Collection date'])):
        # create cylinder
        latlon = float(data['Latitude'][i]), float(data['Longitude'][i])

        if last_line is not None and latlon_dist(latlon, last_line[2]) > 4:
            frame_counter += 1
            if latlon_dist(latlon, last_line[2]) > 7:
                frame_counter += 1  
        # coords = equirectangularProjection(location[0], location[1])
        coords = sphericalProjection(latlon[0], latlon[1])
        location_name = data['Location'][i]

        cyl = createCylinder(coords, str(frame_counter) + ', ' + location_name + ', ' + str(coords))

        line, h1, h2 = createLine(coords, "Line from " + location_name + " at " + str(frame_counter), cyl, lcol)
        # h1 and h2 are the handles of the line for animation, and one point of the line is always at coords

        # If a collection for this location does not exist, create it
        if location_name not in location_collections:
            location_collections[location_name] = new_collection(location_name, col)
            location_collections[location_name + "Lines"] = new_collection(location_name + "Lines", location_collections[location_name])

        # Add the cylinder to the collection for this location
        location_collections[location_name].objects.link(cyl)
        location_collections[location_name + "Lines"].objects.link(line)

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
        keyframeInvisible(line, frame_counter + 2)
        keyframeLineThickness(line, frame_counter - 1, 0)
        keyframeLineThickness(line, frame_counter, 1)
        keyframeLineThickness(line, frame_counter + 2, 0)
        
        keyframeLineFirst(h1, h2, frame_counter)
        if last_line is not None:
            # get a target lat lon
            min_distance = 7
            max = 12
            i = random.randint(0, len(data['Collection date']) - 1)
            target = (float(data['Latitude'][i]), float(data['Longitude'][i]))
            while max < latlon_dist(target, latlon) < min_distance or max < latlon_dist(target, last_line[2]) < min_distance:
                i = random.randint(0, len(data['Collection date']) - 1)
                target = (float(data['Latitude'][i]), float(data['Longitude'][i]))

            # to xyz
            target = sphericalProjection(target[0], target[1])
            last = sphericalProjection(last_line[2][0], last_line[2][1])
            # get the midpoint between the two nodes
            half = ((target[0] + last[0]) / 2, (target[1] + last[1]) / 2, (target[2] + last[2]) / 2)
            # get the midpoint between the midpoint and the last node
            midpointhalf = ((half[0] + last[0]) / 2, (half[1] + last[1]) / 2, (half[2] + last[2]) / 2)
            #ensure that midpoints are sphere radius away from 0,0,0
            ensure = 100
            if distance(midpointhalf, (0, 0, 0)) < ensure:
                #push it along normal to 110
                normal = sphereNormal(midpointhalf)
                midpointhalf = Vector(midpointhalf) + normal * (ensure - distance(midpointhalf, (0, 0, 0))) *.1

            if distance(half, (0, 0, 0)) < ensure:
                #push it along normal to 110
                normal = sphereNormal(half)
                half = Vector(half) + normal * (ensure - distance(half, (0, 0, 0))) *.01

            last_line[0].name = "H1 from " + last_line[3] + " to " + data['Location'][i] + ", " + str(half) + "->" + str(target)
            last_line[1].name = "H2 from " + last_line[3] + " to " + data['Location'][i] + ", " + str(midpointhalf) + "->" + str(half)

            keyframeLineSecond(last_line[0], last_line[1], frame_counter, half, midpointhalf)
            keyframeLineThird(last_line[0], last_line[1], frame_counter + 1, target, half)

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

def new_collection(name, parent=None):
    # create a new collection
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
    
    return col

# plot_country_meshes(cData)
cam = createCamera()
# layout()        
main(cam)