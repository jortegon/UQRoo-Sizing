from django.shortcuts import render, redirect
from .forms import SolarForm  # Debo importar desde el forms las clases que  utilizaré aquí
from apps.Hibrido.models import Solar # probando csv
#from pyswarm import pso
import math
from random import random
from zipfile import ZipFile
import zipfile
import os
import shutil # Para eliminar directorio
#from pylab import *
from platypus import NSGAII, Problem, DTLZ2, SMPSO, OMOPSO, Real, nondominated
import numpy as np

from geopy.geocoders import Nominatim # Librería que me permite trabajar con geolocalización
import requests 
import json
#from configparser import ConfigParser  # Para el archivo de confifuración
import configparser


#.............................................

import matplotlib.pyplot as plt
from gpcharts import figure #https://github.com/Dfenestrator/GooPyCharts
#https://www.youtube.com/watch?v=P-tbaw_wLGk VIDEO de la explicacion de pso en python

# PARA EJEMPLO CSV 
import csv, io
from django.contrib import messages

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
            #print("request.POST['elegir_carga']: ",type (int(request.POST['elegir_carga'])),int(request.POST['elegir_carga']))
            return render(request,'varios/carga.html',{'SolarForm':form})
        elif temporal == 2: # carga KWh/mes
            #print("request.POST['elegir_carga']: ",type (int(request.POST['elegir_carga'])),int(request.POST['elegir_carga']))
            return render(request,'varios/carga_kwh_mes.html',{'SolarForm':form})
        elif temporal == 3: #KWh durante todo año
            #print("request.POST['elegir_carga']: ",type (int(request.POST['elegir_carga'])),int(request.POST['elegir_carga']))
            return render(request,'varios/carga_kwh.html',{'SolarForm':form})
    else:
        return render(request,'varios/home.html')

def Paneles(request):
    if request.method == "POST":
        #form = SolarForm(request.POST)
        if request.POST['carga_o'] == "carga_o_kwh":
            p1 = SolarForm
            paramFile = request.FILES["carga_o"]
            data = paramFile.read().decode("utf-8").splitlines()
            reader = csv.DictReader(data)
            #print("ESTO VA BUENO ESTA NOCHE: ",type(reader.fieldnames))
            list1 = []
            for row in reader:
                list1.append(row)
            carga = []
            irradiancia = []
            velocidadDelViento = []
            for nombres in reader.fieldnames:# reader.fieldnames me da los nombres de los encabezados
                for dato in list1: #queda pendiente validar el tamaño de los datos subidos por el usuario FALTA!!!
                    if nombres == "carga":
                        carga.append(float(dato['carga']))
                    if nombres == "irradiancia":
                        if float(dato['irradiancia']) > 1.3: # En caso de que la irradiancia esté en Watt/m^2 lo convierto a KW/
                            irradiancia.append(float(dato['irradiancia']) / 1000)
                        else:
                            irradiancia.append(float(dato['irradiancia']))
                        #irradiancia.append(float(dato['irradiancia']))
                    if nombres == "velocidadviento":
                        velocidadDelViento.append(float(dato['velocidadviento']))
            #if len(carga) != 8760:
                #return render(request,'varios/index.html',{'error':'La carga debe ser un valor por cada hora durante un año'})
            p1.datos_carga = carga
            p1.Irradiancia = irradiancia
            p1.velocidad_vientos = velocidadDelViento
            
            #exit()
            
            p1.pruebaDatos =  list1     
            #p1.datos_carga = float(request.POST['carga'])#............. salida good
            p1.estado = request.POST['carga_o']
            #print("float(request.POST['carga']): ",(request.POST['carga']))
        if request.POST['carga_o'] == "carga_o_mes":
            p1 = SolarForm
           
            paramFile = request.FILES["carga_o"]
            data = paramFile.read().decode("utf-8").splitlines()
            reader = csv.DictReader(data)
            #print("ESTO VA BUENO ESTA NOCHE: ",type(reader.fieldnames))
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
            #p1.datos_carga = float(request.POST['carga'])#............. salida good
            p1.estado = request.POST['carga_o']
            
        if request.POST['carga_o'] == "carga_o":
            p1 = SolarForm
            p1.datos_carga = float(request.POST['carga'])#............. salida good
            p1.estado = request.POST['carga_o']  
        form = SolarForm()
        
        return render( request,'varios/energia_solar.html',{'SolarForm':form})
    else: 
        form = SolarForm()
    return render( request,'varios/energia_solar.html',{'SolarForm':form}) # despues de aquí seria bueno redireccionar a carga, pensarlo......................

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
        #p3 = SolarForm
        form = SolarForm()
        return render(request,'varios/configuracion.html',{'SolarForm':form})
    return render(request,'varios/login.html')

def Resumen(request):
    if request.method == "POST":
        p3 = SolarForm
        carga = p3.datos_carga # Carga ingresada por el usuario ya sea  cuando elige KWh/dia o KWh/mes
        #print("Tipo de carga : ",p3.estado) # Permite conocer si la carga que eligió el usuario fue KWh/dia o KWh/mes
        # si es carga_o_kwh se que se refiere a KWh durante el año. carga_o_mes : carga mensual,carga_o : carga por día
        
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
#hidrogenoEnElTanque = 100
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
            
            #print("Secciones: ",config.sections())
            #print(type(config.get('economico','INTERES')['INTERES']))
            #print(configi.get('economico','INTERES'))
                    
            #Abro el archivo de configuración que usa el sistema para editarlo
            archivo = 'Templates/varios/dato.json'# Ruta donde se encuentra el archivo de configuración
            with open(archivo,'r') as f:
                config = json.load(f)
                #print("config.get('economico','INTERES'): ",config.get('economico','INTERES')['INTERES'])
                #print(type(config.get('economico','INTERES')['INTERES']))
                config['economico']['INTERES'] = configi.getfloat('economico','INTERES')
                
                config['economico']['TIEMPOVIDAPROYECTO'] = configi.getfloat('economico','TIEMPOVIDAPROYECTO')
                
                config['celda']['eficienciaElectrolizador'] = configi.getfloat('celda','eficienciaElectrolizador')
                
                config['celda']['eficienciaCelda'] = configi.getfloat('celda','eficienciaCelda')
                
                config['celda']['hidrogenoEnElTanque'] = configi.getfloat('celda','hidrogenoEnElTanque')
                
                config['inversor']['eficienciaInversor'] = configi.getfloat('inversor','eficienciaInversor')
                
                config['inversor']['factorPotencia'] = configi.getfloat('inversor','factorPotencia')
                
                config['inversor']['factorSeguridad'] = configi.getfloat('inversor','factorSeguridad')
                
                
                config['panelGenerico']['area'] = configi.getfloat('panelGenerico','area')
                
                config['panelGenerico']['eficiencia'] = configi.getfloat('panelGenerico','eficiencia')
                
                config['panelGenerico']['potencia'] = configi.getfloat('panelGenerico','potencia')
                
                config['panelGenerico']['precio'] = configi.getfloat('panelGenerico','precio')
                
                config['panelGenerico']['costoMantenimiento'] = configi.getfloat('panelGenerico','costoMantenimiento')
                
                config['panelMonocristalino']['area'] = configi.getfloat('panelMonocristalino','area')
                
                config['panelMonocristalino']['eficiencia'] = configi.getfloat('panelMonocristalino','eficiencia')
                
                config['panelMonocristalino']['potencia'] = configi.getfloat('panelMonocristalino','potencia')
                
                config['panelMonocristalino']['precio'] = configi.getfloat('panelMonocristalino','precio')
                config['panelMonocristalino']['costoMantenimiento'] = configi.getfloat('panelMonocristalino','costoMantenimiento')
                
                config['panelPolicristalino']['area'] = configi.getfloat('panelPolicristalino','area')
                config['panelPolicristalino']['eficiencia'] = configi.getfloat('panelPolicristalino','eficiencia')
                config['panelPolicristalino']['potencia'] = configi.getfloat('panelPolicristalino','potencia')
                config['panelPolicristalino']['precio'] = configi.getfloat('panelPolicristalino','precio')
                config['panelPolicristalino']['costoMantenimiento'] = configi.getfloat('panelPolicristalino','costoMantenimiento')
                
                config['AerogeneradorGenerico']['velocidadCorteInicio'] = configi.getfloat('AerogeneradorGenerico','velocidadCorteInicio')
                config['AerogeneradorGenerico']['velocidadCorteFinal'] = configi.getfloat('AerogeneradorGenerico','velocidadCorteFinal')
                config['AerogeneradorGenerico']['potenciaNominal'] = configi.getfloat('AerogeneradorGenerico','potenciaNominal')
                config['AerogeneradorGenerico']['velocidadNominal'] = configi.getfloat('AerogeneradorGenerico','velocidadNominal')
                config['AerogeneradorGenerico']['precio'] = configi.getfloat('AerogeneradorGenerico','precio')
                config['AerogeneradorGenerico']['costoMantenimiento'] = configi.getfloat('AerogeneradorGenerico','costoMantenimiento')
                
                config['AerogeneradorHorizontal']['velocidadCorteInicio'] = configi.getfloat('AerogeneradorHorizontal','velocidadCorteInicio')
                config['AerogeneradorHorizontal']['velocidadCorteFinal'] = configi.getfloat('AerogeneradorHorizontal','velocidadCorteFinal')
                config['AerogeneradorHorizontal']['potenciaNominal'] = configi.getfloat('AerogeneradorHorizontal','potenciaNominal')
                config['AerogeneradorHorizontal']['velocidadNominal'] = configi.getfloat('AerogeneradorHorizontal','velocidadNominal')
                config['AerogeneradorHorizontal']['precio'] = configi.getfloat('AerogeneradorHorizontal','precio')
                config['AerogeneradorHorizontal']['costoMantenimiento'] = configi.getfloat('AerogeneradorHorizontal','costoMantenimiento')
                
                config['AerogeneradorVertical']['velocidadCorteInicio'] = configi.getfloat('AerogeneradorVertical','velocidadCorteInicio')
                config['AerogeneradorVertical']['velocidadCorteFinal'] = configi.getfloat('AerogeneradorVertical','velocidadCorteFinal')
                config['AerogeneradorVertical']['potenciaNominal'] = configi.getfloat('AerogeneradorVertical','potenciaNominal')
                config['AerogeneradorVertical']['velocidadNominal'] = configi.getfloat('AerogeneradorVertical','velocidadNominal')
                config['AerogeneradorVertical']['precio'] = configi.getfloat('AerogeneradorVertical','precio')
                config['AerogeneradorVertical']['costoMantenimiento'] = configi.getfloat('AerogeneradorVertical','costoMantenimiento')
            
            #Guardo el archivo de configuración con los cambios realizados  
            with open(archivo,'w') as f:
                f.write(json.dumps(config))
            #print("ARCHIVO DE CONFIGURACIÓN")
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
    
            inversor['eficienciaInversor'] = float(config['inversor']['eficienciaInversor'])
            inversor['factorPotencia'] = float(config['inversor']['factorPotencia'])
            inversor['factorSeguridad'] = float(config['inversor']['factorSeguridad'])
            
            #print("inversor: ",inversor)
            panel_generico['area'] = float(config['panelGenerico']['area'])
            panel_generico['eficiencia'] = float(config['panelGenerico']['eficiencia'])
            panel_generico['potencia'] = float(config['panelGenerico']['potencia'])
            panel_generico['precio'] = float(config['panelGenerico']['precio'])
            panel_generico['costoMantenimiento'] = float(config['panelGenerico']['costoMantenimiento'])
            #print("panel_generico: ",panel_generico)
            panel_monocristalino['area'] = float(config['panelMonocristalino']['area'])
            panel_monocristalino['eficiencia'] = float(config['panelMonocristalino']['eficiencia'])
            panel_monocristalino['potencia'] = float(config['panelMonocristalino']['potencia'])
            panel_monocristalino['precio'] = float(config['panelMonocristalino']['precio'])
            panel_monocristalino['costoMantenimiento'] = float(config['panelMonocristalino']['costoMantenimiento'])
            #print("panel_mono",panel_monocristalino)
            panel_policristalino['area'] = float(config['panelPolicristalino']['area'])
            panel_policristalino['eficiencia'] = float(config['panelPolicristalino']['eficiencia'])
            panel_policristalino['potencia'] = float(config['panelPolicristalino']['potencia'])
            panel_policristalino['precio'] = float(config['panelPolicristalino']['precio'])
            panel_policristalino['costoMantenimiento'] = float(config['panelPolicristalino']['costoMantenimiento'])
            #print("panel_poli",panel_policristalino)
            generador_generico['velocidadCorteInicio'] = float(config['AerogeneradorGenerico']['velocidadCorteInicio'])
            generador_generico['velocidadCorteFinal'] = float(config['AerogeneradorGenerico']['velocidadCorteFinal'])
            generador_generico['potenciaNominal'] = float(config['AerogeneradorGenerico']['potenciaNominal'])
            generador_generico['velocidadNominal'] = float(config['AerogeneradorGenerico']['velocidadNominal'])
            generador_generico['precio'] = float(config['AerogeneradorGenerico']['precio'])
            generador_generico['costoMantenimiento'] = float(config['AerogeneradorGenerico']['costoMantenimiento'])
            #print("generador_generico: ",generador_generico)
            generador_horizontal['velocidadCorteInicio'] = float(config['AerogeneradorHorizontal']['velocidadCorteInicio'])
            generador_horizontal['velocidadCorteFinal'] = float(config['AerogeneradorHorizontal']['velocidadCorteFinal'])
            generador_horizontal['potenciaNominal'] = float(config['AerogeneradorHorizontal']['potenciaNominal'])
            generador_horizontal['velocidadNominal'] = float(config['AerogeneradorHorizontal']['velocidadNominal'])
            generador_horizontal['precio'] = float(config['AerogeneradorHorizontal']['precio'])
            generador_horizontal['costoMantenimiento'] = float(config['AerogeneradorHorizontal']['costoMantenimiento'])
            #print("generador_horizontal: ",generador_horizontal)
            generador_vertical['velocidadCorteInicio'] = float(config['AerogeneradorVertical']['velocidadCorteInicio'])
            generador_vertical['velocidadCorteFinal'] = float(config['AerogeneradorVertical']['velocidadCorteFinal'])
            generador_vertical['potenciaNominal'] = float(config['AerogeneradorVertical']['potenciaNominal'])
            generador_vertical['velocidadNominal'] = float(config['AerogeneradorVertical']['velocidadNominal'])
            generador_vertical['precio'] = float(config['AerogeneradorVertical']['precio'])
            generador_vertical['costoMantenimiento'] = float(config['AerogeneradorVertical']['costoMantenimiento'])
            #print("Genrador_vertical: ",generador_vertical)
            
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
        urls = "https://developer.nrel.gov/api/nsrdb/v2/solar/psm3-download.json?names=2020&interval=60&utc=false&email=ggq302@gmail.com&attributes=dhi%2Cdni%2Cwind_speed%2Cair_temperature&wkt=POINT({0}+{1})&api_key=nF0gcwQrZsPWndGwVbWSvXD93ixYYlPiO6CblOFF".format(longitud,latitud)
        try:
            r = requests.post(urls)
            prueba = json.loads(r.text)
            for x in prueba:
                for x,y in prueba['outputs'].items():
                    if x=="downloadUrl":
                        myfile = requests.get(y)
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
                datos_irradiancia.append(row['Latitude'])
                datos_velocidad_viento.append(row['Time Zone'])
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
        cargaHora.append(round(cargaTemporal,2))
        cargaHora = cargaHora * 8760 # 8760 es la cantidad de horas que tiene  un año
        bandera = True
        if len(p3.velocidad_vientos) == 0 and p3.elegir_eolico == 'on' and p3.elegir_solar == 'off': # Si el usuario no cargó el archivo con la velocidad del viento y eligió incluir energía eólica en su dimensionamiento
            velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) == 0 and p3.elegir_eolico == 'off':
            eolico = "off"
            irradiancia = consumir(latitud,longitud,p3.elegir_solar,eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) != 0 and p3.elegir_eolico == 'off': # Si el usuario subió un archivo con los valores de la irradiancia
            irradiancia = p3.Irradiancia 
        if p3.elegir_eolico == 'on' and len(p3.velocidad_vientos) != 0 and p3.elegir_solar == 'off': # Si el usuario subió un archivo con las velocidades del viento
            velocidadViento = p3.velocidad_vientos
        if p3.elegir_solar == 'on' and p3.elegir_eolico == 'on':
            if len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) != 0:# Si el usuario subió mediante archivo csv la irradiancia y la velocidad del viento
                irradiancia = p3.Irradiancia
                velocidadViento = p3.velocidad_vientos
            elif len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) == 0:# subio valores de irradiancia , pero no subió valores de velocidad del viento
                irradiancia = p3.Irradiancia
                solar = "off"
                velocidadViento = consumir(latitud,longitud,solar,p3.elegir_eolico)
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) != 0:# subio valores de irradiancia , pero no subió valores de velocidad del viento
                velocidadViento = p3.velocidad_vientos
                irradiancia = consumir(latitud,longitud,p3.elegir_solar,eolico = "off")
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) == 0:
                irradiancia, velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
                
    if estado == "carga_o_mes": #CASO Cuando el usuario elige carga en kwh/mes
        # En el método paneles valido que solo sean 12 valores de carga, uno por mes
        # Tratamiento de la carga
        carga_provisional = p3.datos_carga # Obtengo los datos subidos por el usuario en el archivo csv
        carga = []
        for datos_carga in carga_provisional:
            for i in range(31):
                carga.append(round(datos_carga + datos_carga * 0.10 * random(),2)) # Verificar esta conversión
        carga = carga[0:365]
        for z in carga:
            for p in range(24):
                cargaHora.append(z/24)
        if len(p3.velocidad_vientos) == 0 and p3.elegir_eolico == 'on' and p3.elegir_solar == 'off': # Si el usuario no cargó el archivo con la velocidad del viento y eligió incluir energía eólica en su dimensionamiento
            velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) == 0 and p3.elegir_eolico == 'off':
            irradiancia = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
        if p3.elegir_solar == 'on' and len(p3.Irradiancia) != 0 and p3.elegir_eolico == 'off': # Si el usuario subió un archivo con los valores de la irradiancia
            irradiancia = p3.Irradiancia # Revisar si la irraciancia es en Watt o Kilowatt en el webservice 
        if p3.elegir_eolico == 'on' and len(p3.velocidad_vientos) != 0 and p3.elegir_solar == 'off': # Si el usuario subió un archivo con las velocidades del viento
            velocidadViento = p3.velocidad_vientos
        if p3.elegir_solar == 'on' and p3.elegir_eolico == 'on': # En caso que el usuario elija que quiere solar y eólica
            if len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) != 0:# Si el usuario subió mediante archivo csv la irradiancia y la velocidad del viento
                irradiancia = p3.Irradiancia
                velocidadViento = p3.velocidad_vientos
            elif len(p3.Irradiancia) != 0 and len(p3.velocidad_vientos) == 0:# subio valores de irradiancia , pero no subió valores de velocidad del viento
                irradiancia = p3.Irradiancia
                solar = "off"
                velocidadViento = consumir(latitud,longitud,solar,p3.elegir_eolico)
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) != 0:# subio valores de irradiancia , pero no subió valores de velocidad del viento
                velocidadViento = p3.velocidad_vientos
                irradiancia = consumir(latitud,longitud,p3.elegir_solar,eolico = "off")
        elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) == 0:
            irradiancia, velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
    if estado == "carga_o_kwh": #CASO cuando el usuario elige carga en kwh
        cargaHora = p3.datos_carga 
        print("carga cuando el usuario elige carga en kwh: ",len(cargaHora))
        #cargaHora = cargaHora * 365 # Este código solo es para prueba, lo debo de quitar...........................................
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
                solar = "off"
                velocidadViento = consumir(latitud,longitud,solar,p3.elegir_eolico)
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) != 0:#No  subio valores de irradiancia , pero subió valores de velocidad del viento
                velocidadViento = p3.velocidad_vientos
                irradiancia = consumir(latitud,longitud,p3.elegir_solar, eolico ="off")
            elif len(p3.Irradiancia) == 0 and len(p3.velocidad_vientos) == 0:
                irradiancia,velocidadViento = consumir(latitud,longitud,p3.elegir_solar,p3.elegir_eolico)
                
    # Función que calcula la potencia del inversor en función del tipo de carga seleccionado por el usuario           
    def potenciainversor(bandera):
        if bandera == True:
            print("Bandera: ",bandera)
            potenciaInversor = round(inversor['factorSeguridad'] * (cargaHora[0] / inversor['factorPotencia'] * inversor['eficienciaInversor']),2) # cargaHora[0] carga consumida en una hora
        else:
            cargaEnUnaHora = max(cargaHora)#sum(cargaHora) / len(cargaHora) # sum(cargaHora) / len(cargaHora)
            potenciaInversor = round(inversor['factorSeguridad'] * (cargaEnUnaHora / inversor['factorPotencia'] * inversor['eficienciaInversor']),2) # cargaHora[0] carga consumida en una hora
        return potenciaInversor       
        
    # Datos económicos
    factorRecuperacionCapital =  (INTERES * (1+INTERES)**TIEMPOVIDAPROYECTO) / ((1+INTERES)**TIEMPOVIDAPROYECTO -1)
    
    # Función que calcula la potencia del electrolizador y la celda de combustible(ok)
    def tamano(potenciaSolar, carga, inversor, eficienciaCelda, eficienciaElectrolizador, hidrogenoInicialTanque):
        potencia_electrolizador = []
        potencia_electrolizador.append(hidrogenoInicialTanque) # Establezco el tamaño del tanque inicial en el tamaño de la cantidad de hidrógeno inicial
        potencia_celda = []
        for tamano in range(len(potenciaSolar)):
            if potenciaSolar[tamano] > carga[tamano]:
                electrolizador = round(eficienciaElectrolizador * (potenciaSolar[tamano] - (carga[tamano] / inversor)),2)
                potencia_electrolizador.append(electrolizador)
            else:
                celdaCombustible = round(-((carga[tamano] / inversor) - potenciaSolar[tamano]) / eficienciaCelda,2)
                potencia_celda.append(-1 * celdaCombustible)
        return (max(potencia_electrolizador), max(potencia_celda))
    
    #Función que calcula la eficiencia global  en función de la energía total producida y la energía total consumida
    def EficienciaGlobal(energiaSolar, carga, inversor, eficienciaElectrolizador, hidrogenoInicialTanque, eficienciaCelda):
        historialHidrogenoTanque = [] # Cantidad de H2 en cada hora dentro del tanque
        historialHidrogenoTanque.append(hidrogenoInicialTanque)
        energiaProducida = []
        eficienciaSistema = []
        producida = 0
        for j in range(len(energiaSolar)):
            if energiaSolar[j] > carga[j]:
                electrolizador = eficienciaElectrolizador * (energiaSolar[j] - (carga[j] / inversor))
                electrolizador = abs(round(electrolizador,2)) # Si la diferencia de energia solar y la carga es demasiado chica, puede dar resul negat
                #LPSP
                producida = (potenciaSolar[j] - electrolizador) * inversor
                energiaProducida.append(producida)
                eficienciaSistema.append(carga[j] - energiaProducida[j])
                # FIN LPSP 
            else:
                celdaCombustible = ((carga[j] / inversor) - energiaSolar[j]) / eficienciaCelda
                celdaCombustible = abs(round(celdaCombustible,2))
                #LPSP
                producida = (potenciaSolar[j] + celdaCombustible) * inversor
                energiaProducida.append(producida)
                eficienciaSistema.append(carga[j] - energiaProducida[j])
                #FIN LPSP
        #print("sum(eficienciaSistema) / sum(carga) xxx",sum(eficienciaSistema) / sum(carga))
        resultado = abs(round(sum(eficienciaSistema) / sum(carga),2))
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
         
    # Función que genera energía eólica con el Aerogenerador Generico durante un periodo de un año 
    def potenciaEolicaGenerico(): 
        potenciaAerogeneradorGenerico = []
        for i in range(len(velocidadViento)):
            if velocidadViento[i] < generador_generico['velocidadCorteInicio'] or velocidadViento[i]  >= generador_generico['velocidadCorteFinal']:
                potenciaAerogeneradorGenerico.append(0)
            elif velocidadViento[i] >= generador_generico['velocidadNominal'] and velocidadViento[i] < generador_generico['velocidadCorteFinal']:
                potenciaAerogeneradorGenerico.append(generador_generico['potenciaNominal'])
            elif velocidadViento[i] >= generador_generico['velocidadCorteInicio'] and velocidadViento[i] < generador_generico['velocidadNominal']:
                calculoPotencia = generador_generico['potenciaNominal'] * ((velocidadViento[i] - generador_generico['velocidadCorteInicio']) / (generador_generico['velocidadNominal'] - generador_generico['velocidadCorteInicio']))
                potenciaAerogeneradorGenerico.append(calculoPotencia)
        return potenciaAerogeneradorGenerico
    
    # Función que genera energía eólica con el Aerogenerador Horizontal durante un periodo de un año 
    def potenciaEolicaHorizontal(): 
        potenciaAerogeneradorHorizontal = []
        for j in range(len(velocidadViento)):
            if velocidadViento[j] < generador_horizontal['velocidadCorteInicio'] or velocidadViento[j]  >= generador_horizontal['velocidadCorteFinal']:
                potenciaAerogeneradorHorizontal.append(0)
            elif velocidadViento[j] >= generador_horizontal['velocidadNominal'] and velocidadViento[j] < generador_horizontal['velocidadCorteFinal']:
                potenciaAerogeneradorHorizontal.append(generador_horizontal['potenciaNominal'])
            elif velocidadViento[j] >= generador_horizontal['velocidadCorteInicio'] and velocidadViento[j] < generador_horizontal['velocidadNominal']:
                calculoPotencia = generador_horizontal['potenciaNominal'] * ((velocidadViento[j] - generador_horizontal['velocidadCorteInicio']) / (generador_horizontal['velocidadNominal'] - generador_horizontal['velocidadCorteInicio']))
                potenciaAerogeneradorHorizontal.append(calculoPotencia)
        return potenciaAerogeneradorHorizontal
    
    # Función que genera energía eólica con el Aerogenerador vertical durante un periodo de un año     
    def potenciaEolicaVertical(): 
        potenciaAerogeneradorVertical = []
        for k in range(len(velocidadViento)):
            if velocidadViento[k] < generador_vertical['velocidadCorteInicio'] or velocidadViento[k]  >= generador_vertical['velocidadCorteFinal']:
                potenciaAerogeneradorVertical.append(0)
            elif velocidadViento[k] >= generador_vertical['velocidadNominal'] and velocidadViento[k] < generador_vertical['velocidadCorteFinal']:
                potenciaAerogeneradorVertical.append(generador_vertical['potenciaNominal'])
            elif velocidadViento[k] >= generador_vertical['velocidadCorteInicio'] and velocidadViento[k] < generador_vertical['velocidadNominal']:
                calculoPotencia = generador_vertical['potenciaNominal'] * ((velocidadViento[k] - generador_vertical['velocidadCorteInicio']) / (generador_vertical['velocidadNominal'] - generador_vertical['velocidadCorteInicio']))
                potenciaAerogeneradorVertical.append(calculoPotencia)
        return potenciaAerogeneradorVertical
    
    #Calcula la potencia de salida de un panel solar generico durante un periodo de un año
    def PotenciaSolarGenerico():
        potenciaSolarPanelGenerico = []
        for indiceSolar in range(len(irradiancia)):
            potenciaSolarPanelGenerico.append(panel_generico['area'] * panel_generico['eficiencia'] * irradiancia[indiceSolar])
        return potenciaSolarPanelGenerico
  
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
        if p3.tipo_panel == 1:
            def belegundu(vars):
                celda = 0
                electrolizador = 0
                #* 2.3 KWh valor del tanque en kwh
                x = vars[0]
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_generico['eficiencia'] for i in range(len(irradiancia))]
                energiaProducidaMenosEnergiaConsumida = 0
                hidrogenoActualTanque = hidrogenoEnElTanque
                for hora in range(len(f1)):
                    if f1[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        #Eficienciaelectrolizador2 = ecuacion romeli
                        electrolizador = eficienciaElectrolizador * (f1[hora] - (cargaHora[hora] / inversor['eficienciaInversor']))
                        #print("Electrolizador: ",electrolizador)
                        energiaProducidaMenosEnergiaConsumida += electrolizador
                        hidrogenoActualTanque += electrolizador
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        #eficienciaCelda 2 = ecuacion romeli
                        celda = ((cargaHora[hora] / inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda
                        #print("celda: ",celda)
                        energiaProducidaMenosEnergiaConsumida -= celda    
                        hidrogenoActualTanque -= celda         
                  
                con = hidrogenoActualTanque
                con1 = energiaProducidaMenosEnergiaConsumida
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * ((x / panel_generico['area']) * panel_generico['precio'])
                costoMantenimientoAnual = factorRecuperacionCapital * (x / panel_generico['area']) * panel_generico['costoMantenimiento']  #[???] 
                return [x,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(1, 3, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)
            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
            # display the results
            for solution in algorithm.result:
                print(solution.objectives)
                #resultados.append(solution.objectives)# Resultados obtenidos con PSO
                areaSolar = solution.objectives[0]
                numeropaneles = round((solution.objectives[0] / panel_generico['area']),2)# Siempre redondeo un número arriba
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
        if p3.tipo_panel == 2:
            angulo_maxima_potencia = angulo(latitud) # Llamo la función que calcula el ángulo óptimo
            def belegundu(vars):
                x = vars[0]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_monocristalino ['eficiencia'] for i in range(len(irradiancia))]
                contador = 0
                for hora in range(len(f1)):
                    #lps = cargaHora - (f1[hora] + hidrogenoEnElTanque * eficienciaCelda) *inversor['eficienciaInversor']
                    #print("lps: ",lps)
                    if f1[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * (f1[hora] - (cargaHora[hora] / inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * (f1[hora] - (cargaHora[hora] / inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] / inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] / inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * ((x / panel_monocristalino['area']) * panel_monocristalino['precio'])
                costoMantenimientoAnual = (x / panel_monocristalino['area']) * panel_monocristalino['costoMantenimiento']   
                return [x,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(1, 3, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"
        
            problem.function = belegundu

            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
            
            # display the results
            for solution in algorithm.result:
                #print(solution.objectives)
                areaSolar = solution.objectives[0]
                numeropaneles = round(solution.objectives[0] / panel_generico['area'],2)
                capital = round(solution.objectives[1],2)
                mantenimiento = round(solution.objectives[2],2)
            
            potenciaInversor = potenciainversor(bandera) # Llamo la función que calcula la potencia del inversor
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_monocristalino['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            # Llamo la función que calcula tamaños elec y celda
            #os.path.join(os.getcwd(),"Desktop")
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda

            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            #print("Potencia solar: ",potenciaSolar)
            potenciaS =  json.dumps(potenciaSolar) 
            load = json.dumps(cargaHora)
            
            context = {'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'energia':energia,'potenciaS':potenciaS,'load':load,'angulo_maxima_potencia':angulo_maxima_potencia,'potenciaInversor':potenciaInversor,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal}     
            return render( request,'varios/resultado.html',context)
                     
          
        if p3.tipo_panel == 3:
            def belegundu(vars):
                x = vars[0]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_policristalino['eficiencia'] for i in range(len(irradiancia))]
                contador = 0
                for hora in range(len(f1)):
                    if f1[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * (f1[hora] - (cargaHora[hora] / inversor['eficienciaInversor']))
                        hidrogenoEnElTanque += eficienciaElectrolizador * (f1[hora] - (cargaHora[hora] / inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] / inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] / inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda     
                con = hidrogenoEnElTanque
                con1 = contador
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * ((x / panel_policristalino['area']) * panel_policristalino['precio'])
                costoMantenimientoAnual = (x / panel_policristalino['area']) * panel_policristalino['costoMantenimiento']   
                return [x,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(1, 3, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"
    
            problem.function = belegundu

            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            #Gráficar los resultados
         
            # display the results
            for solution in algorithm.result:
                #print(solution.objectives)
                areaSolar = solution.objectives[0]
                numeropaneles = math.ceil(solution.objectives[0] / panel_generico['area'])# Siempre redondeo un número arriba
                capital = round(solution.objectives[1],2)
                mantenimiento = round(solution.objectives[2],2)
                
            potenciaInversor = potenciainversor(bandera)
            
            # Datos para hacer las gráficas
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_policristalino['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            
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
        if p3.tipo_eolico == 1: # Si el tipo de aerogenerador es el generico
            def belegundu(vars):
                y = vars[0]
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                provisionalEolico = np.array(potenciaEolicaGenerico())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f2)):
                    if f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * (f2[hora] - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * (f2[hora] - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - f2[hora])  / eficienciaCelda
                        #np.append(contador,-(((cargaHora /inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda))
                        #contado = np.cumsum(contador)
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - f2[hora]) / eficienciaCelda
                        #print("Hidrógeno en tanque - : ",hidrogenoEnElTanque)
                   
                con = hidrogenoEnElTanque
                con1 = contador
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (y * generador_generico['precio'])
                costoMantenimientoAnual = factorRecuperacionCapital * (y * generador_generico['costoMantenimiento'])
                return [y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(1, 3, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"
            
            problem.function = belegundu

            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
           
            # display the results
            for solution in algorithm.result:
                #print(solution.objectives)
                numero_aerogeneradores = solution.objectives[0]
                numeroaerogeneradores = round(solution.objectives[0],2)# Siempre redondeo un número arriba
                capital = round(solution.objectives[1],2)
                mantenimiento = round(solution.objectives[2],2)
            potenciaInversor = potenciainversor(bandera)
                
            # Datos para graficar
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaGenerico()[i],2)  for i in range(len(potenciaEolicaGenerico()))]
            
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
        
        if p3.tipo_eolico == 2: # Si el tipo de aerogenerador es el horizontal
            def belegundu(vars):
                y = vars[0]
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                provisionalEolico = np.array(potenciaEolicaHorizontal())
                #print("provisionalEolico: ",provisionalEolico.sum())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f2)):
                    #lps = cargaHora - (f1[hora] + hidrogenoEnElTanque * eficienciaCelda) *inversor['eficienciaInversor']
                    #print("lps: ",lps)
                    if f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * (f2[hora] - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * (f2[hora] - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - f2[hora])  / eficienciaCelda
                        #np.append(contador,-(((cargaHora /inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda))
                        #contado = np.cumsum(contador)
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - f2[hora]) / eficienciaCelda
                        #print("Hidrógeno en tanque - : ",hidrogenoEnElTanque)
                   
                con = hidrogenoEnElTanque
                con1 = contador
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (y * generador_horizontal['precio'])
                costoMantenimientoAnual = factorRecuperacionCapital * (y * generador_horizontal['costoMantenimiento'])
                return [y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(1, 3, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"
        
            problem.function = belegundu

            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            #Gráficar los resultados
           
            # display the results
            for solution in algorithm.result:
                #print(solution.objectives)
                numero_aerogeneradores = round(solution.objectives[0],2)
                numeroaerogeneradores = round(solution.objectives[0],2)
                capital = round(solution.objectives[1],2)
                mantenimiento = round(solution.objectives[2],2)
            
            potenciaInversor = potenciainversor(bandera)
            
            # Datos para graficar
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaHorizontal()[i],2)  for i in range(len(potenciaEolicaHorizontal()))]
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = potenciaEolica
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            potenciaE =  json.dumps(potenciaEolica)
            #print("potenciaE: ",potenciaE)
            load = json.dumps(cargaHora)
            context = {'numeroaerogeneradores':numeroaerogeneradores,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'velocidad_viento':velocidad_viento,'potenciaE':potenciaE,'load':load,'potenciaInversor':potenciaInversor,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal}
            return render( request,'varios/resultado.html',context)
                    
        if p3.tipo_eolico == 3: # Si el tipo de aerogenerador es el vertical
            def belegundu(vars):
                y = vars[0] 
                provisionalEolico = np.array(potenciaEolicaVertical())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f2)):
                    if f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * (f2[hora] - (cargaHora[hora] /inversor['eficienciaInversor']))
                        hidrogenoEnElTanque += eficienciaElectrolizador * (f2[hora] - (cargaHora[hora] /inversor['eficienciaInversor'])) 
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - f2[hora])  / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - f2[hora]) / eficienciaCelda
                con = hidrogenoEnElTanque
                con1 = contador
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (y * generador_vertical['precio'])
                costoMantenimientoAnual = factorRecuperacionCapital * (y * generador_vertical['costoMantenimiento'])
                return [y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]
            problem = Problem(1, 3, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"
            problem.function = belegundu
            algorithm = SMPSO(problem)
            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
            # display the results
            for solution in algorithm.result:
                #print(solution.objectives)
                numero_aerogeneradores = round(solution.objectives[0],2)
                numeroaerogeneradores = round(solution.objectives[0],2)# Siempre redondeo un número arriba
                capital = round(solution.objectives[1],2)
                mantenimiento = round(solution.objectives[2],2)
            potenciaInversor = potenciainversor(bandera)
            velocidad_viento = json.dumps(velocidadViento)
            #print("velocidad_viento: ",velocidad_viento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaVertical()[i],2)  for i in range(len(potenciaEolicaVertical()))]
            potenciaSolar = potenciaEolica
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
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
        if p3.tipo_panel == 1 and p3.tipo_eolico == 1 and p3.tipo_celdas == 1:
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_generico['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaGenerico())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f1)):
                    if f1[hora] + f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno   
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_generico['area']) * panel_generico['precio']) + (y * generador_generico['precio']))
                costoMantenimientoAnual = (x / panel_generico['area']) * panel_generico['costoMantenimiento'] + (y * generador_generico['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]
            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"
            problem.function = belegundu
            algorithm = SMPSO(problem)
            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
   
            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = round(solution.objectives[1],2)# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            potenciaInversor = potenciainversor(bandera)
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaGenerico()[i],2)  for i in range(len(potenciaEolicaGenerico()))]
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_generico['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
            
        elif p3.tipo_panel == 1 and p3.tipo_eolico == 2 and p3.tipo_celdas == 1:
            
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                hidrogenoEnElTanque = 40 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_generico['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaHorizontal())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f1)):
                    if f1[hora] + f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno  
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda
                           
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_generico['area']) * panel_generico['precio']) + (y * generador_horizontal['precio']))
                costoMantenimientoAnual = (x / panel_generico['area']) * panel_generico['costoMantenimiento'] + (y * generador_horizontal['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            potenciaInversor = potenciainversor(bandera)
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaHorizontal()[i],2)  for i in range(len(potenciaEolicaHorizontal()))]
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_generico['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
            
        elif p3.tipo_panel == 1 and p3.tipo_eolico == 3 and p3.tipo_celdas == 1:
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_generico['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaVertical())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f1)):
                    if f1[hora] + f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                        
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda     
                con = hidrogenoEnElTanque
                con1 = contador
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_generico['area']) * panel_generico['precio']) + (y * generador_vertical['precio']))
                costoMantenimientoAnual = (x / panel_generico['area']) * panel_generico['costoMantenimiento'] + (y * generador_vertical['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
           
            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            potenciaInversor = potenciainversor(bandera)
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaVertical()[i],2)  for i in range(len(potenciaEolicaVertical()))]
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_generico['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
        
        elif p3.tipo_panel == 2 and p3.tipo_eolico == 1 and p3.tipo_celdas == 1:# ESTE CASO ESTÁ PENDIENTE, YA QUE DA MÁS
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                #hidrogenoEnElTanque = 21
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_monocristalino['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaGenerico())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f1)):
                    if f1[hora] + f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_monocristalino['area']) * panel_monocristalino['precio']) + (y * generador_generico['precio']))
                costoMantenimientoAnual = (x / panel_monocristalino['area']) * panel_monocristalino['costoMantenimiento'] + (y * generador_generico['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            #Gráficar los resultados
           
            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            
            potenciaInversor = potenciainversor(bandera)
            
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaGenerico()[i],2)  for i in range(len(potenciaEolicaGenerico()))]
            
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_monocristalino['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
               
        elif p3.tipo_panel == 2 and p3.tipo_eolico == 2 and p3.tipo_celdas == 1:
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                #hidrogenoEnElTanque = 21
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_monocristalino['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaHorizontal())
                f2 = y * provisionalEolico
                contador = 0
            
                for hora in range(len(f1)):
                    if f1[hora] + f2[hora] >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                        
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_monocristalino['area']) * panel_monocristalino['precio']) + (y * generador_horizontal['precio']))
                costoMantenimientoAnual = (x / panel_monocristalino['area']) * panel_monocristalino['costoMantenimiento'] + (y * generador_horizontal['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            
            potenciaInversor = potenciainversor(bandera)
            
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaHorizontal()[i],2)  for i in range(len(potenciaEolicaHorizontal()))]
            
            energia = json.dumps(irradiancia)
            potenciaSolar = [float(areaSolar) * panel_monocristalino['eficiencia'] * irradiancia[i] for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
               
        elif p3.tipo_panel == 2 and p3.tipo_eolico == 3 and p3.tipo_celdas == 1:
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                #hidrogenoEnElTanque = 21
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_monocristalino['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaVertical())
                f2 = y * provisionalEolico
                contador = 0
            
                for hora in range(len(f1)):
                    if (f1[hora] + f2[hora]) >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        #np.append(contador,-(((cargaHora /inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda))
                        #contado = np.cumsum(contador)
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda
                        #print("Hidrógeno en tanque - : ",hidrogenoEnElTanque)
                        #print("")        
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_monocristalino['area']) * panel_monocristalino['precio']) + (y * generador_vertical['precio']))
                costoMantenimientoAnual = (x / panel_monocristalino['area']) * panel_monocristalino['costoMantenimiento'] + (y * generador_vertical['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            
            potenciaInversor = potenciainversor(bandera)
            
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaVertical()[i],2)  for i in range(len(potenciaEolicaVertical()))]
            
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_monocristalino['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
                      
        elif p3.tipo_panel == 3 and p3.tipo_eolico == 1 and p3.tipo_celdas == 1:
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                #hidrogenoEnElTanque = 21
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_policristalino['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaGenerico())
                f2 = y * provisionalEolico
                contador = 0            
                for hora in range(len(f1)):
                    if (f1[hora] + f2[hora]) >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                        
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        #np.append(contador,-(((cargaHora /inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda))
                        #contado = np.cumsum(contador)
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda
                        #print("Hidrógeno en tanque - : ",hidrogenoEnElTanque)
                        #print("")        
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_policristalino['area']) * panel_policristalino['precio']) + (y * generador_generico['precio']))
                costoMantenimientoAnual = (x / panel_policristalino['area']) * panel_policristalino['costoMantenimiento'] + (y * generador_generico['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)
           
            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            
            potenciaInversor = potenciainversor(bandera)
            
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaGenerico()[i],2)  for i in range(len(potenciaEolicaGenerico()))]
            
            energia = json.dumps(irradiancia)
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
        elif p3.tipo_panel == 3 and p3.tipo_eolico == 2 and p3.tipo_celdas == 1:
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                #hidrogenoEnElTanque = 21
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_policristalino['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaHorizontal())
                f2 = y * provisionalEolico
                contador = 0
                for hora in range(len(f1)):
                    if (f1[hora] + f2[hora]) >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        #np.append(contador,-(((cargaHora /inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda))
                        #contado = np.cumsum(contador)
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda       
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_policristalino['area']) * panel_policristalino['precio']) + (y * generador_horizontal['precio']))
                costoMantenimientoAnual = (x / panel_policristalino['area']) * panel_policristalino['costoMantenimiento'] + (y * generador_horizontal['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            #Gráficar los resultados
           
            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            
            potenciaInversor = potenciainversor(bandera)
            
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaHorizontal()[i],2)  for i in range(len(potenciaEolicaHorizontal()))]
            
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_policristalino['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
               
        elif p3.tipo_panel == 3 and p3.tipo_eolico == 3 and p3.tipo_celdas == 1 :
            
            def belegundu(vars):
                x = vars[0]
                y = vars[1]
                #hidrogenoEnElTanque = 21
                hidrogenoEnElTanque = 10 #* 2.3 KWh valor del tanque en kwh
                # Calculos de la producción de energía de los paneles  
                f1 = [x * irradiancia[i] * panel_policristalino['eficiencia'] for i in range(len(irradiancia))]
                provisionalEolico = np.array(potenciaEolicaVertical())
                f2 = y * provisionalEolico
                contador = 0
            
                for hora in range(len(f1)):
                    if (f1[hora] + f2[hora]) >= cargaHora[hora]: # El electrolizador  produce hidrógeno con el exceso de energía (Superavit)
                        contador += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor']))
                        #a = np.append(contador,eficienciaElectrolizador * (f1[hora] - (cargaHora /inversor['eficienciaInversor'])))
                        #contado = np.cumsum(a)
                        hidrogenoEnElTanque += eficienciaElectrolizador * ((f1[hora] + f2[hora]) - (cargaHora[hora] /inversor['eficienciaInversor'])) # El electrolizador genera Hidrógeno 
                        #print("Hidrógeno en tanque + : ",hidrogenoEnElTanque)                      
                    else:# La celda de combustible quema hidrógeno del tanque para completar la energía que falta para suplir la carga (Deficit)
                        contador -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora]))  / eficienciaCelda
                        #np.append(contador,-(((cargaHora /inversor['eficienciaInversor']) - f1[hora]) / eficienciaCelda))
                        #contado = np.cumsum(contador)
                        hidrogenoEnElTanque -= ((cargaHora[hora] /inversor['eficienciaInversor']) - (f1[hora] + f2[hora])) / eficienciaCelda
                        #print("Hidrógeno en tanque - : ",hidrogenoEnElTanque)
                        #print("")        
                con = hidrogenoEnElTanque
                con1 = contador
      
                # Calculos de costos anualizados
                costoCapitalAnual = factorRecuperacionCapital * (((x / panel_policristalino['area']) * panel_policristalino['precio']) + (y * generador_vertical['precio']))
                costoMantenimientoAnual = (x / panel_policristalino['area']) * panel_policristalino['costoMantenimiento'] + (y * generador_vertical['costoMantenimiento'])
                return [x,y,costoCapitalAnual,costoMantenimientoAnual],[con,con1]

            problem = Problem(2, 4, 2) # (num de variables de decision,numero de objetivos,numero de restricciones)
            problem.types[:] = [Real(0, 1000),Real(0, 1000)]
            problem.constraints[0] = ">=0"
            problem.constraints[1] = ">=0"

            problem.function = belegundu
            # instantiate the optimization algorithm
            #algorithm = NSGAII(problem)
            #algorithm = OMOPSO(problem,0.05)
            algorithm = SMPSO(problem)

            # optimize the problem using 10,000 function evaluations
            algorithm.run(10000)

            # display the results
            numeroaerogeneradores = []
            numeropaneles = []
            capital = []
            mantenimiento = []
            for solution in algorithm.result:
                print(solution.objectives)
                numero_aerogeneradores = solution.objectives[1]# Para la gráfica
                areaSolar = solution.objectives[0]# Para la gráfica
                #resultados.append(solution.objectives[0])
                numeroaerogeneradores.append(round(solution.objectives[1],2))# Siempre redondeo un número arriba
                numeropaneles.append(round(solution.objectives[0],2))
                capital.append(round(solution.objectives[2],2))
                mantenimiento.append(round(solution.objectives[3],2))
            zlista = zip(numeropaneles,numeroaerogeneradores,capital,mantenimiento) # listas comprimidas
            
            potenciaInversor = potenciainversor(bandera)
            
            velocidad_viento = json.dumps(velocidadViento)
            potenciaEolica = [round(float(numero_aerogeneradores) *  potenciaEolicaVertical()[i],2)  for i in range(len(potenciaEolicaVertical()))]
            
            energia = json.dumps(irradiancia)
            potenciaSolar = [round(float(areaSolar) * panel_policristalino['eficiencia'] * irradiancia[i],2) for i in range(len(irradiancia))]
            suma = sumalistas(potenciaEolica,potenciaSolar) # Suma de las potencia solar y eólica
            potenciaE =  json.dumps(suma)
            
            # Llamo la función que calcula tamaños elec y celda
            potenciaSolar = suma
            EficienciaGlobal = EficienciaGlobal(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaElectrolizador, hidrogenoEnElTanque, eficienciaCelda)
            electrolizador, celda = tamano(potenciaSolar, cargaHora, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador, hidrogenoEnElTanque)# Llamo la función que calcula tamaños elec y celda
            tamano_tanque_hidrogeno = TamanoTanque(cargaHora, potenciaSolar, hidrogenoEnElTanque, inversor['eficienciaInversor'], eficienciaCelda, eficienciaElectrolizador)
            load = json.dumps(cargaHora)
            velocidad_viento = json.dumps(velocidadViento)
            return render( request,'varios/resultado.html',{'numeroaerogeneradores':numeroaerogeneradores,'numeropaneles':numeropaneles,'capital':capital,'mantenimiento':mantenimiento,'solar':solar,'eolico':eolico,'zlista':zlista,'potenciaInversor':potenciaInversor,'angulo_maxima_potencia':angulo_maxima_potencia,'velocidad_viento':velocidad_viento,'energia':energia,'potenciaE':potenciaE,'load':load,'electrolizador':electrolizador,'celda':celda,'tamano_tanque_hidrogeno':tamano_tanque_hidrogeno,'EficienciaGlobal':EficienciaGlobal})
                  
    return render( request,'varios/resultado.html',{'SolarForm':cargas})
# Create your views here.
