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

NOMBRE_KML = f"Sordos Sangolqui - {obtener_fecha_titulo()}"
DESCRIPCION = "Territorios de Señas Sangolquí"

root = ET.Element("kml")
root.set("xmlns", "http://www.opengis.net/kml/2.2")

document = ET.SubElement(root, "Document")

estilos = b'''\
<Styles>
  <Style id="placemark-red">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-red.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-blue">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-blue.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-purple">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-purple.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-yellow">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-yellow.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-pink">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-pink.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-brown">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-brown.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-green">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-green.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-orange">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-orange.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-deeppurple">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-deeppurple.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-lightblue">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-lightblue.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-cyan">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-cyan.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-teal">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-teal.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-lime">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-lime.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-deeporange">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-deeporange.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-gray">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-gray.png</href>
      </Icon>
    </IconStyle>
  </Style>
  <Style id="placemark-bluegray">
    <IconStyle>
      <Icon>
        <href>http://maps.me/placemarks/placemark-bluegray.png</href>
      </Icon>
    </IconStyle>
  </Style>
</Styles>\
'''

estilos = ET.parse(BytesIO(estilos))
estilos_root = estilos.getroot()

for estilo in estilos_root.iter('Style'):
    document.append(estilo)

name = ET.SubElement(document, "name")
name.text = NOMBRE_KML

description = ET.SubElement(document, "description")
description.text = DESCRIPCION

visibility = ET.SubElement(document, "visibility")
visibility.text = "1"

# Extended Data
extended_data = ET.SubElement(document, "ExtendedData")
extended_data.set("xmlns:mwm", "http://maps.me/")
mwm_name = ET.SubElement(extended_data, "mwm:name")
mwm_lang = ET.SubElement(mwm_name, "mwm:lang")
mwm_lang.set("code", "default")
mwm_lang.text = NOMBRE_KML
mwm_annotation = ET.SubElement(extended_data, "mwm:annotation")
mwm_description = ET.SubElement(extended_data, "mwm:description")
mwmw_lang_2 = ET.SubElement(mwm_description, "mwm:lang")
mwmw_lang_2.set("code", "default")
mwmw_lang_2.text = DESCRIPCION
mwm_last_modified = ET.SubElement(extended_data, "mwm:lastModified")
mwm_last_modified.text = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
mwm_access_Rules = ET.SubElement(extended_data, "mwm:accessRules")
mwm_access_Rules.text = "Local"


data = {'congregacion_id': 1}
sordos =  requests.post('http://localhost:8000/api/sordos/para_kml_y_gpx/', json = data).json()

for sordo in sordos:
    placemark = ET.SubElement(document, "Placemark")
    
    name = ET.SubElement(placemark, "name")
    name.text = sordo['codigo'] + ' - ' + sordo['nombre'] + ' - ' + str(sordo['anio_nacimiento'])
    
    description = ET.SubElement(placemark, "description")
    description.text = f"{sordo['direccion']} -- {sordo['detalles_direccion']}"
    
    styleUrl = ET.SubElement(placemark, "styleUrl")
    if sordo['publicador_estudio']:
        styleUrl.text = "#placemark-lime"
    else:
        styleUrl.text = "#placemark-red"
    
    point = ET.SubElement(placemark, "Point")
    coordinates = ET.SubElement(point, "coordinates")
    coordinates.text = f"{sordo['gps_longitud']},{sordo['gps_latitud']}"
    
    #extended_data = ET.SubElement(placemark, "ExtendedData")
    #data = ET.SubElement(extended_data, "Data")
    #data.set("name", "Territorio")
    #value = ET.SubElement(data, "value")
    #value.text = f"{sordo['territorio_numero']} - {sordo['territorio_nombre']}"

tree = ET.ElementTree(root)
ET.indent(tree, space="\t", level=0)
tree.write("territorios.kml", xml_declaration=True,encoding='utf-8', method="xml")
