import bpy

#get the root collection
root_coll = bpy.context.scene.collection.children[0]
#for every collection in the root collection
for coll in root_coll.children:
    #merge the objects in that collection into one object
    if len(coll.objects) > 1:
        bpy.ops.object.select_all(action='DESELECT')
        for obj in coll.objects:
            obj.select_set(True)
        #set active object to the first object in the collection
        bpy.context.view_layer.objects.active = coll.objects[0]
        bpy.ops.object.join()