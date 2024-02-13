import bpy
import os

def getData(path):
    sep = '\t'
    data = {}
    with open(path, 'r') as f:
        headers = f.readline().strip().split(sep)
        for header in headers:
            data[header] = []
        for line in f:
            line = line.strip().split(sep)
            for i in range(len(headers)):
                data[headers[i]].append(line[i])

    return data

def ls(path):
    return os.listdir(path)

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output.tsv")
for key in data:
    print(key, len(data[key]))
# print headers // should be Collection date	Region	Country	State	City	County	Airport	Latitude	Longitude
# collection date is an integer from 0 to n

# for each row in the data, create a new cylinder at the lat and long
# and set keygrames for the cylinder to appear at the collection date, aswell as animated from z = 0 to z = -1 over some period (to make it fade into the ground)
# and create a text label as a child of the cylinder with the location name

textScale = [1, 1, 1]
textLocation = [.5, .5, 1]
textZ = 1
cylinderScale = [1, .1] #radius, height
initialZ = 0
finalZ = -1
zSlideFrames = 10

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

def createCylinder(location):
    # create 
    cyl = bpy.ops.mesh.primitive_cylinder_add(vertices=32, radius=cylinderScale[0], depth=cylinderScale[1], location=(location[0], location[1], initialZ))
    cyl = bpy.context.object
    return cyl

def createText(string, location, scale):
    # create text
    text = bpy.data.curves.new(type="FONT", name="Text")
    text.body = string
    textObj = bpy.data.objects.new("Text", text)
    bpy.context.collection.objects.link(textObj)

    textObj.location = location
    textObj.scale = scale

    return textObj

def keyframeLocations(obj, frame):
    #set keyframe at 0 at frame
    obj.location = (obj.location[0], obj.location[1], initialZ)
    obj.keyframe_insert(data_path="location", frame=frame)
    #set keyframe at finalZ at frame + zSlideFrames
    obj.location = (obj.location[0], obj.location[1], finalZ)
    obj.keyframe_insert(data_path="location", frame=frame + zSlideFrames)
    return obj

def main():
    for i in range(len(data['Collection date'])):
        # create cylinder
        location = (data['Longitude'][i], data['Latitude'][i])
        location = (float(location[0]), float(location[1]), 0)
        date = data['Collection date'][i]
        date = int(date)
        cyl = createCylinder(location)
        # create text and make a child of cylinder
        text = createText(data['Airport'][i], location, textScale)
        text.parent = cyl
        #unlink text from scene root so it is only a child of the cylinder
        bpy.context.collection.objects.unlink(text)
        # set visibility keyframes for both
        keyframeVisible(cyl, date)
        keyframeVisible(text, date)
        keyframeInvisible(cyl, date - 1)
        keyframeInvisible(text, date - 1)
        # set location keyframes for cylinder
        keyframeLocations(cyl, date)
        
main()