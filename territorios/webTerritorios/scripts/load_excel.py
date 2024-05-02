# Script usado como una vista para cargar datos de los sordos del Excel

'''
@csrf_exempt
def cargar_excel(request):
    df = pd.read_excel('Territorio2024.xlsx')
    df = df.replace({np.nan: None})

    local_id = codigo = nombre = tipo_senias = anio_nacimiento = telefono = direccion = gps_latitud = gps_longitud = detalles_sordo = detalles_familia = detalles_direccion = estado = ""
    for index, row in df.iterrows():

        local_id = row['id']
        codigo = row['codigo']
        nombre = "" if row['nombre'] is None else row['nombre']
        tipo_senias = "" if row['tipo_senias'] is None else row['tipo_senias']
        anio_nacimiento = row['anio_nacimiento']
        telefono = "" if row['telefono'] is None else row['telefono']
        direccion = "" if row['direccion'] is None else row['direccion']
        detalles_sordo = "" if row['detalles_sordo'] is None else row['detalles_sordo']
        detalles_familia = "" if row['detalles_familia'] is None else row['detalles_familia']
        detalles_direccion = "" if row['detalles_direccion'] is None else row['detalles_direccion']

        obj = Sordo(
            congregacion=Congregacion.objects.get(pk=1),
            local_id=local_id,
            codigo=codigo,
            nombre=nombre,
            tipo_senias=tipo_senias,
            anio_nacimiento=anio_nacimiento,
            telefono=telefono,
            direccion=direccion,
            gps_latitud=row['gps_latitud'],
            gps_longitud=row['gps_longitud'],
            detalles_sordo=detalles_sordo,
            detalles_familia=detalles_familia,
            detalles_direccion=detalles_direccion,
            estado_sordo=EstadoSordo.objects.get(nombre=row['estado']),
        )
        obj.save()
'''