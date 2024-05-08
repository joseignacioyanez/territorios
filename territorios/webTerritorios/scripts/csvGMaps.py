import csv

import requests

with open('territorios.csv', 'w', newline='') as file:
    writer = csv.writer(file, lineterminator='\n', quoting=csv.QUOTE_NONE, quotechar=None, delimiter=',', escapechar='\\')
    field = ['WKT', 'nombre', 'descripción']

    writer.writerow(field)

    data = {'congregacion_id': 1}
    sordos =  requests.post('http://localhost:8000/api/sordos/para_kml_y_gpx/', json = data).json()

    for sordo in sordos:
        WKT = f"\"POINT ({sordo['gps_longitud']} {sordo['gps_latitud']})\""

        writer.writerow([WKT, f"{sordo['codigo']} - {sordo['nombre']} - {sordo['anio_nacimiento']}", f"{sordo['direccion']} -- {sordo['detalles_direccion']}"])