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
import requests
from datetime import datetime
import qrcode

# Usando la unica plantilla d 5 sordos, estas son las posiciones en que debe ir el texto
# TODO Modificar para permitir diferentes plantillas
posiciones_texto_impreso = [[47,317],[47,251],[47,185],[47,119],[47,53]]

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
    # Cargar Variables de Entorno
    load_dotenv()

    # Iconos Marcadores https://imgur.com/a/TsOuZ5N
    # HD con 120 pixeles de alto
    static_map_url = "https://maps.googleapis.com/maps/api/staticmap?size=640x370&scale=2"

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
    imgData = requests.get(static_map_url).content
    return imgData    

def insertar_texto(text1, text2, text3, text4, text5, nombre_territorio, template="plantillaDigitalNuevosBotones.pdf"):

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
    c.setFont("Helvetica-Bold", 11)
    c.setFillColor(colors.black)
    
    # Titulo Nombre Territorio Bold
    t = c.beginText()
    t.setTextOrigin(180,576) # Esquina Superior Izquierda
    t.textLine(nombre_territorio)
    c.drawText(t)

    c.setFont("Helvetica", 8)

    # Insertar textos
    posiciones = posiciones_texto_impreso
    texts = [text1, text2, text3, text4, text5]
    for i in range(5):
        t = c.beginText()
        t.setTextOrigin(posiciones[i][0], posiciones[i][1])
        text = "\\n".join(wrap(texts[i], 60)) # Max caracteres/Linea
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

def insertar_mapa_y_qr(output_buffer, territory_name , gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5):

    # Abrir PDF desde buffer en memoria
    archivo_buffer = BytesIO(output_buffer.getvalue())
    archivo = open_fitz(stream=archivo_buffer, filetype="pdf")
    primera_pagina = archivo[0]

    # Mapa
    mapa_bytes = generar_mapa(gps1, gps2, gps3, gps4, gps5)
    mapa_rectangle = Rect(0, 15,419,270)
    primera_pagina.insert_image(mapa_rectangle, stream=mapa_bytes)

    gps_list = [gps1, gps2, gps3, gps4, gps5]
    id_sordos_list = [id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5]
    for i in range(5):
        if not gps_list[i] and not id_sordos_list[i]:
            continue

        # Botones Ubicacion Proporcion (203 x 106)
        diferencial_en_y_entre_sordos = 66 * i
        dif = diferencial_en_y_entre_sordos 
        googlemaps_rectangle = Rect(297,(272 + dif),340,(315 + dif))
        osmand_rectangle = Rect(366,(272 + dif),409,(315 + dif))

        # Coordenadas GPS
        gps = gps_list[i].split(",")

        qr_google = qrcode.make(f'https://www.google.com/maps/search/?api=1&query={gps[0]},{gps[1]}')
        qr_google_buffer = BytesIO()
        qr_google.save(qr_google_buffer, format="JPEG")
        qr_google_buffer.seek(0)
        primera_pagina.insert_image(googlemaps_rectangle, stream=qr_google_buffer)


        qr_osmand = qrcode.make(f'https://osmand.net/map?pin={gps[0]},{gps[1]}#16/{gps[0]}/{gps[1]}')
        qr_osmand_buffer = BytesIO()
        qr_osmand.save(qr_osmand_buffer, format="JPEG")
        qr_osmand_buffer.seek(0)
        primera_pagina.insert_image(osmand_rectangle, stream=qr_osmand_buffer)
    
    # Guardar el resultado en buffer en lugar de archivo
    output_final_buffer = BytesIO()
    archivo.save(output_final_buffer, garbage=4, deflate=True)
    output_final_buffer.seek(0)

    # Generar un nombre de archivo sugerido (no se guarda, solo se devuelve como metadata)
    filename = f"{territory_name} - {fecha_hoy_formato_espanol()}.pdf"
    
    return output_final_buffer.getvalue(), filename

# Funcion que englobe el proceso para importar desde App Django
def llenarTerritorioImpreso(text1, text2, text3, text4, text5, territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5, template="recursos/plantillaVaciaImprimir.pdf"):
    output_buffer = insertar_texto(text1, text2, text3, text4, text5, territory_name, template)
    pdf_bytes, filename = insertar_mapa_y_qr(output_buffer, territory_name, gps1, gps2, gps3, gps4, gps5, id_sordo_1, id_sordo_2, id_sordo_3, id_sordo_4, id_sordo_5)
    return pdf_bytes, filename

def main():
    parser = argparse.ArgumentParser(description='Script para llenar plantillas de Territorios')
    parser.add_argument('--territory_name', '-n', required=True, help='Nombre del Territorio')
    parser.add_argument('--text1', '-1', required=True, help='Texto Sordo 1')
    parser.add_argument('--text2', '-2', required=True, help='Texto Sordo 2')
    parser.add_argument('--text3', '-3', required=True, help='Texto Sordo 3')
    parser.add_argument('--text4', '-4', required=True, help='Texto Sordo 4')
    parser.add_argument('--text5', '-5', required=True, help='Texto Sordo 5')
    parser.add_argument('--gps1', required=True, help='Coordenadas GPS 1 (latitud,longitud)')
    parser.add_argument('--gps2', required=True, help='Coordenadas GPS 2 (latitud,longitud)')
    parser.add_argument('--gps3', required=True, help='Coordenadas GPS 3 (latitud,longitud)')
    parser.add_argument('--gps4', required=True, help='Coordenadas GPS 4 (latitud,longitud)')
    parser.add_argument('--gps5', required=True, help='Coordenadas GPS 5 (latitud,longitud)')
    parser.add_argument('--id_sordo_1', required=True, help='ID de Sordo 1')
    parser.add_argument('--id_sordo_2', required=True, help='ID de Sordo 2')
    parser.add_argument('--id_sordo_3', required=True, help='ID de Sordo 3')
    parser.add_argument('--id_sordo_4', required=True, help='ID de Sordo 4')
    parser.add_argument('--id_sordo_5', required=True, help='ID de Sordo 5')
    parser.add_argument('--template', default="recursos/plantillaDigitalNuevosBotones.pdf", required=False, help='Plantilla a Utilizar')

    args = parser.parse_args()

    # Limpiar los GPS de paréntesis
    args.gps1 = args.gps1.replace("(", "").replace(")", "")
    args.gps2 = args.gps2.replace("(", "").replace(")", "")
    args.gps3 = args.gps3.replace("(", "").replace(")", "")
    args.gps4 = args.gps4.replace("(", "").replace(")", "")
    args.gps5 = args.gps5.replace("(", "").replace(")", "")

    # Generar PDF en memoria
    pdf_bytes, filename = llenarTerritorioImpreso(
        args.text1, args.text2, args.text3, args.text4, args.text5,
        args.territory_name,
        args.gps1, args.gps2, args.gps3, args.gps4, args.gps5,
        args.id_sordo_1, args.id_sordo_2, args.id_sordo_3, args.id_sordo_4, args.id_sordo_5,
        args.template
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
python territorioPDFimpreso.py  -1 "Texto 1" -2 "Texto 2" -3 "Texto 3 lorem ipsum estamos como estamos por que quereos ser muy felice spor la entrada de la autopsta ruminahui ddsa " -4 "Texto 4"     -5 "Texto 5 \n dsadas"  --gps1 "(-0.33096,-78.43727)" --gps2 "(-0.32815,-78.43665)" --gps3 "(-0.32581,-78.44173)" --gps4 "(-0.33317,-78.43452)" --gps5 "(-0.32770,-78.42725)" -n "Terracota A" --id_sordo_1 SS-031 --id_sordo_2 SS-032 --id_sordo_3 SS-033 --id_sordo_4 SS-034 --id_sordo_5 SS-035
'''