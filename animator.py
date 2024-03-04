import bpy
import bmesh
from mathutils import Vector
import os
import csv

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
#order data by collection date

# print headers // should be Collection date	Region	Country	State	City	County	Airport	Latitude	Longitude
# collection date is an integer from 0 to n

# for each row in the data, create a new cylinder at the lat and long
# and set keygrames for the cylinder to appear at the collection date, aswell as animated from z = 0 to z = -1 over some period (to make it fade into the ground)
# and create a text label as a child of the cylinder with the location name

textScale = [1, 1, 1]
textLocation = [.8, .5, .15]
cylinderScale = [1, .1] #radius, height
initialZ = -1
finalZ = 1
zSlideFrames = 15

def keyframeVisible(obj, frame):
    #set to visible
    obj.hide_render = False
    obj.hide_viewport = False
    obj.keyframe_insert(data_path="hide_render", frame=frame)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    return obj

def keyframeInvisible(obj, frame):
    #set to invisible
    obj.hide_render = True
    obj.hide_viewport = True
    obj.keyframe_insert(data_path="hide_render", frame=frame)
    obj.keyframe_insert(data_path="hide_viewport", frame=frame)
    return obj


def createCylinder(location, name, parent=None, collection=None):
    # Create a new mesh
    mesh = bpy.data.meshes.new(name)

    # Create a new object associated with the mesh
    obj = bpy.data.objects.new(name, mesh)

    # Link the new object to the scene
    bpy.context.collection.objects.link(obj)

    # Set the new object as the active object in the scene
    bpy.context.view_layer.objects.active = obj
    obj.select_set(True)

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
    obj.location = Vector((location[0], location[1], initialZ))

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

    textObj = bpy.context.object
    return textObj

def keyframeLocations(obj, frame):
    #set keyframe at 0 at frame
    obj.location = (obj.location[0], obj.location[1], initialZ)
    obj.keyframe_insert(data_path="location", frame=frame)
    #set keyframe at finalZ at frame + zSlideFrames
    obj.location = (obj.location[0], obj.location[1], finalZ)
    obj.keyframe_insert(data_path="location", frame=frame + zSlideFrames)
    return obj

def equirectangularProjection(lat, lon):
    #converts lat (=90 to -90) and lon (=180 to -180) to x, y, z
    x = lon
    y = lat
    return (x, y)

labeled = []
def main():
    #collection for these objects
    col = new_collection("Nodes")
    tcol = new_collection("TextCollection", col)
    location_collections = {}  # Dictionary to store collections for each location
    for i in range(len(data['Collection date'])):
        # create cylinder
        location = float(data['Latitude'][i]), float(data['Longitude'][i])
        coords = equirectangularProjection(location[0], location[1])
        date = data['Collection date'][i]
        date = int(date)
        location_name = data['Location'][i]
        cyl = createCylinder(coords, str(date) + ', ' + location_name + ', ' + str(coords))

        # If a collection for this location does not exist, create it
        if location_name not in location_collections:
            location_collections[location_name] = new_collection(location_name, col)

        # Add the cylinder to the collection for this location
        location_collections[location_name].objects.link(cyl)
        bpy.context.collection.objects.unlink(cyl)

        # create text and make a child of cylinder
        if location_name not in labeled:
            text = createText(location_name, textLocation, textScale, cyl, tcol)
            
            keyframeVisible(text, date)
            keyframeInvisible(text, date - 1)
            labeled.append(location_name)

        # set visibility keyframes for both
        keyframeVisible(cyl, date)
        keyframeInvisible(cyl, date - 1)
        # set location keyframes for cylinder
        keyframeLocations(cyl, date)

def layout():
    col = new_collection("GridCollection")
    #creates a grid of lat long points (equirectangular projection)
    for latitude in range(-90, 100, 10):
        for longitude in range(-180, 190, 20):
            coords = equirectangularProjection(latitude, longitude)
            cyl = createCylinder(coords, str(latitude) + ', ' + str(longitude) + ' => ' + str(coords))

def new_collection(name, parent=None):
    # create a new collection
    col = bpy.data.collections.new(name)
    if parent:
        parent.children.link(col)
    else:
        bpy.context.scene.collection.children.link(col)
    bpy.context.view_layer.active_layer_collection = bpy.context.view_layer.layer_collection.children[-1]
    
    return col


layout()        
main()