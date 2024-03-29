import geopandas as gpd
import pandas as pd
import fiona

def countryData(path):
    data = gpd.read_file(path, engine='pyogrio', use_arrow=True)

    return data

cData = countryData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\gadm_410-levels.gpkg")

layers = fiona.listlayers("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\gadm_410-levels.gpkg")
print(layers)
#describe the data
print(cData.head())
print(cData.info())
print(cData.describe())

def countryBorders(data):
    # Filter the data where GID_0 is not null
    country_borders = data[data['GID_0'].notnull()]

    return country_borders

# Use the function
cData = countryData("C:\\Users\\trist\\Desktop\\gingkoi\\mapplacer\\gadm_410-levels.gpkg")
country_borders = countryBorders(cData)

# Now, country_borders contains only the country level data
print(country_borders.head())
# ============================ LEVELS ============================
#   GID_0      COUNTRY                                           geometry
# 0   ABW        Aruba  MULTIPOLYGON (((-69.97820 12.46986, -69.97847 ...
# 1   AFG  Afghanistan  MULTIPOLYGON (((63.61554 29.46970, 63.61425 29...
# 2   AGO       Angola  MULTIPOLYGON (((19.89892 -17.87674, 19.89082 -...
# 3   AIA     Anguilla  MULTIPOLYGON (((-63.02064 18.20750, -63.02587 ...
# 4   ALA        Åland  MULTIPOLYGON (((21.32306 59.74847, 21.32306 59...
# <class 'geopandas.geodataframe.GeoDataFrame'>
# RangeIndex: 263 entries, 0 to 262
# Data columns (total 3 columns):
#  #   Column    Non-Null Count  Dtype
# ---  ------    --------------  -----
#  0   GID_0     263 non-null    object
#  1   COUNTRY   263 non-null    object
#  2   geometry  263 non-null    geometry
# dtypes: geometry(1), object(2)
# memory usage: 6.3+ KB
# None
#        GID_0 COUNTRY                                           geometry
# count    263     263                                                263
# unique   263     254                                                263
# top      ABW   India  MULTIPOLYGON (((-69.97819519099988 12.46986103...
# freq       1       6                                                  1
# ============================ NO LEVELS ============================
#   UID GID_0       NAME_0 VARNAME_0    GID_1      NAME_1  ... REGION VARREGION      COUNTRY CONTINENT SUBCONT                                           geometry
# 0    1   AFG  Afghanistan            AFG.1_1  Badakhshan  ...                   Afghanistan      Asia          MULTIPOLYGON (((71.41149 36.55717, 71.40954 36...
# 1    2   AFG  Afghanistan            AFG.1_1  Badakhshan  ...                   Afghanistan      Asia          MULTIPOLYGON (((71.27620 38.00465, 71.27578 38...
# 2    3   AFG  Afghanistan            AFG.1_1  Badakhshan  ...                   Afghanistan      Asia          MULTIPOLYGON (((70.78272 37.27678, 70.78635 37...
# 3    4   AFG  Afghanistan            AFG.1_1  Badakhshan  ...                   Afghanistan      Asia          MULTIPOLYGON (((71.41149 36.55717, 71.40091 36...
# 4    5   AFG  Afghanistan            AFG.1_1  Badakhshan  ...                   Afghanistan      Asia          MULTIPOLYGON (((70.71236 37.07621, 70.73582 37...

# [5 rows x 53 columns]
# <class 'geopandas.geodataframe.GeoDataFrame'>
# RangeIndex: 356508 entries, 0 to 356507
# Data columns (total 53 columns):
#  #   Column      Non-Null Count   Dtype
# ---  ------      --------------   -----
#  0   UID         356508 non-null  int64
#  1   GID_0       356508 non-null  object
#  2   NAME_0      356508 non-null  object
#  3   VARNAME_0   356508 non-null  object
#  4   GID_1       356508 non-null  object
#  5   NAME_1      356508 non-null  object
#  6   VARNAME_1   356508 non-null  object
#  7   NL_NAME_1   356508 non-null  object
#  8   ISO_1       356508 non-null  object
#  9   HASC_1      356508 non-null  object
#  10  CC_1        356508 non-null  object
#  11  TYPE_1      356508 non-null  object
#  12  ENGTYPE_1   356508 non-null  object
#  13  VALIDFR_1   356508 non-null  object
#  14  GID_2       356508 non-null  object
#  15  NAME_2      356508 non-null  object
#  16  VARNAME_2   356508 non-null  object
#  17  NL_NAME_2   356508 non-null  object
#  18  HASC_2      356508 non-null  object
#  19  CC_2        356508 non-null  object
#  20  TYPE_2      356508 non-null  object
#  21  ENGTYPE_2   356508 non-null  object
#  22  VALIDFR_2   356508 non-null  object
#  23  GID_3       356508 non-null  object
#  24  NAME_3      356508 non-null  object
#  25  VARNAME_3   356508 non-null  object
#  26  NL_NAME_3   356508 non-null  object
#  27  HASC_3      356508 non-null  object
#  28  CC_3        356508 non-null  object
#  29  TYPE_3      356508 non-null  object
#  30  ENGTYPE_3   356508 non-null  object
#  31  VALIDFR_3   356508 non-null  object
#  32  GID_4       356508 non-null  object
#  33  NAME_4      356508 non-null  object
#  34  VARNAME_4   356508 non-null  object
#  35  CC_4        356508 non-null  object
#  36  TYPE_4      356508 non-null  object
#  37  ENGTYPE_4   356508 non-null  object
#  38  VALIDFR_4   356508 non-null  object
#  39  GID_5       356508 non-null  object
#  40  NAME_5      356508 non-null  object
#  41  CC_5        356508 non-null  object
#  42  TYPE_5      356508 non-null  object
#  43  ENGTYPE_5   356508 non-null  object
#  44  GOVERNEDBY  356508 non-null  object
#  45  SOVEREIGN   356508 non-null  object
#  46  DISPUTEDBY  356508 non-null  object
#  47  REGION      356508 non-null  object
#  48  VARREGION   356508 non-null  object
#  49  COUNTRY     356508 non-null  object
#  50  CONTINENT   356508 non-null  object
#  51  SUBCONT     356508 non-null  object
#  52  geometry    356508 non-null  geometry
# dtypes: geometry(1), int64(1), object(51)
# memory usage: 144.2+ MB
# None
#                  UID
# count  356508.000000
# mean   178254.500000
# std    102915.139222
# min         1.000000
# 25%     89127.750000
# 50%    178254.500000
# 75%    267381.250000
# max    356508.000000
