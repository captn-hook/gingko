import bpy 

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

for crv in col.objects:

    #some objects have two duplicate hooks? if so, remove one
    crv.modifiers[1].strength = .8
    crv.modifiers[2].strength = .5
    
    #get the first hook modifier crv.modifiers[0].object
    hook = crv.modifiers[0].object
    
    icon = hook.children[0]

    print(icon.name)
    print(hook.name)
    
    #determine frame times by getting the first and last keyframe of the icon.hide_render property
    startframe = icon.animation_data.action.fcurves[0].keyframe_points[0].co[0]
    endframe = icon.animation_data.action.fcurves[0].keyframe_points[-1].co[0]

    #add a follow path constraint to the icon
    fpc = icon.constraints.new('FOLLOW_PATH')
    fpc.target = crv

    #remove the icon's parent
    icon.parent = None

    #animate the path and its start mapping, get the bpy.data.curves object
    crv = crv.data
    #crv.bevel_factor_start from 1 to 0
    crv.bevel_factor_start = 1
    crv.keyframe_insert(data_path="bevel_factor_start", frame=startframe)
    crv.bevel_factor_start = 0
    crv.keyframe_insert(data_path="bevel_factor_start", frame=endframe)

    #crv.use_path = True
    crv.use_path = True

    #crv.eval_time from 100% to 0
    duration = int(endframe - startframe)
    crv.path_duration = duration
    crv.eval_time = duration
    crv.keyframe_insert(data_path="eval_time", frame=startframe)
    crv.eval_time = 0
    crv.keyframe_insert(data_path="eval_time", frame=endframe)