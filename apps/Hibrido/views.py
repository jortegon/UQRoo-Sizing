from django.shortcuts import render, redirect
from .forms import SolarForm  # Debo importar desde el forms las clases que  utilizaré aquí
from apps.Hibrido.models import Solar # probando csv
import math
import time
from random import random
from zipfile import ZipFile
import zipfile
import os
import shutil # Para eliminar directorio
from platypus import Problem, SMPSO, Integer, Real, nondominated
import numpy as np

from geopy.geocoders import Nominatim # Librería que me permite trabajar con geolocalización
import requests 
import json
import configparser

#.............................................

import matplotlib.pyplot as plt
from gpcharts import figure #https://github.com/Dfenestrator/GooPyCharts

# PARA EJEMPLO CSV 
import csv, io
from django.contrib import messages

MAIL = 'micorreo@sitio.com'
NREL_ID = 'asdifausifhlasjdnfasdf'

# Ejecutar django desde anaconda python manage.py runserver
def index(request):
    return render(request,'varios/index.html')

def Ubicacion(request): #Muestra la vista ubicación, donde el usuario ingresa el lugar donde desea el proyecto
    form = SolarForm()
    return render(request,'varios/ubicacion.html',{'SolarForm':form})
    
def Tipocarga(request):
    
    if request.method == "POST":
        p1 = SolarForm
        p1.municipioG = request.POST['municipio']
        p1.estadoG = request.POST['estado']
        p1.paisG = request.POST['pais']
    form = SolarForm 
    return render(request,'varios/home.html',{'SolarForm':form})

def Camino(request):
    if request.method == "POST":
        form = SolarForm()
        temporal = int(request.POST['elegir_carga'])
        if temporal == 1: # carga KWh/dia
            return render(request,'varios/carga.html',{'SolarForm':form})
        elif temporal == 2: # carga KWh/mes
            return render(request,'varios/carga_kwh_mes.html',{'SolarForm':form})
        elif temporal == 3: #KWh durante todo año
            return render(request,'varios/carga_kwh.html',{'SolarForm':form})
    else:
        return render(request,'varios/home.html')

def Paneles(request):
    if request.method == "POST":
        if request.POST['carga_o'] == "carga_o_kwh":
            p1 = SolarForm
            paramFile = request.FILES["carga_o"]
            data = paramFile.read().decode("utf-8").splitlines()
            reader = csv.DictReader(data)
            list1 = []
            for row in reader:
                list1.append(row)
            carga = []
            irradiancia = []
            velocidadDelViento = []
            for nombres in reader.fieldnames:# reader.fieldnames me da los nombres de los encabezados
                for dato in list1: #queda pendiente validar el tamaño de los datos subidos por el usuario 
                    if nombres == "carga":
                        carga.append(float(dato['carga']))
                    if nombres == "irradiancia":
                        if float(dato['irradiancia']) > 1.3: # En caso de que la irradiancia esté en Watt/m^2 lo convierto a KW/
                            irradiancia.append(float(dato['irradiancia']) / 1000)
                        else:
                            irradiancia.append(float(dato['irradiancia']))
                    if nombres == "velocidadviento":
                        velocidadDelViento.append(float(dato['velocidadviento']))
            p1.datos_carga = carga
            p1.Irradiancia = irradiancia
            p1.velocidad_vientos = velocidadDelViento
            
            
            p1.pruebaDatos =  list1     
            p1.estado = request.POST['carga_o']
        if request.POST['carga_o'] == "carga_o_mes":
            p1 = SolarForm
           
            paramFile = request.FILES["carga_o"]
            data = paramFile.read().decode("utf-8").splitlines()
            reader = csv.DictReader(data)
            list1 = []
            for row in reader:
                list1.append(row)
    
            carga = []
            irradiancia = []
            velocidadDelViento = []
            contador = 0
            for nombres in reader.fieldnames:# reader.fieldnames me da los nombres de los encabezados
                for dato in list1:
                    if nombres == "carga":
                        if contador < 12:
                            contador+=1
                            carga.append(float(dato['carga']))
                    if nombres == "irradiancia":
                        if float(dato['irradiancia']) > 1.3: # En caso de que la irradiancia esté en Watt/m^2 lo convierto a KW/
                            irradiancia.append(float(dato['irradiancia']) / 1000)
                        else:
                            irradiancia.append(float(dato['irradiancia']))
                    if nombres == "velocidadviento":
                        velocidadDelViento.append(float(dato['velocidadviento']))
        
            if len(carga) != 12:
                return render(request,'varios/index.html',{'error':'La carga debe ser un valor por cada mes'})
            
            p1.Irradiancia = irradiancia
            p1.velocidad_vientos = velocidadDelViento
            p1.datos_carga = carga
            p1.pruebaDatos =  list1
            p1.estado = request.POST['carga_o']
            
        if request.POST['carga_o'] == "carga_o":
            p1 = SolarForm
            p1.datos_carga = float(request.POST['carga'])
            p1.estado = request.POST['carga_o']  
        form = SolarForm()
        
        return render( request,'varios/energia_solar.html',{'SolarForm':form})
    else: 
        form = SolarForm()
    return render( request,'varios/energia_solar.html',{'SolarForm':form}) # despues de aquí seria bueno redireccionar a carga

def Viento(request):
    if request.method == "POST":
        p2 = SolarForm
        p2.elegir_solar = request.POST.get("elegir_energia_solar","off")
        p2.tipo_panel = int(request.POST['tipo_paneles'])
        form = SolarForm()
        return render( request,'varios/generador_eolico.html',{'SolarForm':form})
    else:
        form = SolarForm()
    return render( request,'varios/generador_eolico.html',{'SolarForm':form})

def Hidrogeno(request):
    if request.method == "POST":
        p3 = SolarForm
        p3.elegir_eolico  = request.POST.get('elegir_generador_eolico','off')
        p3.tipo_eolico = int(request.POST['tipo_generador_eolico'])
        form = SolarForm()
        return render( request,'varios/hidrogeno.html',{'SolarForm':form})
    else:
        form = SolarForm()
    return render( request,'varios/hidrogeno.html',{'SolarForm':form})

def Login(request):
    if request.method == "POST" and request.POST['login_name'] == "login_valor":
        if request.POST['loginPassword'] == "effpkk663":
            return render(request,'varios/login.html')
    return render(request,'varios/login.html')

def Configuracion(request):
    if request.method == "POST":
        form = SolarForm()
        return render(request,'varios/configuracion.html',{'SolarForm':form})
    return render(request,'varios/login.html')

def Resumen(request):
    if request.method == "POST":
        p3 = SolarForm
        carga = p3.datos_carga # Carga ingresada por el usuario ya sea  cuando elige KWh/dia o KWh/mes
        csv = p3.pruebaDatos # Carga leída de csv cuando el usuario elige KWh durante todo el año, es un diccionario
        elegir_solar = p3.elegir_solar
        tipo_panel = p3.tipo_panel
        
        elegir_eolico = p3.elegir_eolico
        tipo_eolico = p3.tipo_eolico
        
        elegir_celda  = request.POST.get('elegir_celda','off')
        p3.elegir_celdas = elegir_celda
        
        if p3.elegir_celdas == 'off':
            return render(request,'varios/index.html',{'error':"Debe seleccionar almacenamiento en Hidrógeno"})
        
        if p3.elegir_solar == 'off' and p3.elegir_eolico == 'off' and p3.elegir_celdas == 'on':
            return render(request,'varios/index.html',{'error':"Debe seleccionar al menos una fuente primaria (Solar o Eólica)"})
             
        tipo_celda = int(request.POST['tipo_celda'])
        p3.tipo_celdas = tipo_celda
        
        return render( request,'varios/resumen.html',{'carga':carga,'elegir_celda':elegir_celda,'tipo_celda':tipo_celda,'elegir_eolico':elegir_eolico,'tipo_eolico':tipo_eolico,'elegir_solar':elegir_solar,'tipo_panel':tipo_panel,'cvs':csv})

def ConfiguracionJson(request):
    return render(request,'varios/dato.json')

def Resultado(request):
    if (request.method) == 'GET':
        print('Quisiste entrar con GET..')
        return render(request,'varios/index.html',{'error':"Acceso inválido"}) 
        
    if(request.method == "POST"):
        if (request.POST['carga_o'] == 'configuracion'):
            configi = configparser.ConfigParser()
            # Lectura del archivo de configuración que sube el usuario
            data = request.FILES['carga_o']
            dato = data.read().decode("utf-8")#.splitlines()
            configDato  = json.loads(dato) #Convierte los datos joson a un diccionario python
            configi.read_dict(configDato)
            
            #Abro el archivo de configuración que usa el sistema para editarlo
            archivo = 'Templates/varios/dato.json'# Ruta donde se encuentra el archivo de configuración
            with open(archivo,'r') as f:
                config = json.load(f)
                for itemList in config:
                    for item in config[itemList]:
                        config[itemList][item] = configi.getfloat(itemList,item)
            
            #Guardo el archivo de configuración con los cambios realizados  
            with open(archivo,'w') as f:
                f.write(json.dumps(config))
            return render(request,'varios/index.html',{'exito':'Datos actualizados correctamente'})
        
        if(request.POST['carga_o'] == 'resumen'):
            inversor = {'eficienciaInversor':0,'factorPotencia':0,'factorSeguridad':0}
            panel_generico = {'area':0,'eficiencia':0,'potencia':0,'precio':0,'costoMantenimiento':0}
            panel_monocristalino = {'area':0,'eficiencia':0,'potencia':0,'precio':0,'costoMantenimiento':0}
            panel_policristalino = {'area':0,'eficiencia':0,'potencia':0,'precio':0,'costoMantenimiento':0}
            
            generador_generico = {'velocidadCorteInicio':0, 'velocidadCorteFinal':0, 'potenciaNominal':0, 'velocidadNominal':0,'precio':0,'costoMantenimiento':0} # Potencia nominal en KW Velocidad en m/s
            generador_horizontal = {'velocidadCorteInicio':0, 'velocidadCorteFinal':0, 'potenciaNominal':0, 'velocidadNominal':10,'precio':0,'costoMantenimiento':0} # Potencia nominal en KW Velocidad en m/s
            generador_vertical = {'velocidadCorteInicio':0, 'velocidadCorteFinal':0, 'potenciaNominal':0, 'velocidadNominal':0,'precio':0,'costoMantenimiento':0} # Potencia nominal en KW y Velocidad en m/s
            hidrogenoEnElTanque = 0
            #Obtener los valores de las constantes del archivo dato.json
            config = configparser.ConfigParser()
            archivo = 'Templates/varios/dato.json'
            with open(archivo,'r') as f:
                config = json.load(f)
            #Nuevos valores de las constantes 
            INTERES = config['economico']['INTERES']
            TIEMPOVIDAPROYECTO = float(config['economico']['TIEMPOVIDAPROYECTO'])
            eficienciaElectrolizador = float(config['celda']['eficienciaElectrolizador'])
            eficienciaCelda = float(config['celda']['eficienciaCelda'])
            hidrogenoEnElTanque = float(config['celda']['hidrogenoEnElTanque'])
    
            inversor = config['inversor']
            panel_generico = config['panelGenerico']
            panel_monocristalino = config['panelMonocristalino']
            panel_policristalino = config['panelPolicristalino']
            generador_generico = config['AerogeneradorGenerico']
            generador_horizontal = config['AerogeneradorHorizontal']
            generador_vertical = config['AerogeneradorVertical']
            
            print("RESUMEN")
            #return render(request,'varios/login.html')
        
    # Objeto de la clase SolarForm que contiene  todos los datos ingresados por el usuario
    p3 = SolarForm  
    
    # Datos de geolocalización y uso de la librería requests
    direccion = p3.municipioG + "," + p3.estadoG + "," + p3.paisG
    try:
        print("Obteniendo valores de latitud y longitud")
        geolocator = Nominatim(user_agent="prueba")
        location = geolocator.geocode(direccion)
        latitud = location.latitude
        longitud = location.longitude
        print(location)
    except:
        return render(request,'varios/index.html',{'error':"Error de conexión, no se pudo obtener latitud y longitud"})
        
    # Aquí se guardará la carga promedio ingresada por el usuario
    cargaHora = [] # Lista que maneja las cargas de todos los casos
    velocidadViento = []
    # Función que calcula el ángulo más apropiado dependiendo la latitud
    def angulo(x):
        return round((3.7 + 0.69 * x),2)
    
    # Función que obtiene la velocidad del viento desde los servidores de la NASA
    def consumir(latitud, longitud,solar,eolico):
        datos_irradiancia = []
        datos_velocidad_viento = []
        urls = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.json?names=2020&interval=60&utc=false&email="+MAIL
        urls = urls + "&attributes=solar_zenith_angle%2Cdni%2Cwind_speed%2Cair_temperature&wkt=POINT({0}+{1})".format(longitud,latitud)
        urls = urls + "&api_key=" + NREL_ID
        try:
            r = requests.post(urls)
            prueba = json.loads(r.text)
            for x in prueba:
                for x,y in prueba['outputs'].items():
                    if x=="downloadUrl":
                        time.sleep(5)
                        print(myfile.text)
                        if os.listdir('./datos_solar_eolico/')!=[]: # Si el directorio no está vacío
                            for root, dirs, files in os.walk('./datos_solar_eolico/', topdown=False): # Elimino todo el contenido del direct
                                for name in files:
                                    os.remove(os.path.join(root, name))
                                for name in dirs:
                                    os.rmdir(os.path.join(root, name))
                        open('./datos_solar_eolico/datos.zip', 'wb').write(myfile.content)
            stories_zip = zipfile.ZipFile('./datos_solar_eolico/datos.zip')# abro el documento
            for file in [x for x in stories_zip.namelist() if x.find('.csv')>0]:# obtengo los  nombres de todos los documentos que tienen extension csv
                direccion = file 
                stories_zip.extract(file, './datos_solar_eolico/')# Extraigo los archivos del zip
            url_local = './datos_solar_eolico/{}'.format(direccion) # Dirección de donde abriré el archivo con los datos que necesito
            nombre_archivo = open(url_local,'r')
            data = nombre_archivo.read().splitlines()
            reader = csv.DictReader(data)
            for row in reader:
                datos_irradiancia.append(row['Longitude']) #This column has the DNI data
                datos_velocidad_viento.append(row['Time Zone'])#This column has the wind speed data
            stories_zip.close() # Cierro la conexión del archivo zip
            del datos_irradiancia[0:2]
            del datos_velocidad_viento[0:2]
            datos_irradiancia = [float(datos_irradiancia[i]) / 1000 for i in range(len(datos_irradiancia))] # Convierto la irradiancia a KW/m^2
            datos_velocidad_viento = [float(datos_velocidad_viento[i]) for i in range(len(datos_velocidad_viento))]
            print(solar, eolico, len(datos_irradiancia), len(datos_velocidad_viento))
            if solar == "on" and eolico == "off":
                return datos_irradiancia
            if eolico == "on" and solar == "off":
                return datos_velocidad_viento
            if solar == "on" and eolico == "on":
                return datos_irradiancia, datos_velocidad_viento
        except:
            return render(request,'varios/index.html',{'error':"Error de conexión, no se pudo establecer conexión con el servidor del NREL"})
        
    estado = p3.estado # Almacena que tipo de carga se eligió. KWh/dia:carga_o , KWh/mes:carga_o_mes, KWh:carga_o_kwh
    bandera = False
    if estado == "carga_o": #CASO Cuando el usuario elige carga en kwh/dia
        # Carga ingresada por el usuario cuando elige KWh/dia o KWh/mes
        cargas = p3.datos_carga
        #Carga promedio por hora durante el día
        cargaTemporal = cargas / 24
        for i in range(8760):# 8760 es la cantidad de horas que tiene  un año
                cargaHora.append(round(cargaTemporal + cargaTemporal * 0.20 * (random()-0.5),2)) # 20% de variabilidad horaria
        bandera = True
        if p3.elegir_eolico == 'on' and p3.elegir_solar == 'off': # Si el usuario eligió incluir energía eólica en su dimensionamiento
            velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and p3.elegir_eolico == 'off':
            irradiancia = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and p3.elegir_eolico == 'on':
            irradiancia, velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
                
    if estado == "carga_o_mes": #CASO Cuando el usuario elige carga en kwh/mes
        # En el método paneles valido que solo sean 12 valores de carga, uno por mes
        # Tratamiento de la carga
        carga_provisional = p3.datos_carga # Obtengo los datos subidos por el usuario en el archivo csv
        carga = []
        dias_mes = [31,28,31,30,31,30,31,31,30,31,30,31]
        for idx, datos_carga in enumerate(carga_provisional):
            for i in range(dias_mes[idx]):
                carga.append(datos_carga + datos_carga * 0.10 * (random()-0.5)) # 10% de variabilidad diaria
        for z in carga:
            for p in range(24):
                cargaHora.append(round(z/24 + z/24 * 0.20 * (random()-0.5),2)) # 20% de variabilidad horaria
        if len(p3.velocidad_vientos) == 0 and p3.elegir_eolico == 'on' and p3.elegir_solar == 'off': # solo eolico, sin datos
            velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) == 0 and p3.elegir_eolico == 'off':# solo solar, sin datos
            irradiancia = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) != 0 and p3.elegir_eolico == 'off': # solo solar, con datos
            irradiancia = p3.Irradiancia # Revisar si la irraciancia es en Watt o Kilowatt en el webservice 
        if p3.elegir_eolico == 'on' and len(p3.velocidad_vientos) != 0 and p3.elegir_solar == 'off': # solo eolico, con datos
            velocidadViento = p3.velocidad_vientos
        if p3.elegir_solar == 'on' and p3.elegir_eolico == 'on': #  solar y eólica
            if len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) != 0:# datos solar y eolico
                irradiancia = p3.Irradiancia
                velocidadViento = p3.velocidad_vientos
            elif len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) == 0:# datos solar, eolico online
                irradiancia = p3.Irradiancia
                velocidadViento = consumir(latitud,longitud,'off',p3.elegir_eolico)
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) != 0:# datos eolico, solar online
                velocidadViento = p3.velocidad_vientos
                irradiancia = consumir(latitud,longitud,p3.elegir_solar,'off')
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) == 0: #sin datos
                irradiancia, velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
    if estado == "carga_o_kwh": #CASO cuando el usuario elige carga en kwh
        cargaHora = p3.datos_carga 
        if len(p3.velocidad_vientos) == 0 and p3.elegir_eolico == 'on' and p3.elegir_solar == "off": # Si el usuario no cargó el archivo con la velocidad del viento y eligió incluir energía eólica en su dimensionamiento
            velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) == 0 and p3.elegir_eolico == 'off':
            irradiancia = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) != 0 and p3.elegir_eolico == 'off': # Si el usuario subió un archivo con los valores de la irradiancia
            irradiancia = p3.Irradiancia # Revisar si la irraciancia es en Watt o Kilowatt en el webservice
            irradiancia = irradiancia
        if p3.elegir_eolico == 'on' and len(p3.velocidad_vientos) != 0 and p3.elegir_solar == 'off': # Si el usuario subió un archivo con las velocidades del viento
            velocidadViento = p3.velocidad_vientos    
        if p3.elegir_solar == 'on' and p3.elegir_eolico == 'on': # En caso que el usuario elija que quiere solar y eólica
            if len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) != 0:# Si el usuario subió mediante archivo csv la irradiancia y la velocidad del viento
                irradiancia = p3.Irradiancia
                velocidadViento = p3.velocidad_vientos
            elif len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) == 0:# subio valores de irradiancia , pero no subió valores de velocidad del viento
                irradiancia = p3.Irradiancia
                velocidadViento = consumir(latitud,longitud,'off',p3.elegir_eolico)
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) != 0:#No  subio valores de irradiancia , pero subió valores de velocidad del viento
                velocidadViento = p3.velocidad_vientos
                irradiancia = consumir(latitud,longitud,p3.elegir_solar, 'off')
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) == 0:
                irradiancia,velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
                
    # Función que calcula la potencia del inversor en función del tipo de carga seleccionado por el usuario           
    def potenciainversor(bandera):
        if bandera == True:
            print("Bandera: ",bandera)
            potenciaInversor = round(inversor['factorSeguridad'] * (cargaHora[0] / inversor['factorPotencia'] * inversor['eficienciaInversor']),2) # cargaHora[0] carga consumida en una hora
        else:
            cargaEnUnaHora = max(cargaHora)
            potenciaInversor = round(inversor['factorSeguridad'] * (cargaEnUnaHora / inversor['factorPotencia'] * inversor['eficienciaInversor']),2) # cargaEnUnaHora carga máxima consumida en una hora
        return potenciaInversor       
        
    # Datos económicos
    factorRecuperacionCapital =  (INTERES * (1+INTERES)**TIEMPOVIDAPROYECTO) / ((1+INTERES)**TIEMPOVIDAPROYECTO -1)
    
    # Función que calcula la potencia del electrolizador y la celda de combustible(ok)
    def tamano(potenciaSolar, carga, inversor, eficienciaCelda, eficienciaElectrolizador, hidrogenoInicialTanque):
        potencia_electrolizador = []
        potencia_electrolizador.append(hidrogenoInicialTanque) # Establezco el tamaño del tanque inicial en el tamaño de la cantidad de hidrógeno inicial
        potencia_celda = []
        for tamano_i in range(len(potenciaSolar)):
            if potenciaSolar[tamano_i] > carga[tamano_i]:
                electrolizador = round(eficienciaElectrolizador * (potenciaSolar[tamano_i] - (carga[tamano_i] / inversor)),2)
                potencia_electrolizador.append(electrolizador)
            else:
                celdaCombustible = round(-((carga[tamano_i] / inversor) - potenciaSolar[tamano_i]) / eficienciaCelda,2)
                potencia_celda.append(-1 * celdaCombustible)
        return (max(potencia_electrolizador), max(potencia_celda))
    
    #Función que calcula la eficiencia global  en función de la energía total producida y la energía total consumida
    def EficienciaGlobal(energia, carga, inversor, eficienciaElectrolizador, hidrogenoInicialTanque, eficienciaCelda):
        historialHidrogenoTanque = [] # Cantidad de H2 en cada hora dentro del tanque
        historialHidrogenoTanque.append(hidrogenoInicialTanque)
        energiaProducida = []
        eficienciaSistema = []
        producida = 0
        for j in range(len(energia)):
            if energia[j] >= (carga[j] / inversor):
                electrolizador = eficienciaElectrolizador * (energia[j] - (carga[j] / inversor))
                electrolizador = abs(round(electrolizador,2)) # Si la diferencia de energia solar y la carga es demasiado chica, puede dar resul negat
                #LPSP
                #producida = (energia[j] - electrolizador) * inversor
                producida = energia[j]
                energiaProducida.append(producida)
                eficienciaSistema.append(carga[j] - energiaProducida[j])
                # FIN LPSP 
            else:
                celdaCombustible = ((carga[j] / inversor) - energia[j]) / eficienciaCelda
                celdaCombustible = abs(round(celdaCombustible,2))
                #LPSP
                producida = (energia[j] + celdaCombustible) * inversor
                energiaProducida.append(producida)
                eficienciaSistema.append(carga[j] - energiaProducida[j])
                #FIN LPSP
        resultado = abs(round(sum(carga)/sum(energiaProducida),2))
        return round(resultado * 100,2)

    #Función que calcula el tamaño máximo que debe tener el tanque de H2
    def TamanoTanque(carga, energiaSolar, hidrogenoIniTanque, inversor, eficienciaCelda, eficienciaElectrolizador):
        tamanoActuaTanque = hidrogenoIniTanque
        tamano_tanque_hidrogeno = []
        tamano_tanque_hidrogeno.append(tamanoActuaTanque)# inicializo el tamaño del tanque
        for tama in range(len(energiaSolar)):
            if energiaSolar[tama] > carga[tama]:
                electrolizador = eficienciaElectrolizador * (energiaSolar[tama] - (carga[tama] / inversor))
                electrolizador = round(electrolizador,2)
                tamano_tanque_hidrogeno.append(tamano_tanque_hidrogeno[tama] + electrolizador)
            else:
                celdaCombustible = ((carga[tama] / inversor) - energiaSolar[tama]) / eficienciaCelda
                celdaCombustible = round(celdaCombustible,2)
                tamano_tanque_hidrogeno.append(tamano_tanque_hidrogeno[tama] - celdaCombustible)   
        return round(max(tamano_tanque_hidrogeno),2)
         
    # Función que genera energía eólica con el Aerogenerador durante un periodo de un año 
    def potenciaEolica(generador=generador_generico): 
        potenciaAerogenerador= []
        for i in range(len(velocidadViento)):
            if velocidadViento[i] < generador['velocidadCorteInicio'] or velocidadViento[i]  >= generador['velocidadCorteFinal']:
                potenciaAerogenerador.append(0)
            elif velocidadViento[i] >= generador['velocidadNominal'] and velocidadViento[i] < generador['velocidadCorteFinal']:
                potenciaAerogenerador.append(generador['potenciaNominal'])
            elif velocidadViento[i] >= generador['velocidadCorteInicio'] and velocidadViento[i] < generador['velocidadNominal']:
                calculoPotencia = generador['potenciaNominal'] * ((velocidadViento[i] - generador['velocidadCorteInicio']) / (generador['velocidadNominal'] - generador['velocidadCorteInicio']))
                potenciaAerogenerador.append(calculoPotencia)
        return potenciaAerogenerador

    #Calcula la potencia de salida de un panel solar generico durante un periodo de un año
    def PotenciaSolar(panel=panel_generico):
        potenciaSolarPanel= []
        for indiceSolar in range(len(irradiancia)):
            potenciaSolarPanel.append(panel['area'] * panel['eficiencia'] * irradiancia[indiceSolar])
        return potenciaSolarPanel



  
    if p3.elegir_solar == 'off' and p3.elegir_eolico == 'off' and p3.elegir_celdas == 'on':
        return render(request,'varios/index.html',{'error':"Debe seleccionar al menos una fuente primaria (Solar o Eólica)"})
       
    elif p3.elegir_solar == 'on' and p3.elegir_eolico == 'off' and p3.elegir_celdas == 'on': # Funciona para Energía SOLAR e Hidrógeno
        solar = p3.elegir_solar
        eolico = "off"
        #latitude = 40
        #angulo_maxima_potencia = 90 -(latitude + 23) # Para solsticio de invierno
        #angulo_maxima_potencia = 90 -(latitude - 23) # Para verano
        # 23 es el angulo de inclinación de la tierra
        altura_objeto = 5 # Altura en metros
        angulo_maxima_potencia = angulo(latitud) # Llamo la función que calcula el ángulo óptimo
        #distancia_minima_filas_paneles = altura_objeto / (math.tan(61 - latitude))
        
        class Sizing(Problem):

            def __init__(self,panel = None):
                super(Sizing, self).__init__(1, 3, 2)
                self.types[:] = [Real(0, 5000)]
                self.constraints[:] = ">=0"
                self.pan = panel
                print('iniciando el problema')

    
            def evaluate(self, solution):
                x = solution.variables[0]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * self.pan['eficiencia'] for i in range(len(irradiancia))]
                contador = 0
                for hora in range(len(f1)):
                    generado = f1[hora] 
                    a_consumir = cargaHora[hora] /inversor['eficienciaInversor']
                    if generado >= a_consumir: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        excedente = (generado - a_consumir)
                        hidrogenoEnElTanque += eficienciaElectrolizador * excedente # El electrolizador genera Hidrógeno   
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        deficit = (a_consumir - generado)
                        contador = hidrogenoEnElTanque*eficienciaCelda - (deficit / eficienciaCelda) #podemos atender la carga completa     #CREO QUE NO ES NECESARIO 
                        hidrogenoEnElTanque -= (deficit) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
                costoCapitalAnual = factorRecuperacionCapital * (((x / self.pan['area']) * self.pan['precio']) )
                costoMantenimientoAnual = (x / self.pan['area']) * self.pan['costoMantenimiento'] 
#                return [x,costoCapitalAnual,costoMantenimientoAnual],[con,con1]
                solution.objectives[:] = [x,costoCapitalAnual,costoMantenimientoAnual]
                solution.constraints[:] = [con,con1]
        algorithm = 0       
        if p3.tipo_panel == 1:
            algorithm = SMPSO(Sizing(panel_generico))
            panel = panel_generico
        elif p3.tipo_panel == 2:
            algorithm = SMPSO(Sizing(panel_monocristalino))
            panel = panel_monocristalino
        elif p3.tipo_panel == 3:
            algorithm = SMPSO(Sizing(panel_policristalino))
            panel = panel_policristalino

        # optimize the problem using 10,000 function evaluations
        algorithm.run(10000)
        # display the results //// all solutions are the same
        solution = algorithm.result[0]
        print(solution.objectives)
        areaSolar = solution.objectives[0]
        numeropaneles = round((solution.objectives[0] / panel['area']),2)# Siempre redondeo un número arriba
        capital = round(solution.objectives[1],2)
        mantenimiento = round(solution.objectives[2],2)
            
        potenciaInversor = potenciainversor(bandera)
        #print("Irradiancia: ",irradiancia)
        energia = json.dumps(irradiancia)
        potenciaSolar = [round(float(areaSolar) * panel_generico['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
        
        #os.path.join(os.getcwd(),"Desktop")
        EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
        electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda

        tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
        #print("Potencia solar: ",potenciaSolar)
        potenciaS =  json.dumps(potenciaSolar) 
        load = json.dumps(cargaHora)
            
        context = {'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'energia':energia,'potenciaS':potenciaS,'load':load,'angulo_maxima_potencia':angulo_maxima_potencia,'potenciaInversor':potenciaInversor,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal}     
        return render( request,'varios/resultado.html',context)
                     
            
    elif p3.elegir_solar == 'off' and p3.elegir_eolico == 'on' and p3.elegir_celdas == 'on':
        eolico = p3.elegir_eolico
        solar = "off"
        class Sizing(Problem):

            def __init__(self,generador = None):
                super(Sizing, self).__init__(1, 3, 2)
                self.types[:] = [Real(0, 5000)]
                self.constraints[:] = ">=0"
                self.gen = generador
                self.potEolico = np.array(potenciaEolica(self.gen))
                print('iniciando el problema')

    
            def evaluate(self, solution):
                y = solution.variables[0]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f2 = y * self.potEolico   ####VERIFICAR SI EL POTENCIAL ES DE ACUERDO CON LOS VALORES DE CORTE
                contador = 0
                for hora in range(len(f2)):
                    generado = f2[hora] 
                    a_consumir = cargaHora[hora] /inversor['eficienciaInversor']
                    if generado >= a_consumir: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        excedente = (generado - a_consumir)
                        hidrogenoEnElTanque += eficienciaElectrolizador * excedente # El electrolizador genera Hidrógeno   
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        deficit = (a_consumir - generado)
                        contador = hidrogenoEnElTanque*eficienciaCelda - (deficit / eficienciaCelda) #podemos atender la carga completa     #CREO QUE NO ES NECESARIO 
                        hidrogenoEnElTanque -= (deficit) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
                costoCapitalAnual = factorRecuperacionCapital * (y * self.gen['precio'])
                costoMantenimientoAnual = (y * self.gen['costoMantenimiento'])
#                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]
                solution.objectives[:] = [y,costoCapitalAnual,costoMantenimientoAnual]
                solution.constraints[:] = [con,con1]
        if p3.tipo_eolico == 1: # Si el tipo de aerogenerador es el generico
            algorithm = SMPSO(Sizing(generador = generador_generico))
            generador = generador_generico
        elif p3.tipo_eolico == 2: # Si el tipo de aerogenerador es el horizontal
            algorithm = SMPSO(Sizing(generador = generador_horizontal))
            generador = generador_horizontal
        elif p3.tipo_eolico == 3: # Si el tipo de aerogenerador es el horizontal
            algorithm = SMPSO(Sizing(generador = generador_vertical))
            generador = generador_vertical

        # optimize the problem using 10,000 function evaluations
        algorithm.run(10000)

           
        # display the results //// all solutions are the same
        solution = algorithm.result[0]
        #print(solution.objectives)
        numero_aerogeneradores = solution.objectives[0]
        numeroaerogeneradores = round(solution.objectives[0],2)# Siempre redondeo un número arriba
        capital = round(solution.objectives[1],2)
        mantenimiento = round(solution.objectives[2],2)
        potenciaInversor = potenciainversor(bandera)
                
        # Datos para graficar
        velocidad_viento = json.dumps(velocidadViento)
        potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolica(generador)[i],2)  for i in range(len(potenciaEolica(generador)))]
            
        # Llamo la función que calcula tamaños elec y celda
        potenciaSolar = potenciaEolica
        EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
        electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
        tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
        print("Tamaño tanque: ",tamano_tanque_hidrogeno)
        potenciaE =  json.dumps(potenciaEolica) 
        load = json.dumps(cargaHora)
        context = {'numeroaerogeneradores':numeroaerogeneradores,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'velocidad_viento':velocidad_viento,'potenciaE':potenciaE,'load':load,'potenciaInversor':potenciaInversor,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal}
        return render( request,'varios/resultado.html',context)
        
           
           
    elif p3.elegir_solar == 'on' and p3.elegir_eolico == 'on' and p3.elegir_celdas == 'on':
        def sumalistas(a,b): # Suma dos listas para obtener la energía total eólica y solar en caso que el usuario elija las dos
            sumalista = []
            for i in range(len(a)):
                sumalista.append(a[i]+b[i])
            return sumalista
        
        angulo_maxima_potencia = angulo(latitud) # Llamo la función que calcula el ángulo óptimo
        solar = p3.elegir_solar
        eolico = p3.elegir_eolico
        #hidrogenoEnElTanque = 40
        class Sizing(Problem):

            def __init__(self,panel = None,generador = None):
                super(Sizing, self).__init__(2, 4, 2)
                self.types[:] = [Real(0, 5000), Real(0, 5000)]
                self.constraints[:] = ">=0"
                self.pan = panel
                self.gen = generador
                self.potEolico = np.array(potenciaEolica(self.gen))
                print('iniciando el problema')

    
            def evaluate(self, solution):
                x = solution.variables[0]
                y = solution.variables[1]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * self.pan['eficiencia'] for i in range(len(irradiancia))]
                f2 = y * self.potEolico   ####VERIFICAR SI EL POTENCIAL ES DE ACUERDO CON LOS VALORES DE CORTE
                contador = 0
                for hora in range(len(f1)):
                    generado = f1[hora] + f2[hora] 
                    a_consumir = cargaHora[hora] /inversor['eficienciaInversor']
                    if generado >= a_consumir: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        excedente = (generado - a_consumir)
                        hidrogenoEnElTanque += eficienciaElectrolizador * excedente # El electrolizador genera Hidrógeno   
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        deficit = (a_consumir - generado)
                        contador = hidrogenoEnElTanque*eficienciaCelda - (deficit / eficienciaCelda) #podemos atender la carga completa     #CREO QUE NO ES NECESARIO 
                        hidrogenoEnElTanque -= (deficit) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
                costoCapitalAnual = factorRecuperacionCapital * (((x / self.pan['area']) * self.pan['precio']) + (y * self.gen['precio']))
                costoMantenimientoAnual = (x / self.pan['area']) * self.pan['costoMantenimiento'] + (y * self.gen['costoMantenimiento'])
#                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]
                solution.objectives[:] = [x,y,costoCapitalAnual,costoMantenimientoAnual]
                solution.constraints[:] = [con,con1]

        if p3.tipo_panel == 1:
            panel = panel_generico
        elif p3.tipo_panel == 2:
            panel = panel_monocristalino
        elif p3.tipo_panel == 3:
            panel = panel_policristalino

        if p3.tipo_eolico == 1:
            generador = generador_generico
        elif p3.tipo_eolico == 2:
            generador = generador_horizontal
        elif p3.tipo_eolico == 3:
            generador = generador_vertical
        


        algorithm = SMPSO(Sizing(panel = panel, generador = generador))
        algorithm.run(10000)
            
   
        # display the results
        numeroaerogeneradores = []
        numeropaneles = []
        capital = []
        mantenimiento = []
        result = sorted(algorithm.result, key=lambda solution: solution.objectives[2])
        for solution in algorithm.result:
            print(solution.objectives)
            numero_aerogeneradores = round(solution.objectives[1]) if round(solution.objectives[1]) >= solution.objectives[1] else round(solution.objectives[1])+1 # Para la gráfica
            areaSolar = solution.objectives[0]# Para la gráfica
            #resultados.append(solution.objectives[0])
            numeroaerogeneradores.append(round(solution.objectives[1]) if round(solution.objectives[1]) >= solution.objectives[1] else round(solution.objectives[1])+1)# Siempre redondeo un número arriba
            numeropaneles.append(round(solution.objectives[0]) if round(solution.objectives[0]) >= solution.objectives[0] else round(solution.objectives[0])+1)
            capital.append(round(solution.objectives[2],2))
            mantenimiento.append(round(solution.objectives[3],2))
        zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
        potenciaInversor = potenciainversor(bandera)
        velocidad_viento = json.dumps(velocidadViento)
        potEolica = [round(float(numero_aerogeneradores) *  potenciaEolica(generador_generico)[i],2)  for i in range(len(potenciaEolica(generador_generico)))]
        energia = json.dumps(irradiancia)
        potSolar = [round(float(areaSolar) * panel_generico['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
        suma = sumalistas(potEolica,potSolar) # Suma de las potencia solar y eólica
        potenciaE =  json.dumps(suma)
            
        # Llamo la función que calcula tamaños elec y celda
        potSolar = suma
        EficienciaGlobal = EficienciaGlobal(potSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
        electrolizador, celda = tamano(potSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
        tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
        load = json.dumps(cargaHora)
        velocidad_viento = json.dumps(velocidadViento)
        return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
            
    return render( request,'varios/resultado.html',{'SolarForm':cargas})
# Create your views here.
