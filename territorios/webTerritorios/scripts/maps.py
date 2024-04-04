import math
from dotenv import load_dotenv
import os

# Function to calculate zoom level based on bounding box and image size
def calculate_zoom(bbox, width, height):
    WORLD_DIM = {'height': 256, 'width': 256}
    ZOOM_MAX = 13
    lat_rad = math.radians(bbox['north'] - bbox['south'])
    lat_zoom = math.ceil(math.log2(WORLD_DIM['height'] * height / lat_rad))

    lon_rad = math.radians(bbox['east'] - bbox['west'])
    lon_zoom = math.ceil(math.log2(WORLD_DIM['width'] * width / lon_rad))
    return min(lat_zoom, lon_zoom, ZOOM_MAX)

# Function to calculate bounding box for given points
def calculate_bounding_box(points):
    min_lat = min(point[0] for point in points)
    max_lat = max(point[0] for point in points)
    min_lon = min(point[1] for point in points)
    max_lon = max(point[1] for point in points)
    return {'south': min_lat, 'west': min_lon, 'north': max_lat, 'east': max_lon}

# Example points
points = [(-0.33096, -78.43727), (-0.32815, -78.43665), (-0.32581, -78.44173), (-0.33317, -78.43452), (-0.32770, -78.42725)]

# Example image size
image_width = 800
image_height = 600

# Calculate bounding box and zoom level
bbox = calculate_bounding_box(points)
zoom_level = calculate_zoom(bbox, image_width, image_height)

load_dotenv()  # This line brings all environment variables from .env into os.environ
print(os.environ['GOOGLE_MAPS_API_KEY'])

# Construct the static maps API URL
static_map_url = f'''https://maps.googleapis.com/maps/api/staticmap?size=640x390&scale=2&markers=icon:https://i.imgur.com/ZOWDO0O.png%7Cscale:2%7C-0.33096,-78.43727&markers=icon:https://i.imgur.com/NA2dEjH.png%7Cscale:2%7C-0.32815,-78.43665&markers=icon:https://i.imgur.com/2G5s3mu.png%7Cscale:2%7C-0.33317,-78.43452&markers=icon:https://i.imgur.com/iosHIwU.png%7Cscale:2%7C-0.32235,-78.44497&markers=icon:https://i.imgur.com/AjX1HYJ.png%7Cscale:2%7C-0.32770,-78.42725&maptype=roadmap&style=feature:landscape%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:poi.government%7Cvisibility:on&style=feature:poi.medical%7Cvisibility:on&style=feature:poi.park%7Cvisibility:on&style=feature:poi.place_of_worship%7Cvisibility:on&style=feature:poi.school%7Cvisibility:on&style=feature:poi.sports_complex%7Cvisibility:on&style=feature:road.arterial%7Celement:geometry.stroke%7Ccolor:0xff0000%7Cweight:1&style=feature:road.local%7Celement:geometry.stroke%7Ccolor:0x000000%7Cvisibility:on%7Cweight:0.5&key={os.environ['GOOGLE_MAPS_API_KEY']}'''

# https://imgur.com/a/pNtp9ah
# 

print(static_map_url)

'''https://maps.googleapis.com/maps/api/staticmap?
size=640x640
&scale=2
&center={longitud},{latitud}
&zoom={zoom}
&maptype=roadmap
&style=feature:landscape%7Cvisibility:off
&style=feature:poi%7Cvisibility:off
&style=feature:poi.government%7Cvisibility:on
&style=feature:poi.medical%7Cvisibility:on
&style=feature:poi.park%7Cvisibility:on
&style=feature:poi.place_of_worship%7Cvisibility:on
&style=feature:poi.school%7Cvisibility:on
&style=feature:poi.sports_complex%7Cvisibility:on
&style=feature:road.arterial%7Celement:geometry.stroke%7Ccolor:0xff0000%7Cweight:1
&style=feature:road.local%7Celement:geometry.stroke%7Ccolor:0x000000%7Cvisibility:on%7Cweight:0.5
&markers=icon:https://i.imgur.com/q1Iqwe5.png%7Cscale:2%7C{longitud},{latitud}
'''    

https://t.me/TerritoriosSenias_Bot?text=El%20sordo%20SS-034%20tiene%20un%20error:\n[Por%20favor,%20detalle%20lo%20que%20se%20debe%20corregir,%20puede%20enviar%20la%20ubicacion%20si%20desea]
https://t.me/TerritoriosSenias_Bot?msg=text=Hola
https://t.me/share/url?url={url}&text=Hola
tg://msg?=Hola&to=@TerritoriosSenias_Bot

https://t.me/TerritoriosSenias_Bot?start=report_SS-034
2