import boto3
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
import pandas as pd
from sklearn.linear_model import LinearRegression
from datetime import datetime, timedelta

from .forms import RegistroForm
from .models import Datos, HorarioMantencion

def inicio(request):
    return render(request, 'inicio.html')

def horarios(request):
    horario = HorarioMantencion.objects.first()
    return render(request, 'horarios.html', {'horario': horario})

def registro(request):
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('inicio')
    else:
        form = RegistroForm()
    return render(request, 'registro.html', {'form': form})

def inicio_sesion(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')
        else:
            return render(request, 'login.html', {'error': 'Credenciales incorrectas'})
    return render(request, 'login.html')

@login_required
def datos(request):
    return render(request, 'datos.html')

@login_required
def guardar_datos(request):
    if request.method == "POST":
        dia = request.POST['dia']
        clientes = request.POST['clientes']

        nueva_datos = Datos(dia=dia, clientes=clientes)
        nueva_datos.save()

        messages.success(request, 'Datos guardados correctamente')
        return redirect('datos')

    return render(request, 'datos.html')

def prediccion_view(request):
    if request.method == "POST":
        fechas_rango = request.POST.get('fechas')
        fecha_inicio, fecha_fin = fechas_rango.split(' - ')
        fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
        resultados = predecir_para_rango_fechas(fecha_inicio, fecha_fin)
        dia_menos_clientes = min(resultados, key=lambda x: x['prediccion_clientes'])
        HorarioMantencion.objects.update_or_create(
            defaults={
                'dia_mantencion': dia_menos_clientes['dia'].strftime('%A'),
                'horario_inicio': '08:00:00',
                'horario_fin': '19:00:00',
            }
        )

        return render(request, 'prediccion.html', {'resultados': resultados, 'fechas_rango': fechas_rango})

    return render(request, 'prediccion.html')

def predecir_para_rango_fechas(fecha_inicio, fecha_fin):
    datos = Datos.objects.all().values('dia', 'clientes')
    df = pd.DataFrame(datos)
    df['dia'] = pd.to_datetime(df['dia'])
    df['semana_anio'] = df['dia'].dt.isocalendar().week
    df['dia_semana'] = df['dia'].dt.dayofweek 

    X = df[['semana_anio', 'dia_semana']]
    y = df['clientes']

    modelo = LinearRegression()
    modelo.fit(X, y)

    
    fechas = pd.date_range(start=fecha_inicio, end=fecha_fin, freq='D')

    futuros_datos = pd.DataFrame({
        'dia': fechas,
        'semana_anio': fechas.isocalendar().week,
        'dia_semana': fechas.dayofweek
    })

    predicciones = modelo.predict(futuros_datos[['semana_anio', 'dia_semana']])
    futuros_datos['prediccion_clientes'] = predicciones

    resultados = futuros_datos[['dia', 'prediccion_clientes']].to_dict(orient='records')
    return resultados

def ver_datos(request):
    datos = Datos.objects.all()
    return render(request, 'ver_datos.html', {'datos': datos})


def eliminar_dato(request, dato_id):
    dato = get_object_or_404(Datos, id=dato_id)
    dato.delete()
    return redirect('ver_datos')

def modificar_dato(request, dato_id):
    dato = get_object_or_404(Datos, id=dato_id)
    
    if request.method == "POST":
        dia = request.POST.get('dia')
        clientes = request.POST.get('clientes')
        dato.dia = dia
        dato.clientes = clientes
        dato.save()
        return redirect('ver_datos')
    
    return redirect('ver_datos')

def upload_file_to_s3(request):
    if request.method == 'POST' and request.FILES['file']:
        file = request.FILES['file']
        fs = FileSystemStorage()
        filename = fs.save(file.name, file)
        file_path = fs.url(filename)
        s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        try:
            s3.upload_file(file_path[1:], settings.AWS_STORAGE_BUCKET_NAME, file.name)
            return HttpResponse(f'Archivo "{file.name}" subido exitosamente a S3!')
        except Exception as e:
            return HttpResponse(f'Error al subir el archivo: {e}')

    return render(request, 'upload.html')
@login_required
def exportar_excel(request):
    fechas_rango = request.POST.get('fechas')
    if not fechas_rango:
        return redirect('prediccion')

    # Obtener las fechas y ejecutar la predicción
    fecha_inicio, fecha_fin = fechas_rango.split(' - ')
    fecha_inicio = datetime.strptime(fecha_inicio, '%Y-%m-%d').date()
    fecha_fin = datetime.strptime(fecha_fin, '%Y-%m-%d').date()
    resultados = predecir_para_rango_fechas(fecha_inicio, fecha_fin)

    # Convertir resultados a DataFrame
    df = pd.DataFrame(resultados)

    # Crear la respuesta de descarga en formato Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=prediccion_clientes.xlsx'
    df.to_excel(response, index=False, sheet_name='PrediccionClientes')

    return response