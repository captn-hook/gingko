import bpy 
import csv
import sys

dstring = 'Date'

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

    stupid = False #dstring does not take into account the year, and data is already in chronological order so its redundant
    if stupid == True:
        # Convert dstring to integers
        data[dstring] = list(map(int, data[dstring]))

        # Pair each dstring with its corresponding data row
        data_pairs = list(zip(data[dstring], *[data[h] for h in headers if h != dstring]))

        # Sort these pairs
        data_pairs.sort()

        # Unzip them back into separate lists
        data[dstring], *other_data = zip(*data_pairs)

        # Assign the sorted data back to their respective keys
        for i, h in enumerate(headers):
            if h != dstring:
                data[h] = other_data[i-1]

    return data


path = bpy.data.filepath.split("\\")
path = "\\".join(path[:-1])
sys.path.append(path)

data = getData(path + "\\output_with_colors3.tsv")

# get the selected collection
selected_collection = bpy.context.collection

# get the names of the objects in the collection
object_names = [o.name for o in selected_collection.objects]

# check if every object in the data "Country" column is in the object names
for country in data["Country"]:
    if country not in object_names:
        print(f"{country} not found in collection")

        # check if the object is in the scene

        if bpy.data.objects.get(country) is not None:
            print(f"{country} is in the scene")
            # select the object
            bpy.data.objects[country].select_set(True)
            # set the active object
            bpy.context.view_layer.objects.active = bpy.data.objects[country]

