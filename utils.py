import csv
import os
import math
from mathutils import Vector

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