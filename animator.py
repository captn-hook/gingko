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

data = getData(path + "\\v2.tsv")

textScale = [2, 2, 2]
textLocation = [.9, 2, .4]
initialZ = .9
finalZ = 1.1
step = 40
frame_start = 1
sphereRadius = 100

cam_zoom_out = 1.04
#hex color defaults
land_fresh = "#0E0E1D"
land = "#353542"
water = "#41414F"

def keyframeCam(obj, cam, frame, location, camheight, still=False):
    # Get the target rotation
    target_quat = sphereQuat(location)

    # If the dot product is negative, negate the target quaternion
    if obj.rotation_quaternion.dot(target_quat) < 0:
        target_quat = -target_quat

    # Set the rotation and keyframe it
    obj.rotation_quaternion = target_quat
    obj.keyframe_insert(data_path="rotation_quaternion", frame=frame - step / 10)
    obj.keyframe_insert(data_path="rotation_quaternion", frame=frame + step / 2)
    #if perspective, set the cam orbit distance
    if not still:
        if cam.type == 'PERSP':
            # set the cam orbit distance
            cam.location = camheight
            cam.keyframe_insert(data_path="location", frame=frame)
            cam.location = camheight * cam_zoom_out
            cam.keyframe_insert(data_path="location", frame=frame + step / 2)
        else:
            #set ortho scale bpy.data.cameras["Camera.002"].ortho_scale
            cam.data.ortho_scale = sphereRadius
            cam.data.keyframe_insert(data_path="ortho_scale", frame=frame)
            cam.data.ortho_scale = sphereRadius * cam_zoom_out
            cam.data.keyframe_insert(data_path="ortho_scale", frame=frame + step / 2)

    return obj, target_quat

def createText(string, location, scale, parent, col):
    # create text
    text = bpy.data.curves.new(type="FONT", name="Text")
    text.body = string
    text.align_x = 'CENTER'
    text.align_y = 'CENTER'
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
    obj.keyframe_insert(data_path="location", frame=(frame))
    return obj

def keyframeLocations(obj, frame):
    # set keyframe to current location at frame
    obj.keyframe_insert(data_path="location", frame=frame)
    # get the normal vector of the sphere at the location
    normal = sphereNormal(obj.location)
    # move the object in the normal direction by finalZ
    obj.location = obj.location + normal * finalZ
    # set keyframe at finalZ at frame + zSlideFrames
    obj.keyframe_insert(data_path="location", frame=(frame + step / 2))
    return obj


def createLine(location, name, parent=None, collection=None, h1col=None, h2col=None):
    # Create a new curve
    curve = bpy.data.curves.new(name, type='CURVE')
    curve.dimensions = '3D'
    curve.resolution_u = 6

    # Create a new object associated with the curve
    obj = bpy.data.objects.new(name, curve)

    # Set the parent object
    if parent is not None:
        obj.parent = parent
    else:
        obj.location = location

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
    if h1col is not None:
        h1col.objects.link(h1)

    if h2col is not None:
        h2col.objects.link(h2)

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

def keyframeLineSecond(h1, h2, frame, location, old):
    #and h2 to the midpoint + some normal, in order to make an arc
    #location and midpoint are world space, convert to local space with the handle's parent
    #first make 4d vectors instead of 3d
    if h1.parent is not None:
        location = Vector((location[0], location[1], location[2], 1))
        #convert to local space
        location = h1.matrix_world.inverted() @ location
        #set the location
        location = Vector((location[0], location[1], location[2]))
    
    mid = spherical_midpoint_from_cartesian(location, Vector(old))
    h1.location = mid
    h1.keyframe_insert(data_path="location", frame=frame - step)

    #add some theta to h2 frame - step
    r = mid.length
    theta = math.acos(mid.z / r)
    phi = math.atan2(mid.y, mid.x)
    theta -= math.pi / 12
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)

    modifiedlocation = Vector((x, y, z)) * .2 + Vector(mid) * .4 + Vector(old) * .4

    h1.location = modifiedlocation
    h1.keyframe_insert(data_path="location", frame=frame - step * 2)

    h1.location = Vector(location)
    h2.location = Vector(location)
    #and set the rotation
    h1.keyframe_insert(data_path="location", frame=frame + step)
    h2.keyframe_insert(data_path="location", frame=frame)

    return h1, h2

def keyframeLineThird(h1, h2, frame, location):
    #similar to the second keyframe, but not as far above the ground
    if h1.parent is not None:
        location = Vector((location[0], location[1], location[2], 1))
        location = h1.matrix_world.inverted() @ location
        location = Vector((location[0], location[1], location[2]))
    
    h1.location = h1.location * .9
    h2.location = Vector(location)
    h1.keyframe_insert(data_path="location", frame=frame + step)
    h2.keyframe_insert(data_path="location", frame=frame)

def keyframeLineThickness(obj, frame, thickness):
    #set keyframe for bevel depth
    obj.data.bevel_depth = thickness
    obj.data.keyframe_insert(data_path="bevel_depth", frame=frame)
    return obj

# def hexToRGBA(hex):
#     #convert hex to RGB
#     hex = hex.lstrip('#')
#     hex = tuple(int(hex[i:i+2], 16) / 255 for i in (0, 2, 4))
#     # A = 1
#     return (hex[0], hex[1], hex[2], 1)

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
    mix = nodes.new(type='ShaderNodeMixShader')
    #connect the mix shader to the material output
    output = nodes.new(type='ShaderNodeOutputMaterial')
    mat.node_tree.links.new(mix.outputs[0], output.inputs[0])
    #set the mix shader to 1
    mix.inputs[0].default_value = 1
    # Create a new rgb node
    rgb = nodes.new(type='ShaderNodeRGB')
    rgb.outputs[0].default_value = hex_to_rgb(stringtohex(color))
    # Connect the rgb node to the mix shader
    mat.node_tree.links.new(rgb.outputs[0], mix.inputs[2])
    # create a new transparent shader
    transparent = nodes.new(type='ShaderNodeBsdfTransparent')
    # Connect the transparent shader to the mix shader
    mat.node_tree.links.new(transparent.outputs[0], mix.inputs[1])
    #return the material
    return mat

def fade_material(obj, color, frame):
    # creates a new material with keyframes
    # similar to simple_material, but alpha blend set to hash and keyframed

    mat = simple_material(obj, color)
    mat.blend_method = 'HASHED'

    mix = [node for node in mat.node_tree.nodes if node.type == 'MIX_SHADER'][0]

    #set the alpha to 0 at frame
    mix.inputs[0].default_value = 0
    mix.inputs[0].keyframe_insert(data_path="default_value", frame=frame)
    #set the alpha to 1 at frame + step / 4
    mix.inputs[0].default_value = 1
    mix.inputs[0].keyframe_insert(data_path="default_value", frame=frame + step / 4)
    #hold to frame + step / 4 * 3
    mix.inputs[0].keyframe_insert(data_path="default_value", frame=frame + step)
    #fade back to 0 at frame + step
    mix.inputs[0].default_value = 0
    mix.inputs[0].keyframe_insert(data_path="default_value", frame=frame + step + step / 4 * 3)

def create_fade_material(obj, color):
    # creates a new material without keyframes

    mat = simple_material(obj, color)
    mat.blend_method = 'HASHED'

    mix = [node for node in mat.node_tree.nodes if node.type == 'MIX_SHADER'][0]

    return mat, mix

def find_material(obj):
    #find if we have already created a material of this color
    for mat in bpy.data.materials:
        if mat.name == obj.name + "Material":
            return mat
    return None

def main(cameraEmpty, cam):
    cam_origin = cam.location
    #collection for these objects
    if "NodeCollection" in bpy.data.collections:
        col = bpy.data.collections["NodeCollection"]
    else:
        col = new_collection("NodeCollection")

    lcol = new_collection("Lines", col)
    lh1 = new_collection("LineHandles1", lcol)
    lh2 = new_collection("LineHandles2", lcol)
    tcol = new_collection("StrainText", col)
    ccol = new_collection("Cities", col)
    pcol = new_collection("Planes", col)
    
    labeled = {} # Dictionary to store labeled locations
    # saved_mats = {} # Dictionary to store materials for each location
    location_collections = {}  # Dictionary to store collections for each location
    frame_counter = frame_start  # Start the frame counter at 0
    last_line = None  # Lines take into account the location of the NEXT node
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
            stack_list.append(lineage)
            continue

        #extend out timings if we are moving a lot
        if last_line is not None:
            dist = latlon_dist(latlon, last_line[2])
            max = 13329.7
            frame_counter += dist / max

        # if i + 1 < len(data['Date']) and data['Country'][i + 1] != country:
        #     #if we are moving to a new location, increment the frame counter
        #     frame_counter += 1.5

        frame = frame_counter * step

        # coords = equirectangularProjection(location[0], location[1])
        coords = sphericalProjection(latlon[0], latlon[1])

        if country + "Nodes" not in location_collections:
            #check if the collection exists in NodeCollection
            if country + "Nodes" in bpy.data.collections:
                location_collections[country] = bpy.data.collections[country + "Nodes"]
            else:
                location_collections[country] = new_collection(country + "Nodes", col)

        # spawn the cylinder in the globe by initial z 
        backup = (1 - initialZ) * sphereNormal(coords)
        coordsback = Vector(coords) - backup
        cyl = createCylinder(coordsback, str(frame) + ', ' + country + ', ' + str(coords), collection=location_collections[country])

        line, h1, h2 = createLine(coords, "Line from " + country + " at " + str(frame), None, lcol, lh1, lh2)
        # h1 and h2 are the handles of the line for animation, and one point of the line is always at coords
        #create text child of h1 with Lineage

        #create plane icon child of h1
        plane = getPlaneIcon(parent=h1, collection=pcol)
        #the label for the plane
        zero = (0, 2, 0)
        one = (4, 4, 4)

        #check the stack
        tt = lineage
        tt = lineage
        if len(stack_list) >= 1:
            # append a ' / ' spacer between lineage and the first element of stack_list
            tt += " / "
            # append all the stack to this label, adding a / between two on the same line and a newline between every two
            for i, stack_label in enumerate(stack_list):
                # add a new line for every two elements
                if i % 2 == 0 and i != 0:
                    tt += "\n"
                # add spacer between elements on the same line
                if i % 2 == 1 and i != 0:
                    tt += " / "
                tt += stack_label

            stack_list = []

        texte = createText(tt, zero, one, plane, tcol)
        texte.location = texte.location + Vector((0, texte.dimensions[0] * 2, 0))
        # add damped track constraint to cam, z+ to cam
        # texte.constraints.new('DAMPED_TRACK')
        # texte.constraints['Damped Track'].target = cam
        # texte.constraints['Damped Track'].track_axis = 'TRACK_Z'
        # for ortho, add copy rotation to cam, z+ to cam
        texte.constraints.new('COPY_ROTATION')
        texte.constraints['Copy Rotation'].target = cam

        #set plane and text to fade in and out
        fade_material(plane, "EEEEEE", frame)
        fade_material(texte, "FFFFFF", frame)

        #set the color
        simple_material(line, "DDDDDD")
        
        keyframeVisible(texte, frame)
        keyframeInvisible(texte, frame - 1)
        keyframeInvisible(texte, frame + step * 2, False)
        keyframeVisible(plane, frame)
        keyframeInvisible(plane, frame - 1)
        keyframeInvisible(plane, frame + step * 2, False)

        mapcol = find_collection(country)
        if mapcol is None:
            print("No collection found for " + country)
        else:
            #get the first object in the collection
            countrymap = mapcol.objects[0]
            #get the material
            mat = countrymap.data.materials[0]
            #find name of node labeled 'ActiveColor'
            ActiveColor = [node.name for node in mat.node_tree.nodes if node.label == 'ActiveColor'][0] #color of the center
            LandC = [node.name for node in mat.node_tree.nodes if node.label == 'LandC'][0] #mix between two bg colors
            LandO = [node.name for node in mat.node_tree.nodes if node.label == 'Land'][0] #bg color 1
            LandColor = [node.name for node in mat.node_tree.nodes if node.label == 'LandA'][0] #bg color 2
            StrainC = [node.name for node in mat.node_tree.nodes if node.label == 'StrainC'][0] #mix between fg (inner) and bg (outer) color

            #keyframe the radial gradient
            
            #the general idea is we have a bg color, outerGradColor, and a fg color, innerGradColor
            # we can expand a radial gradient by transitioning gradientMix from 1 (outer) to 0 (inner) while they are different colors
            # and then set the bg to the fg color and while they are the same color, transition gradientMix from 0 to 1 to hide the gradient
            # so we need to keyframe the gradientMix from 1 to 0 and back to 1

            innerGradColor = mat.node_tree.nodes[ActiveColor].outputs[0] # inner
            landC = mat.node_tree.nodes[LandC].outputs[0] # mix between two bg colors
            landO = mat.node_tree.nodes[LandO].outputs[0] # bg color 1
            outerGradColor = mat.node_tree.nodes[LandColor].outputs[0] # bg color 2
            gradientMix = mat.node_tree.nodes[StrainC].outputs[0] # mix between fg (inner) and bg (outer) color

            if country in labeled: #been here before, want to transition from last color
                outerGradColor.default_value = hex_to_rgb(stringtohex(labeled[country][2])) # the last color of this location

            else: #do first time setup, want to transition from land color
                outerGradColor.default_value = hex_to_rgb(stringtohex(land.strip('#')))

                #transition land c frm 0 to 1 while the grad is full
                landC.default_value = 0
                landC.keyframe_insert(data_path="default_value", frame=frame - step / 4)

                landO.default_value = hex_to_rgb(stringtohex(land_fresh.strip('#')))
                landO.keyframe_insert(data_path="default_value", frame=frame)
                landO.default_value = hex_to_rgb(stringtohex(land.strip('#')))
                landO.keyframe_insert(data_path="default_value", frame=frame + step / 4)

            outerGradColor.keyframe_insert(data_path="default_value", frame=frame)

            #set the inner radial gradient color to the color of this strain
            innerGradColor.default_value = hex_to_rgb(stringtohex(color))
            innerGradColor.keyframe_insert(data_path="default_value", frame=frame - step / 2 + 1)
            innerGradColor.keyframe_insert(data_path="default_value", frame=frame + step / 2 - 1) # we transition the inner grad color almost immediately

            gradientMix.default_value = 1
            gradientMix.keyframe_insert(data_path="default_value", frame=frame - step / 2 + 1)
            gradientMix.keyframe_insert(data_path="default_value", frame=frame + step / 2 - 1) # while the inner grad color is transitioning

            gradientMix.default_value = 0
            gradientMix.keyframe_insert(data_path="default_value", frame=frame)
            gradientMix.keyframe_insert(data_path="default_value", frame=frame + step / 4) #hold for a bit

            #and set the outer radial gradient color to the color of this strain while the grad is fully expanded
            outerGradColor.default_value = hex_to_rgb(stringtohex(color))
            outerGradColor.keyframe_insert(data_path="default_value", frame=frame + step / 4)

            
            landC.default_value = 1
            landC.keyframe_insert(data_path="default_value", frame=frame)
            if i + 1 < len(data['Date']) and data['Country'][i + 1] != country:
                landC.keyframe_insert(data_path="default_value", frame=frame + step / 4) #hold for a bit
                landC.default_value = .4
                landC.keyframe_insert(data_path="default_value", frame=frame + step - 1) #fade out
                                      
            # create text and make a child of cylinder CITY LABEL
            if country not in labeled: # FIRST +=111111111111111111111111111111111111111111111=+
                #first time we've seen this location
                text = createText(country, textLocation, textScale, cyl, ccol)
                # create a new material for the text, white
                tmat, node = create_fade_material(text, "FFFFFF") 

                text.data.materials.append(tmat)
    
                #keyframe the node default value alpha
                #keyframeVisible(text, frame)
                alpha = node.inputs[0]
                alpha.default_value = 1
                alpha.keyframe_insert(data_path="default_value", frame=frame + step / 4) # 100% visible from frame + 1/4 to frame + 3/4
                alpha.keyframe_insert(data_path="default_value", frame=frame + step / 4 * 3)

                #keyframeInvisible(text, frame - 1)  
                alpha.default_value = 0
                alpha.keyframe_insert(data_path="default_value", frame=frame) # and 0% visible at spawn
                
                labeled[country] = (text, node, color)

            #check if this is already visible because it was the last location
            elif i - 1 >= 0 and last_line and last_line[3] != country:
            #data['Country'][i - 1] != country:  # REFRESH A LOCATION -=================------------------------------------------
                #we've seen this location before it is invisible
                text, node, _ = labeled[country]
                #keyframeVisible(text, frame)
                #fade in
                alpha = node.inputs[0]
                alpha.default_value = 1
                alpha.keyframe_insert(data_path="default_value", frame=frame + step / 4)
                alpha.keyframe_insert(data_path="default_value", frame=frame + step / 4 * 3)
    
                alpha.default_value = 0
                alpha.keyframe_insert(data_path="default_value", frame=frame)

            else: # 2 IN A ROW -=================------------------------------------------
                #we've seen this location before and it is visible
                text, node, _ = labeled[country]
                #hold the opacity
                alpha = node.inputs[0]
                alpha.keyframe_insert(data_path="default_value", frame=frame + step / 4 * 3)

            # check if the next location is the same as this one for the fade out
            if i + 1 < len(data['Date']) and data['Country'][i + 1] == country:
                alpha.default_value = 1
                alpha.keyframe_insert(data_path="default_value", frame=frame + step / 4 * 3)
            else:
                #visibility
                #keyframeInvisible(text, frame + step, False)
                #fade out
                alpha.default_value = 0
                alpha.keyframe_insert(data_path="default_value", frame=frame + step)


            # set visibility keyframes for both
            keyframeVisible(cyl, frame)
            keyframeInvisible(cyl, frame - 1)
            # set location keyframes for cylinder
            keyframeLocations(cyl, frame)
            still =i + 1 < len(data['Date']) and data['Country'][i + 1] == country
            empt, target_quat = keyframeCam(cameraEmpty, cam, frame + step / 5, coords, cam_origin, still)
            
            #line keyframes
            keyframeVisible(line, frame)
            keyframeInvisible(line, frame - 1)
            keyframeInvisible(line, (frame_counter + 2) * step, False)
            keyframeLineThickness(line, frame - step / 2, .3)
            keyframeLineThickness(line, frame + step / 2, .15)
            keyframeLineThickness(line, frame + step * 1.5, 0)
            
            keyframeLineFirst(h1, h2, frame)

        if last_line is not None:
            # get a target lat lon
            last_point = sphericalProjection(last_line[2][0], last_line[2][1])
            half, target = targ(last_point)

            # rotate the plane on local z to face the target
            rotate_plane_to_target(last_line[5], last_point, half, last_line[4])
            
       
            last_line[0].name = "H1 from " + last_line[3] + " at " + str(last_line[4])
            last_line[1].name = "H2 from " + last_line[3] + " at " + str(last_line[4])
            keyframeLineSecond(last_line[1], last_line[0], frame + step * 3, half, last_point)
            keyframeLineThird(last_line[1], last_line[0], frame + step * 4, target)

        last_line = (h1, h2, latlon, country, frame, plane, texte)

        if country != "End":
            labeled[country] = (labeled[country][0], labeled[country][1], color)

        frame_counter += 1  # Increment the frame counter

def set_loc_rotation(obj, value):  
    rot = Euler(value, 'ZYX')
    obj.rotation_euler = (obj.rotation_euler.to_matrix() @ rot.to_matrix()).to_euler(obj.rotation_mode)

def rotate_plane_to_target(plane, current, target, frame):
    # local z+ is the top down view of the plane, so we want that to align with the sphere normal
    # local y+ is the front of the plane, so we want point to the target
    # (current - target) is the vector from the current to the target
    # Calculate the direction vector from the current location to the target
    direction = target - Vector(current)
    # Calculate the sphere's normal at the current location
    normal = sphereNormal(current)
    # Calculate the cross product of the direction and the normal to get the plane's local X+ axis
    plane_x = direction.cross(normal)
    # Normalize the plane's local X+ axis
    plane_x = plane_x.normalized()
    # Calculate the cross product of the plane's local X+ axis and the direction to get the plane's local Z+ axis
    plane_z = plane_x.cross(direction)
    # Normalize the plane's local Z+ axis
    plane_z = plane_z.normalized()
    # Create a rotation matrix from the plane's local axes
    rotation_matrix = Matrix((plane_x, direction, plane_z)).transposed()
    # Convert the rotation matrix to Euler angles
    rotation_euler = rotation_matrix.to_euler('ZYX')
    # Set the plane's rotation
    set_loc_rotation(plane, rotation_euler)
    #keyframe the rotation
    #rotate the plane by 15 degrees towards the south
    
    plane.keyframe_insert(data_path="rotation_euler", frame=frame)
    posneg = -1 if plane.rotation_euler.y > 0 else 1
    set_loc_rotation(plane, (0, 0, math.radians(15 * posneg)))
    # plane.keyframe_insert(data_path="rotation_euler", frame=frame + step / 3 * 2)
    set_loc_rotation(plane, (0, 0, math.radians(5 * posneg * -1)))
    plane.keyframe_insert(data_path="rotation_euler", frame=frame + step * 2)
    #also move it out along sphere normal by 1
    plane.location = plane.location + normal * 1.3
    

def layout():
    new_collection("GridsCollection")
    #creates a grid of lat long points (equirectangular projection)
    for latitude in range(-90, 100, 10):
        for longitude in range(-180, 190, 20):
            #coords = equirectangularProjection(latitude, longitude)
            coords = sphericalProjection(latitude, longitude)
            createCylinder(coords, str(latitude) + ', ' + str(longitude) + ' => ' + str(coords))


def get_target(normal):
    # Convert the normal vector to spherical coordinates
    r = normal.length
    theta = math.acos(normal.z / r)
    phi = math.atan2(normal.y, normal.x)

    # rotate about the north/south pole by 90 degrees
    phi += math.pi / 2 * random.choice([-1, 1])

    # set the latitude to approximately the equator
    shift = - math.pi / 12
    range = math.pi / 12
    theta = random.uniform(math.pi / 2 - range + shift, math.pi / 2 + range + shift)

    # Convert the spherical coordinates back to a normal vector
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)

    return Vector((x, y, z)).normalized() * sphereRadius

def targ(coords):
    normal = sphereNormal(coords)

    target = get_target(normal)

    mid = spherical_midpoint_from_cartesian(Vector(coords), Vector(target))
    # add a little theta to the midpoint so that the line arcs towards north
    r = mid.length
    theta = math.acos(mid.z / r)
    phi = math.atan2(mid.y, mid.x)

    # add ~15 degrees to latitude
    theta += math.pi / 12

    # Convert the spherical coordinates back to a normal vector
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)

    finalZ = 1.5
    mid = Vector((x, y, z)).normalized() * sphereRadius

    return mid * (finalZ * 1.5), target * finalZ

def test():
    col = new_collection("TestCollection")
    #test the target function
    #choose a random location
    i = random.randint(0, len(data['Date']) - 1)
    coords = (float(data['Latitude'][i]), float(data['Longitude'][i]))
    coords = sphericalProjection(coords[0], coords[1])

    #create a line
    line, h1, h2 = createLine(coords, "test", None, col)
    keyframeLineFirst(h1, h2, 1)

    #get a target
    half, target = targ(coords)

    #create cylinders at the points
    createCylinder(coords, "coords", None, col)
    createCylinder(half, "half", None, col)
    createCylinder(target, "target", None, col)

    #animate the line
    keyframeLineSecond(h2, h1, 2 * step, half, coords)
    keyframeLineThird(h2, h1, 3 * step, target)

camE, cam = createCamera(sphereRadius)
# # layout()        
main(camE, cam)
#test()