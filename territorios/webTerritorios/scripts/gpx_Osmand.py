from datetime import datetime
import locale
import xml.etree.ElementTree as ET
from io import BytesIO

import requests

def obtener_fecha_titulo():
    fecha = datetime.now().date()
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    fecha_formateada = fecha.strftime("%d de %B del %Y")
    return fecha_formateada

NOMBRE_GPX = f"Sordos - {obtener_fecha_titulo()}"

root = ET.Element("gpx")
root.set("version", "1.1")
root.set("creator", "OsmAnd Maps 4.7.3 (4.7.3.10)")
root.set("xmlns", "http://www.topografix.com/GPX/1/1")
root.set("xmlns:osmand", "https://osmand.net")
root.set("xmlns:gpxtpx", "http://www.garmin.com/xmlschemas/TrackPointExtension/v1")
root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")
root.set("xsi:schemaLocation", "http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd")

metadata = ET.SubElement(root, "metadata")

name = ET.SubElement(metadata, "name")
name.text = NOMBRE_GPX

time = ET.SubElement(metadata, "time")
time.text = str(datetime.now().date())
                
# Puntos
data = {'congregacion_id': 1}
sordos =  requests.post('http://localhost:8000/api/sordos/para_kml_y_gpx/', json = data).json()

for sordo in sordos:
    wpt = ET.SubElement(root, "wpt")
    wpt.set("lat", str(sordo['gps_latitud']))
    wpt.set("lon", str(sordo['gps_longitud']))

    ele = ET.SubElement(wpt, "ele")
    name_gpx = ET.SubElement(wpt, "name")
    name_gpx.text = f"{sordo['codigo']} - {sordo['nombre']} - {sordo['anio_nacimiento']}"
    desc = ET.SubElement(wpt, "desc")
    desc.text = f"{sordo['direccion']} -- {sordo['detalles_direccion']}"
    cmt = ET.SubElement(wpt, "cmt")
    cmt.text = f"{sordo['direccion']} -- {sordo['detalles_direccion']}"


# extensions = b'''\
# <ext>
# <extensions>
#         <osmand:show_arrows>false</osmand:show_arrows>
#         <osmand:show_start_finish>true</osmand:show_start_finish>
#         <osmand:vertical_exaggeration_scale>1.000000</osmand:vertical_exaggeration_scale>
#         <osmand:line_3d_visualization_by_type>none</osmand:line_3d_visualization_by_type>
#         <osmand:line_3d_visualization_wall_color_type>upward_gradient</osmand:line_3d_visualization_wall_color_type>
#         <osmand:line_3d_visualization_position_type>top</osmand:line_3d_visualization_position_type>
#         <osmand:split_interval>0</osmand:split_interval>
#         <osmand:split_type>no_split</osmand:split_type>
#         <osmand:points_groups>
#             <osmand:group color="#ffffffff" background="" name="" icon=""/>
#         </osmand:points_groups>
#     </extensions>
#     <extensions>
#     </extensions>
# </ext>\
# '''
# extensions = ET.parse(BytesIO(extensions))
# extensions_root = extensions.getroot()
# for extension in extensions_root.iter('extensions'):
#     root.append(extension)


# Hola

extensions = ET.SubElement(root, "extensions")
points_groups = ET.SubElement(extensions, "osmand:points_groups")
group = ET.SubElement(points_groups, "osmand:group")
group.set("background", "circle")
group.set("name", NOMBRE_GPX)
group.set("color", "#ffff0000")
group.set("icon", "special_marker")

tree = ET.ElementTree(root)
ET.indent(tree, space="\t", level=0)
tree.write("territorios.gpx", xml_declaration=True,encoding='utf-8', method="xml")
