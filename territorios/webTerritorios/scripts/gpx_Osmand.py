from datetime import datetime
import locale
import xml.etree.ElementTree as ET
from io import BytesIO

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
