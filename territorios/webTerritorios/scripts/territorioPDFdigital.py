import argparse
from io import BytesIO
import pathlib
import PyPDF2
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from textwrap import wrap
from fitz import Rect, open as open_fitz
import os
from dotenv import load_dotenv
from datetime import datetime
from security import safe_requests

# Usando la unica plantilla d 5 sordos, estas son las posiciones en que debe ir el texto
# TODO Modificar para permitir diferentes plantillas
posiciones_texto_digital = [[24,270],[24,219],[24,168],[24,117],[24,66]]

def fecha_hoy_formato_espanol():
    current_date = datetime.now()
    months = {
        1: "enero", 2: "febrero", 3: "marzo", 4: "abril",
        5: "mayo", 6: "junio", 7: "julio", 8: "agosto",
        9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
    }
    formatted_date = current_date.strftime("%d de ") + months[current_date.month] + current_date.strftime(" %Y")
    return formatted_date

def generar_mapa(gps1, gps2, gps3, gps4, gps5):
    # Cargar Variables de Entorno
    load_dotenv()

    # Iconos Marcadores https://imgur.com/a/TsOuZ5N
    # HD con 120 pixeles de alto
    static_map_url = "https://maps.googleapis.com/maps/api/staticmap?size=640x390&scale=2"

    # Dependiendo d ela cantidad de Sordos, agregar los marcadores al mapa
    if gps1:
        static_map_url += f"&markers=icon:https://i.imgur.com/TZpeTeZ.png%7Cscale:2%7C{gps1}"
    if gps2:
        static_map_url += f"&markers=icon:https://i.imgur.com/u71rMfo.png%7Cscale:2%7C{gps2}"
    if gps3:
        static_map_url += f"&markers=icon:https://i.imgur.com/oBqEgG7.png%7Cscale:2%7C{gps3}"
    if gps4:
        static_map_url += f"&markers=icon:https://i.imgur.com/teU4P50.png%7Cscale:2%7C{gps4}"
    if gps5:
        static_map_url += f"&markers=icon:https://i.imgur.com/yQ9U9CF.png%7Cscale:2%7C{gps5}"
    
    # Estilos y Token
    static_map_url += f"&maptype=roadmap&style=feature:landscape%7Cvisibility:off&style=feature:poi%7Cvisibility:off&style=feature:poi.government%7Cvisibility:on&style=feature:poi.medical%7Cvisibility:on&style=feature:poi.park%7Cvisibility:on&style=feature:poi.place_of_worship%7Cvisibility:on&style=feature:poi.school%7Cvisibility:on&style=feature:poi.sports_complex%7Cvisibility:on&style=feature:road.arterial%7Celement:geometry.stroke%7Ccolor:0xff0000%7Cweight:1&style=feature:road.local%7Celement:geometry.stroke%7Ccolor:0x000000%7Cvisibility:on%7Cweight:0.5&key={os.environ['GOOGLE_MAPS_API_KEY']}"
    
    # Regresar el mapa como bytes en memoria para no generar archivos temporales
    imgData = safe_requests.get(static_map_url).content
    return imgData

def insertar_texto(text1, text2, text3, text4, text5, template="plantillaDigitalNuevosBotones.pdf"):
    
    # Si el template es un string, abrir el archivo
    if isinstance(template, str):
        template = PyPDF2.PdfReader(open(template, 'rb'))
    # En otro caso, se paso el la plantilla en memoria y se asume es tipo archivo
    else:
        template = PyPDF2.PdfReader(template)

    output = PyPDF2.PdfWriter()
    page = template.pages[0]

    # Crear canvas en memoria, no en archivo temporal
    overlay_buffer = BytesIO()
    c = canvas.Canvas(overlay_buffer, pagesize=[page.mediabox.width,page.mediabox.height])

    # TEXTO
    # Propiedades de Letra
    c.setFont("Helvetica", 5)
    c.setFillColor(colors.black)
    
    # Insetar textos
    posiciones = posiciones_texto_digital
    texts = [text1, text2, text3, text4, text5]
    for i in range(5):
        t = c.beginText()
        t.setTextOrigin(posiciones[i][0], posiciones[i][1])
        text = "\\n".join(wrap(texts[i], 50)) # Max caracteres/Linea, salto de linea
        lines = text.split("\\n")
        for line in lines:
            t.textLine(line)
        c.drawText(t)
    c.save()

    # Resetear el puntero del buffer para leerlo
    overlay_buffer.seek(0)
    overlay = PyPDF2.PdfReader(overlay_buffer).pages[0]
    page.merge_page(overlay)

    output.add_page(page)

    # Guardar el resultado en un buffer en memoria
    output_buffer = BytesIO()
    output.write(output_buffer)
    output_buffer.seek(0)
    
    return output_buffer

def insertar_mapa_y_botones(output_buffer, territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, id_asignacion, icon1="recursos/botonGoogle.png", icon2="recursos/botonOsmand.png", icon_reportar="recursos/botonReportar.png", icon_entregar="recursos/botonTerminar.png"):
    
    # Abrir PDF desde buffer en memoria
    archivo_buffer = BytesIO(output_buffer.getvalue())
    archivo = open_fitz(stream=archivo_buffer, filetype="pdf")
    primera_pagina = archivo[0]

    # Mapa en memoria e insertarlo en pdf
    mapa_bytes = generar_mapa(gps1, gps2, gps3, gps4, gps5)
    mapa_rectangle = Rect(0,0,184,112)
    primera_pagina.insert_image(mapa_rectangle, stream=mapa_bytes)

    # Boton Entregar Territorio
    boton_entrega_rectangle = Rect(50,368,130,388)

    # Cargar iconos como bytes si son strings (paths)
    if isinstance(icon_entregar, str):
        with open(icon_entregar, 'rb') as f:
            icon_entregar_bytes = f.read()
    # Si no asumir es de tipo bytes
    else:
        icon_entregar_bytes = icon_entregar
    
    primera_pagina.insert_image(boton_entrega_rectangle, stream=icon_entregar_bytes)
    primera_pagina.insert_link({'kind': 2, 'from': boton_entrega_rectangle, 'uri': f'https://t.me/TerritoriosSenias_Bot?start=entregar_{id_asignacion}'})

    # Cargar los demás iconos (Apps de Mapas y Reportar) como bytes si son strings (paths) o Asumir que son bytes
    if isinstance(icon1, str):
        with open(icon1, 'rb') as f:
            icon1_bytes = f.read()
    else:
        icon1_bytes = icon1
        
    if isinstance(icon2, str):
        with open(icon2, 'rb') as f:
            icon2_bytes = f.read()
    else:
        icon2_bytes = icon2
        
    if isinstance(icon_reportar, str):
        with open(icon_reportar, 'rb') as f:
            icon_reportar_bytes = f.read()
    else:
        icon_reportar_bytes = icon_reportar



    # Botones dependientes del Sordo (GPS y Reportar)
    gps_list = [gps1, gps2, gps3, gps4, gps5]
    id_sordos_list = [id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5]
    for i in range(5):
        if not gps_list[i] and not id_sordos_list[i]:
            continue

        # Botones Ubicacion - Proporcion (203 x 106)
        diferencial_en_y_entre_sordos = 51 * i
        dif = diferencial_en_y_entre_sordos 
        googlemaps_rectangle = Rect(140,(117 + dif),178,(137 + dif))
        osmand_rectangle = Rect(140,(139 + dif),178,(159 + dif))

        # Boton Reportar - (61 x 61)
        reportar_rectangle = Rect(10, (148 + dif), 20, (158 + dif))
        primera_pagina.insert_link({'kind': 2, 'from': reportar_rectangle, 'uri': f'https://t.me/TerritoriosSenias_Bot?start=reportar_{id_sordos_list[i]}'})

        # Insertar Imagenes
        primera_pagina.insert_image(googlemaps_rectangle, stream=icon1_bytes)
        primera_pagina.insert_image(osmand_rectangle, stream=icon2_bytes)
        primera_pagina.insert_image(reportar_rectangle, stream=icon_reportar_bytes)

        # Coordenadas GPS
        gps = gps_list[i].split(",")

        primera_pagina.insert_link({'kind': 2, 'from': googlemaps_rectangle, 'uri': f'https://www.google.com/maps/search/?api=1&query={gps[0]},{gps[1]}'})
        primera_pagina.insert_link({'kind': 2, 'from': osmand_rectangle, 'uri': f'https://osmand.net/map?pin={gps[0]},{gps[1]}#16/{gps[0]}/{gps[1]}'})    
    
    # Guardar el resultado en buffer en lugar de archivo
    output_final_buffer = BytesIO()
    archivo.save(output_final_buffer, garbage=4, deflate=True)
    output_final_buffer.seek(0)
    
    # Generar un nombre de archivo sugerido (no se guarda, solo se devuelve como metadata)
    filename = f"{territory_name} - {fecha_hoy_formato_espanol()}.pdf"
    
    return output_final_buffer.getvalue(), filename

# Funcion que englobe el proceso para importar desde App Django
def llenarTerritorioDigital(text1, text2, text3, text4, text5, territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, id_asignacion, template="recursos/plantillaDigitalNuevosBotones.pdf", icon1="recursos/botonGoogle.png", icon2="recursos/botonOsmand.png", icon_reportar="recursos/botonReportar.png", icon_entregar="recursos/botonTerminar.png"):
    output_buffer = insertar_texto(text1, text2, text3, text4, text5, template)
    pdf_bytes, filename = insertar_mapa_y_botones(output_buffer, territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, id_asignacion, icon1, icon2, icon_reportar, icon_entregar)
    return pdf_bytes, filename

# Para mantener la compatibilidad con el script original cuando se ejecuta desde la línea de comandos
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
    parser.add_argument('--output', default=None, required=False, help='Ruta de salida del PDF generado (opcional)')
    
    args = parser.parse_args()

    # Limpiar los GPS de paréntesis
    args.gps1 = args.gps1.replace("(", "").replace(")", "")
    args.gps2 = args.gps2.replace("(", "").replace(")", "")
    args.gps3 = args.gps3.replace("(", "").replace(")", "")
    args.gps4 = args.gps4.replace("(", "").replace(")", "")
    args.gps5 = args.gps5.replace("(", "").replace(")", "")

    # Generar PDF en memoria
    pdf_bytes, filename = llenarTerritorioDigital(
        args.text1, args.text2, args.text3, args.text4, args.text5,
        args.territory_name,
        args.gps1, args.gps2, args.gps3, args.gps4, args.gps5,
        args.id_sordo_1, args.id_sordo_2, args.id_sordo_3, args.id_sordo_4, args.id_sordo_5,
        args.id_asignacion,
        args.template, args.icon1, args.icon2, args.icon_reportar, args.icon_entregar
    )
    
    # Si se ejecuta como script, guardar el PDF en un archivo
    output_path = args.output if args.output else filename
    with open(output_path, 'wb') as f:
        f.write(pdf_bytes)
    
    print(f"Archivo generado correctamente: {output_path}")

if __name__ == "__main__":
    main()

# Ejemplo de uso desde Terminal
'''
python territorioPDFdigital.py -1 "Texto 1" -2 "Texto 2" -3 "Texto 3 lorem ipsum estamos como estamos por que quereos ser muy felice spor la entrada de la autopsta ruminahui ddsa " -4 "Texto 4"     -5 "Texto 5 \n dsadas"   --gps1 "(-0.33096,-78.43727)" --gps2 "(-0.32815,-78.43665)" --gps3 "(-0.32581,-78.44173)" --gps4 "(-0.33317,-78.43452)" --gps5 "(-0.32770,-78.42725)" -n "Terracota" --id_sordo_1 SS-031 --id_sordo_2 SS-032 --id_sordo_3 SS-033 --id_sordo_4 SS-034 --id_sordo_5 SS-035 --id_asignacion 13214
'''
