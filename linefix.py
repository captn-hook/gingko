import bpy, bmesh
from mathutils import Vector
# for curve in collection: Scene Collection/A/NodeCollection/Lines
# get its related icon, which is the child of the first hook empty of the curve 
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

col = find_collection('Lines')

def midpoint3d(p1, p2, weight=.5):
    cntrwght = 1 - weight
    return (p1 * cntrwght) + (p2 * weight)

def deleteFrames(obj, keyList):
    for key in keyList:
        obj.keyframe_delete(data_path="location", frame=key)

def singleFrame(hook, frame):
    #set the scene to the frame, and delete all other keyframes, then keyframe the location
    bpy.context.scene.frame_set(frame)
    locationFcurve = hook.animation_data.action.fcurves.find('location')
    deleteFrames(hook, [key.co[0] for key in locationFcurve.keyframe_points])
    hook.keyframe_insert(data_path="location", frame=frame)

# in the console: 
# import linearCurveBevel as lb
# lb.adjust_linear_fcurve(C.object)
def main():
    for crv in col.objects:

        if "Line from End" in crv.name:
            continue

        # #some objects have two duplicate hooks? if so, remove one
        # crv.modifiers[1].strength = .8
        # crv.modifiers[2].strength = .5
        
        # #get the first hook modifier crv.modifiers[0].object
        hook = crv.modifiers[0].object
        
        icon = hook.children[0]
        rotationFcurve = icon.animation_data.action.fcurves.find('rotation_euler')
        if len(rotationFcurve.keyframe_points) > 2: 
            #delete frame 3, move frame 2 to its frame number
            fnum = int(rotationFcurve.keyframe_points[2].co[0])
            #remove
            rotationFcurve.keyframe_points.remove(rotationFcurve.keyframe_points[2])
            rotationFcurve.keyframe_points[1].co[0] = fnum
        # print(icon.name)
        # print(hook.name)
        
        #determine frame times by getting the first and last keyframe of the icon.hide_render property
        renderFcurve = icon.animation_data.action.fcurves.find('hide_render')
        startframe = int(renderFcurve.keyframe_points[0].co[0])
        endframe = int(renderFcurve.keyframe_points[-1].co[0])

        #add a follow path constraint to the icon
        fpc = icon.constraints.new('FOLLOW_PATH')
        fpc.target = crv

        #remove the icon's parent
        icon.parent = None

        # animate the path and its start mapping, get the bpy.data.curves object
        crvD = crv.data

        # crv.bevel_factor_start from 1 to 0
        crvD.bevel_factor_start = 1
        crvD.keyframe_insert(data_path="bevel_factor_start", frame=startframe)

        crvD.bevel_factor_start = 0
        crvD.keyframe_insert(data_path="bevel_factor_start", frame=endframe)

        # crv.use_path = True
        crvD.use_path = True

        # crv.eval_time from 100% to 0%
        crvD.path_duration = 1

        crvD.eval_time = 1
        crvD.keyframe_insert(data_path="eval_time", frame=startframe)

        crvD.eval_time = 0
        crvD.keyframe_insert(data_path="eval_time", frame=endframe)



        #delete the hook keyframes
        for hookmod in crv.modifiers:
            hook = hookmod.object
            #mergeTo1Frame(hook)
            singleFrame(hook, int(endframe - (endframe - startframe)/5))

            #apply the hook modifier
            crv.select_set(True)
            bpy.context.view_layer.objects.active = crv

            bpy.ops.object.modifier_apply(modifier=hookmod.name)

            bpy.ops.object.select_all(action='DESELECT')

main()

# #set the frame to the end of the animation
# bpy.context.scene.frame_set(bpy.context.scene.frame_end)
# #refresh blender
# bpy.ops.wm.redraw_timer(type='DRAW_WIN_SWAP', iterations=1)
# for crv in col.objects:
#     if "Line from End" in crv.name:
#           continue
#     #deselct all objects
#     bpy.ops.object.select_all(action='DESELECT')
#     #select the curve
#     crv.select_set(True)
#     #set the curve to active
#     bpy.context.view_layer.objects.active = crv
#     #adjust the fcurve
#     adjust_linear_fcurve(crv)
