from datetime import datetime
import locale
import xml.etree.ElementTree as ET
from io import BytesIO

def obtener_fecha_titulo():
    fecha = datetime.now().date()
    locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
    fecha_formateada = fecha.strftime("%d de %B del %Y")
    return fecha_formateada

NOMBRE_KML = f"Sordos - {obtener_fecha_titulo()}"

root = ET.Element("kml")
root.set("xmlns", "http://www.opengis.net/kml/2.2")

document = ET.SubElement(root, "Document")

name = ET.SubElement(document, "name")
name.text = NOMBRE_KML

description = ET.SubElement(document, "description")
description.text = "Territorios de Señas Sangolquí"

estilos = b'''\
<Styles>
<Style id="icon-503-62AF44-normal">
    <IconStyle>
        <color>ff44af62</color>
        <scale>1.1</scale>
        <Icon>
            <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
        <hotSpot x="16" xunits="pixels" y="32" yunits="insetPixels"/>
    </IconStyle>
    <LabelStyle>
        <scale>0</scale>
    </LabelStyle>
    </Style>
    <Style id="icon-503-62AF44-highlight">
        <IconStyle>
        <color>ff44af62</color>
        <scale>1.1</scale>
        <Icon>
            <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
        </Icon>
        <hotSpot x="16" xunits="pixels" y="32" yunits="insetPixels"/>
        </IconStyle>
        <LabelStyle>
        <scale>1.1</scale>
        </LabelStyle>
    </Style>
    <StyleMap id="icon-503-62AF44">
        <Pair>
        <key>normal</key>
        <styleUrl>#icon-503-62AF44-normal</styleUrl>
        </Pair>
        <Pair>
        <key>highlight</key>
        <styleUrl>#icon-503-62AF44-highlight</styleUrl>
        </Pair>
        </StyleMap>
        <Style id="icon-503-DB4436-normal">
        <IconStyle>
            <color>ff3644db</color>
            <scale>1.1</scale>
            <Icon>
            <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
            </Icon>
            <hotSpot x="16" xunits="pixels" y="32" yunits="insetPixels"/>
        </IconStyle>
        <LabelStyle>
            <scale>0</scale>
        </LabelStyle>
        </Style>
        <Style id="icon-503-DB4436-highlight">
        <IconStyle>
            <color>ff3644db</color>
            <scale>1.1</scale>
            <Icon>
            <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
            </Icon>
            <hotSpot x="16" xunits="pixels" y="32" yunits="insetPixels"/>
        </IconStyle>
        <LabelStyle>
            <scale>1.1</scale>
        </LabelStyle>
        </Style>
        <StyleMap id="icon-503-DB4436">
        <Pair>
            <key>normal</key>
            <styleUrl>#icon-503-DB4436-normal</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#icon-503-DB4436-highlight</styleUrl>
        </Pair>
        </StyleMap>
        <Style id="icon-503-DB4436-nodesc-normal">
        <IconStyle>
            <color>ff3644db</color>
            <scale>1.1</scale>
            <Icon>
            <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
            </Icon>
            <hotSpot x="16" xunits="pixels" y="32" yunits="insetPixels"/>
        </IconStyle>
        <LabelStyle>
            <scale>0</scale>
        </LabelStyle>
        <BalloonStyle>
            <text><![CDATA[<h3>$[name]</h3>]]></text>
        </BalloonStyle>
        </Style>
        <Style id="icon-503-DB4436-nodesc-highlight">
        <IconStyle>
            <color>ff3644db</color>
            <scale>1.1</scale>
            <Icon>
            <href>https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png</href>
            </Icon>
            <hotSpot x="16" xunits="pixels" y="32" yunits="insetPixels"/>
        </IconStyle>
        <LabelStyle>
            <scale>1.1</scale>
        </LabelStyle>
        <BalloonStyle>
            <text><![CDATA[<h3>$[name]</h3>]]></text>
        </BalloonStyle>
        </Style>
        <StyleMap id="icon-503-DB4436-nodesc">
        <Pair>
            <key>normal</key>
            <styleUrl>#icon-503-DB4436-nodesc-normal</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#icon-503-DB4436-nodesc-highlight</styleUrl>
        </Pair>
        </StyleMap>
        <Style id="poly-DB4436-2501-0-nodesc-normal">
        <LineStyle>
            <color>ff3644db</color>
            <width>2.501</width>
        </LineStyle>
        <PolyStyle>
            <color>003644db</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
        <BalloonStyle>
            <text><![CDATA[<h3>$[name]</h3>]]></text>
        </BalloonStyle>
        </Style>
        <Style id="poly-DB4436-2501-0-nodesc-highlight">
        <LineStyle>
            <color>ff3644db</color>
            <width>3.7515</width>
        </LineStyle>
        <PolyStyle>
            <color>003644db</color>
            <fill>1</fill>
            <outline>1</outline>
        </PolyStyle>
        <BalloonStyle>
            <text><![CDATA[<h3>$[name]</h3>]]></text>
        </BalloonStyle>
        </Style>
        <StyleMap id="poly-DB4436-2501-0-nodesc">
        <Pair>
            <key>normal</key>
            <styleUrl>#poly-DB4436-2501-0-nodesc-normal</styleUrl>
        </Pair>
        <Pair>
            <key>highlight</key>
            <styleUrl>#poly-DB4436-2501-0-nodesc-highlight</styleUrl>
        </Pair>
        </StyleMap>
</Styles>\
'''

estilos = ET.parse(BytesIO(estilos))
estilos_root = estilos.getroot()

for estilo in estilos_root.iter('StyleMap'):
    document.append(estilo)
for estilo in estilos_root.iter('Style'):
    document.append(estilo)



tree = ET.ElementTree(root)
ET.indent(tree, space="\t", level=0)
tree.write("territorios.kml", xml_declaration=True,encoding='utf-8', method="xml")

'''
style = ET.SubElement(document, "Style")
style.set("id", "icon-503-62AF44-normal")
iconstyle = ET.SubElement(style, "IconStyle")
color = ET.SubElement(iconstyle, "color")
color.text = "ff44af62"
scale = ET.SubElement(iconstyle, "scale")
scale.text = "1.1"
icon = ET.SubElement(iconstyle, "Icon")
href = ET.SubElement(icon, "href")
href.text = "https://www.gstatic.com/mapspro/images/stock/503-wht-blank_maps.png"
hotspot = ET.SubElement(iconstyle, "hotSpot")
hotspot.set("x", "16")
hotspot.set("xunits", "pixels")
hotspot.set("y", "32")
hotspot.set("yunits", "insetPixels")
labelstyle = ET.SubElement(style, "LabelStyle")
scale = ET.SubElement(labelstyle, "scale")
scale.text = 0
'''
