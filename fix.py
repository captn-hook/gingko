import bpy
import csv
import math
from mathutils import Matrix

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

def sphericalProjection(lat, lon, radius=100):
    # Convert latitude and longitude into radians
    lat_rad = math.radians(90 - lat) # convert from latitude to inclination (theta)
    lon_rad = math.radians(lon)

    # Convert lat/lon (spherical coordinates) to cartesian coordinates
    x = radius * math.sin(lat_rad) * math.cos(lon_rad)
    y = radius * math.sin(lat_rad) * math.sin(lon_rad)
    z = radius * math.cos(lat_rad)

    return (x, y, z)

data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output.tsv")

# # loop through the selection list
# for obj in bpy.context.selected_objects:
#     # get the object's name
#     name = obj.name
#     print(name)
#     # get its lat and long from data by name
#     try:
#         i = data['Location'].index(name)
#         print("no location for", name)
#     except ValueError:      
#         continue

#     lat = float(data['Latitude'][i])
#     lon = float(data['Longitude'][i])
#     xyz = sphericalProjection(lat, lon)

#     # set the object's origin

#     mw = obj.matrix_world
#     imw = mw.inverted()
#     me = obj.data
#     #convert xyz to a matrix
#     origin = Matrix.Translation(tuple(xyz))
#     local_origin = imw @ origin
#     neg_local_origin = [-x for x in local_origin]
#     me.transform(Matrix.Translation(neg_local_origin))
#     mw.translation += (origin - mw.translation)

#get the active object
obj = bpy.context.active_object
#get its name
name = obj.name
#get its lat and long from data by name
i = data['Location'].index(name)
lat = float(data['Latitude'][i])
lon = float(data['Longitude'][i])
xyz = sphericalProjection(lat, lon)

#set the 3d cursor to the xyz
bpy.context.scene.cursor.location = xyz