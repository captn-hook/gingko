import bpy
import bmesh
import geopandas as gpd
from utils import sphericalProjection
from bpyutils import new_collection

def countryData(path):
    data = gpd.read_file(path, engine='pyogrio', use_arrow=True, layer='ADM_0')
    return data

def plot_country_meshes(data):
    if "CountryCollection" in bpy.data.collections:
        countriescol = bpy.data.collections["CountryCollection"]
    else:
        countriescol = new_collection("CountryCollection")

    for index, row in data.iterrows():
        country_name = row['COUNTRY']
        print(f"Plotting {country_name}... {index}/{len(data)}")
        print(f"{index/len(data)*100:.2f}% complete")

        countrycol = new_collection(country_name, countriescol)

        multipolygon = row['geometry'].geoms
        #sort by area
        sortedMultipolygons = sorted(multipolygon, key=lambda x: x.area, reverse=True)

        for polygon in sortedMultipolygons:
            # Create a new mesh
            mesh = bpy.data.meshes.new(country_name)

            # Create a new object associated with the mesh
            obj = bpy.data.objects.new(country_name, mesh)

            # Link the new object to the collection
            countrycol.objects.link(obj)

            #bmesh
            bm = bmesh.new()        

            polygon = polygon.simplify(0.05, preserve_topology=True)

            for vertex in polygon.exterior.coords:
                xyz = sphericalProjection(vertex[1], vertex[0])
                bm.verts.new(xyz)

            bm.verts.ensure_lookup_table()
            bm.verts.index_update()
            bm.faces.new(bm.verts)

            bm.to_mesh(mesh)
            bm.free()

    return countriescol


cData = countryData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\gadm_410-levels.gpkg")

plot_country_meshes(cData)