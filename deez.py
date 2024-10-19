import bpy
# get the selected collection
collection = bpy.context.collection

# for every subcollection in the collection
for subcollection in collection.children:
    # if the subcollection is empty
    if not subcollection.objects:
        print(f"{subcollection.name} is empty")

        # if an object with the same name as the subcollection is in the scene
        if bpy.data.objects.get(subcollection.name) is not None:
            # link the object to the subcollection
            subcollection.objects.link(bpy.data.objects[subcollection.name])
            print(f"{subcollection.name} linked")