import csv
import os
import math
from math import sin, cos, acos, asin
from mathutils import Vector

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

    stupid2 = False #if the data is in the wrong order
    if stupid2 == True:
        # convert dstring to integers
        data[dstring] = list(map(int, data[dstring]))
        # order the data by dstring column
        data_pairs = list(zip(data[dstring], *[data[h] for h in headers if h != dstring]))
        data_pairs.sort()
        data[dstring], *other_data = zip(*data_pairs)
        for i, h in enumerate(headers):
            if h != dstring:
                data[h] = other_data[i-1]

        print(data[dstring])

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
    # Convert latitude and longitude from degrees to radians
    lat1, lon1 = math.radians(latlon1[0]), math.radians(latlon1[1])
    lat2, lon2 = math.radians(latlon2[0]), math.radians(latlon2[1])

    # Radius of the Earth in kilometers
    R = 6371.0

    # Differences in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # Haversine formula
    a = math.sin(dlat / 2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    distance = R * c
    return distance

def distance(p1, p2):
    #returns the distance between two 3d points
    return math.sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2 + (p1[2] - p2[2])**2)

def sphereNormal(location1, location2=(0, 0, 0)):
    #returns the normal vector of the surface point 1 of a sphere at point 2
    return (Vector(location1) - Vector(location2)).normalized()

def sphereRotation(location):
    #returns the x, y, z euler of a normal vector
    normal = sphereNormal(location)
    return normal.to_track_quat('Z', 'Y').to_euler()

def sphereQuat(location):
    #returns the quaternion of a normal vector
    normal = sphereNormal(location)
    return normal.to_track_quat('Z', 'Y')

def midpoint(p1, p2):
    #returns the midpoint of two 3d points
    return ((p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2, (p1[2] + p2[2]) / 2)

def cartesian_to_spherical(x, y, z):
    r = math.sqrt(x**2 + y**2 + z**2)
    theta = math.acos(z/r)
    phi = math.atan2(y, x)
    return r, theta, phi

def spherical_to_cartesian(r, theta, phi):
    x = r * math.sin(theta) * math.cos(phi)
    y = r * math.sin(theta) * math.sin(phi)
    z = r * math.cos(theta)
    return x, y, z

def spherical_midpoint_from_cartesian(p0, p1):
    p0 = Vector(p0)
    p1 = Vector(p1)
    r1 = p0.length
    r2 = p1.length
    r = (r1 + r2) / 2

    point = midpoint(p0, p1)
    point = Vector(point)
    return point.normalized() * r
    

def spherical_midpoint(p0, p1):
    """Calculate the midpoint along the sphere's surface."""
    return slerp(p0, p1, 0.5)

def slerp(p0, p1, t):
    """Spherical linear interpolation."""
    dot_product = p0.dot(p1) / (p0.length * p1.length)
    clamped_value = max(min(dot_product, 1), -1)  # Clamp the value to the range -1 to 1
    omega = math.acos(clamped_value)
    so = math.sin(omega)
    return math.sin((1.0-t) * omega) / so * p0 + math.sin(t * omega) / so * p1

def fixStupid():
    #fixes the stupid data by turning Date into sequential integers
    data = getData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output_with_colors4.tsv")

    for i in range(len(data[dstring])):
        data[dstring][i] = i

    #save to new file
    with open("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\output_with_colors4.tsv", 'w', newline='') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow([dstring] + [h for h in data if h != dstring])
        for i in range(len(data[dstring])):
            # Strip newline characters from data before writing
            row = [str(data[dstring][i]).strip('\n')] + [str(data[h][i]).strip('\n') for h in data if h != dstring]
            writer.writerow(row)

fixStupid()