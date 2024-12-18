import argparse
import pathlib
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from textwrap import wrap
from fitz import Rect, open as open_fitz
import os
from dotenv import load_dotenv
import requests
from datetime import datetime

posiciones_texto_digital = [[24,270],[24,219],[24,168],[24,117],[24,66]]

def fecha_hoy_formato_espanol():
    current_date = datetime.now()
    months = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    # Format the date
    formatted_date = current_date.strftime("%d de ") + months[current_date.month] + current_date.strftime(" %Y")
    return formatted_date

def generar_mapa(gps1, gps2, gps3, gps4, gps5):
    load_dotenv()

    # Iconos Marcadores https://imgur.com/a/pNtp9ah 
    # MD con 90 pixeles de alto
    # static_map_url = f'''https://maps.googleapis.com/maps/api/staticmap?size=640x390&scale=2&markers=icon:https://i.imgur.com/ZOWDO0O.png%7Cscale:2%7C{gps1.replace("(","").replace(")","")}&markers=icon:https://i.imgur.com/NA2dEjH.png%7Cscale:2%7C{gps2.replace("(","").replace(")","")}&markers=icon:https://i.imgur.com/2G5s3mu.png%7Cscale:2%7C{gps3.replace("(","").replace(")","")}&markers=icon:https://i.imgur.com/iosHIwU.png%7Cscale:2%7C{gps4.replace("(","").replace(")","")}&markers=icon:https://i.imgur.com/AjX1HYJ.png%7Cscale:2%7C{gps5.replace("(","").replace(")","")}&maptype=roadmap&style=feature:landscape%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:poi.government%7Cvisibility:on&style=feature:poi.medical%7Cvisibility:on&style=feature:poi.park%7Cvisibility:on&style=feature:poi.place_of_worship%7Cvisibility:on&style=feature:poi.school%7Cvisibility:on&style=feature:poi.sports_complex%7Cvisibility:on&style=feature:road.arterial%7Celement:geometry.stroke%7Ccolor:0xff0000%7Cweight:1&style=feature:road.local%7Celement:geometry.stroke%7Ccolor:0x000000%7Cvisibility:on%7Cweight:0.5&key={os.environ['GOOGLE_MAPS_API_KEY']}'''
    # HD con 120 pixeles de alto
    static_map_url = "https://maps.googleapis.com/maps/api/staticmap?size=640x390&scale=2"

    if gps1:
        static_map_url += f"&markers=icon:https://i.imgur.com/1V4605W.png%7Cscale:2%7C{gps1}"
    if gps2:
        static_map_url += f"&markers=icon:https://i.imgur.com/T9QOGJV.png%7Cscale:2%7C{gps2}"
    if gps3:
        static_map_url += f"&markers=icon:https://i.imgur.com/XRk5ysU.png%7Cscale:2%7C{gps3}"
    if gps4:
        static_map_url += f"&markers=icon:https://i.imgur.com/3RPpnd4.png%7Cscale:2%7C{gps4}"
    if gps5:
        static_map_url += f"&markers=icon:https://i.imgur.com/dp8riZt.png%7Cscale:2%7C{gps5}"
    # Estilos y Token
    static_map_url += f"&maptype=roadmap&style=feature:landscape%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:poi.government%7Cvisibility:on&style=feature:poi.medical%7Cvisibility:on&style=feature:poi.park%7Cvisibility:on&style=feature:poi.place_of_worship%7Cvisibility:on&style=feature:poi.school%7Cvisibility:on&style=feature:poi.sports_complex%7Cvisibility:on&style=feature:road.arterial%7Celement:geometry.stroke%7Ccolor:0xff0000%7Cweight:1&style=feature:road.local%7Celement:geometry.stroke%7Ccolor:0x000000%7Cvisibility:on%7Cweight:0.5&key={os.environ['GOOGLE_MAPS_API_KEY']}"
    imgData = requests.get(static_map_url, timeout=60).content
    with open("mapa.jpg", 'wb') as handlerImage:
        handlerImage.write(imgData)

    return "mapa.jpg"    

def insertar_texto(text1, text2, text3, text4, text5, template="plantillaDigitalNuevosBotones.pdf"):
    template = PyPDF2.PdfReader(open(template, 'rb'))
    output = PyPDF2.PdfWriter()
    page = template.pages[0]

    c = canvas.Canvas("overlay.pdf", pagesize=[page.mediabox.width,page.mediabox.height])

    # Texto

    # Propiedades de Letra
    c.setFont("Helvetica", 5)
    c.setFillColor(colors.black)
    
    # Insetar textos
    posiciones = posiciones_texto_digital
    texts = [text1, text2, text3, text4, text5]
    for i in range(5):
        t = c.beginText()
        t.setTextOrigin(posiciones[i][0], posiciones[i][1])
        text = "\\n".join(wrap(texts[i], 50)) # Max caracteres/Linea
        lines = text.split("\\n")
        for line in lines:
            t.textLine(line)
        c.drawText(t)
    c.save()

    overlay = PyPDF2.PdfReader(open("overlay.pdf", 'rb')).pages[0]
    page.merge_page(overlay)

    output.add_page(page)

    with open("output.pdf", 'wb') as f:
        output.write(f)

    # Cleanup
    try:
        os.remove("overlay.pdf")# Mover a cleanup function
    except:
        pass

def insertar_mapa_y_botones(territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, id_asignacion, icon1="recursos/botonGoogle.png", icon2="recursos/botonOsmand.png", icon_reportar="recursos/botonReportar.png", icon_entregar="recursos/botonTerminar.png"):

    archivo = open_fitz("output.pdf")
    primera_pagina = archivo[0]

    # Mapa
    generar_mapa(gps1, gps2, gps3, gps4, gps5)
    mapa_rectangle = Rect(0,0,184,112)
    primera_pagina.insert_image(mapa_rectangle, filename="mapa.jpg")

    # Boton Entregar Territorio
    boton_entrega_rectangle = Rect(50,368,130,388)
    primera_pagina.insert_image(boton_entrega_rectangle, filename=icon_entregar)
    primera_pagina.insert_link({'kind': 2, 'from': boton_entrega_rectangle, 'uri': f'https://t.me/TerritoriosSenias_Bot?start=entregar_{id_asignacion}'})

    # Botones dependientes del Sordo (GPS y Reportar)
    gps_list = [gps1, gps2, gps3, gps4, gps5]
    id_sordos_list = [id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5]
    for i in range(5):

        if not gps_list[i] and not id_sordos_list[i]:
            continue

        # Botones Ubicacion Proporcion (203 x 106)
        diferencial_en_y_entre_sordos = 51 * i
        dif = diferencial_en_y_entre_sordos 
        googlemaps_rectangle = Rect(140,(117 + dif),178,(137 + dif))
        osmand_rectangle = Rect(140,(139 + dif),178,(159 + dif))

        # Boton Reportar (61 x 61)
        reportar_rectangle = Rect(10, (148 + dif), 20, (158 + dif))
        primera_pagina.insert_link({'kind': 2, 'from': reportar_rectangle, 'uri': f'https://t.me/TerritoriosSenias_Bot?start=reportar_{id_sordos_list[i]}'})

        # Insertar Imagenes
        primera_pagina.insert_image(googlemaps_rectangle, filename=icon1)
        primera_pagina.insert_image(osmand_rectangle, filename=icon2)
        primera_pagina.insert_image(reportar_rectangle, filename=icon_reportar)

        # Coordenadas GPS
        gps = gps_list[i].split(",")

        primera_pagina.insert_link({'kind': 2, 'from': googlemaps_rectangle, 'uri': f'https://www.google.com/maps/search/?api=1&query={gps[0]},{gps[1]}'})
        primera_pagina.insert_link({'kind': 2, 'from': osmand_rectangle, 'uri': f'https://osmand.net/map?pin={gps[0]},{gps[1]}#16/{gps[0]}/{gps[1]}'})    
    

    
    archivo.save(f"{pathlib.Path(__file__).parent.resolve()}/{territory_name} - {fecha_hoy_formato_espanol()}.pdf", garbage=4, deflate=True)

    # Cleanup
    try:
        os.remove("output.pdf")
        os.remove("mapa.jpg")
    except:
        pass

    return f"{pathlib.Path(__file__).parent.resolve()}/{territory_name} - {fecha_hoy_formato_espanol()}.pdf"

# Funcion que englobe el proceso para importar desde App Django
def llenarTerritorioDigital(text1, text2, text3, text4, text5, territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, id_asignacion, template="recursos/plantillaDigitalNuevosBotones.pdf", icon1="recursos/botonGoogle.png", icon2="recursos/botonOsmand.png", icon_reportar="recursos/botonReportar.png", icon_entregar="recursos/botonTerminar.png"):
    insertar_texto(text1, text2, text3, text4, text5, template)
    output = insertar_mapa_y_botones(territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, id_asignacion, icon1, icon2, icon_reportar, icon_entregar)
    return output

# Funcion que recibe datos en un JSON
def llenarTerritorioDigitalJSON(data):
    pass

def main():
    parser = argparse.ArgumentParser(description='Script para llenar plantillas de Territorios')
    parser.add_argument('--territory_name', '-n', required=True, help='Nombre del Territorio')
    parser.add_argument('--text1', '-1', required=True, help='Texto Sordo 1')
    parser.add_argument('--text2', '-2', required=True, help='Texto Sordo 2')
    parser.add_argument('--text3', '-3', required=True, help='Texto Sordo 3')
    parser.add_argument('--text4', '-4', required=True, help='Texto Sordo 4')
    parser.add_argument('--text5', '-5', required=True, help='Texto Sordo 5')
    parser.add_argument('--gps1', required=True, help='Coordenadas GPS 1 latitud,longitud')
    parser.add_argument('--gps2', required=True, help='Coordenadas GPS 2 latitud,longitud')
    parser.add_argument('--gps3', required=True, help='Coordenadas GPS 3 latitud,longitud')
    parser.add_argument('--gps4', required=True, help='Coordenadas GPS 4 latitud,longitud')
    parser.add_argument('--gps5', required=True, help='Coordenadas GPS 5 latitud,longitud')
    parser.add_argument('--id_sordo_1', required=True, help='ID de Sordo 1')
    parser.add_argument('--id_sordo_2', required=True, help='ID de Sordo 2')
    parser.add_argument('--id_sordo_3', required=True, help='ID de Sordo 3')
    parser.add_argument('--id_sordo_4', required=True, help='ID de Sordo 4')
    parser.add_argument('--id_sordo_5', required=True, help='ID de Sordo 5')
    parser.add_argument('--id_asignacion', required=True, help='ID de Asignacion para Registrar Entrega')
    parser.add_argument('--icon1', default="recursos/botonGoogle.png", help='Icono para Boton Google Maps')
    parser.add_argument('--icon2', default="recursos/botonOsmand.png", help='Icono para Boton Osmand')
    parser.add_argument('--icon_reportar', default="recursos/botonReportar.png", help='Icono para Boton Reportar')
    parser.add_argument('--icon_entregar', default="recursos/botonTerminar.png", required=False, help='Boton Terminar')
    parser.add_argument('--template', default="recursos/plantillaDigitalNuevosBotones.pdf", required=False, help='Plantilla a Utilizar')
    

    args = parser.parse_args()

    args.gps1 = args.gps1.replace("(", "").replace(")", "")
    args.gps2 = args.gps2.replace("(", "").replace(")", "")
    args.gps3 = args.gps3.replace("(", "").replace(")", "")
    args.gps4 = args.gps4.replace("(", "").replace(")", "")
    args.gps5 = args.gps5.replace("(", "").replace(")", "")

    insertar_texto(args.text1, args.text2, args.text3, args.text4, args.text5, args.template)
    insertar_mapa_y_botones(args.territory_name, args.gps1, args.gps2, args.gps3, args.gps4, args.gps5, args.id_sordo_1, args.id_sordo_2, args.id_sordo_3, args.id_sordo_4, args.id_sordo_5, args.id_asignacion, args.icon1, args.icon2, args.icon_reportar, args.icon_entregar)

if __name__ == "__main__":
    main()

# Ejemplo de uso desde Terminal
'''
python territorioPDFdigital.py -1 "Texto 1" -2 "Texto 2" -3 "Texto 3 lorem ipsum estamos como estamos por que quereos ser muy felice spor la entrada de la autopsta ruminahui ddsa " -4 "Texto 4"     -5 "Texto 5 \n dsadas"   --gps1 "(-0.33096,-78.43727)" --gps2 "(-0.32815,-78.43665)" --gps3 "(-0.32581,-78.44173)" --gps4 "(-0.33317,-78.43452)" --gps5 "(-0.32770,-78.42725)" -n "Terracota" --id_sordo_1 SS-031 --id_sordo_2 SS-032 --id_sordo_3 SS-033 --id_sordo_4 SS-034 --id_sordo_5 SS-035 --id_asignacion 13214
'''
