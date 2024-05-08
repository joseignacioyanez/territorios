import csv

import requests

with open('territorios.csv', 'w', newline='') as file:
    writer = csv.writer(file, lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, delimiter=',', escapechar='\\')
    field = ['WKT', 'nombre', 'descripción', 'detalles_direccion', 'estudio']

    writer.writerow(field)

    data = {'congregacion_id': 1}
    sordos =  requests.post('http://localhost:8000/api/sordos/para_kml_y_gpx/', json = data).json()

    for sordo in sordos:
        WKT = f"\"POINT ({sordo['gps_longitud']} {sordo['gps_latitud']})\""

        if sordo['territorio_nombre'] == "Estudios":
            estudio = "Estudio"
        else:
            estudio = "No Estudio"


        nombre = f"{sordo['codigo']} - {sordo['nombre']} - {sordo['anio_nacimiento']}".replace(',', ';')
        direccion = f"{sordo['direccion']}".replace(',', ';')
        detalles_direccion = f"{sordo['detalles_direccion']}".replace(',', ';')

        writer.writerow([WKT, nombre, direccion, detalles_direccion, estudio])

        