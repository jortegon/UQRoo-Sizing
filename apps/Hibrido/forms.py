from django import forms
from .models import Solar
import io, csv
from django.core.files import File

class SolarForm(forms.ModelForm):
  
    class Meta:
        model = Solar
        fields = [
            'carga',
            'elegir_energia_solar',
            'tipo_paneles',
            'elegir_generador_eolico',
            'tipo_generador_eolico', 
            'elegir_celda',
            'tipo_celda', 
            'elegir_carga',
            'carga_o',
            'municipio',
            'estado',
            'pais'
          
            
        ]
        
        labels = {
            'carga': 'Ingrese la carga',
            'elegir_energia_solar' : 'Elegir fuente solar',
            'tipo_paneles': 'Tipo de panel',
            'elegir_generador_eolico':'Elegir generador eólico',
            'tipo_generador_eolico': 'Seleccione el tipo de generador',
            'elegir_celda':'Agregar almacenamiento en hidrogeno',
            'tipo_celda':'Elegir tipo de celda',
            'elegir_carga':'Elegir tipo de carga',
            'carga_o':'subir archivo',
            'municipio':'Municipio donde llevará a cabo el proyecto',
            'estado': 'Estado donde llevará a cabo el proyecto',
            'pais':'País donde llevará a cabo el proyecto',
            
          
             
            
        }
        
        widgets = {
            'carga': forms.TextInput(attrs={'class':'form-control'}),
            'elegir_energia_solar' : forms.CheckboxInput(attrs={'class':'form-control','onchange':'javascript:showContent()'}),
            'tipo_paneles': forms.Select(attrs={'class':'form-control'}),
            'elegir_generador_eolico': forms.CheckboxInput(attrs={'class':'form-control','onclick':'showContent()'}),
            'tipo_generador_eolico': forms.Select(attrs={'class':'form-control'}),
            'elegir_celda': forms.CheckboxInput(attrs={'class':'form-control','onclick':'showContent()'}),
            'tipo_celda': forms.Select(attrs={'class':'form-control'}),
            'elegir_carga': forms.Select(attrs={'class':'form-control'}),
            'carga_o': forms.FileInput(attrs={'class':'form-control-file'}),
            'municipio': forms.TextInput(attrs={'class':'form-control'}),
            'estado': forms.TextInput(attrs={'class':'form-control'}),
            'pais':forms.TextInput(attrs={'class':'form-control'}),
           
             #'archivo': CustomClearableFileInput FileInput
        }
    datos_carga = "" # Aquí almaceno la carga que el usuario ingresa en el formulario carga.html
    elegir_solar = ""  # Aquí almaceno los datos del la energía solar que el usuario ingresa en el formulario energia_solar.html
    tipo_panel = 0 # Aquí almaceno los datos del la energía eólica que el usuario ingresa en el formulario generador_eolico.html
    elegir_eolico = ""
    tipo_eolico = 0
    
    elegir_celdas = ""
    tipo_celdas = 0
    estado = "" # permite conocer el tipo de carga seleccionada por el usuario
    
    datos = {'datos_carga':datos_carga,'elegir_solar':elegir_solar,'tipo_panel':tipo_panel,'elegir_eolico':elegir_eolico,'tipo_eolico':tipo_eolico,'elegir_celdas':elegir_celdas,'tipo_celdas':tipo_celdas}
    Irradiancia = "" # Almacena la irradiancia solar cargada por el usuario desde el archivo csv
    velocidad_vientos = "" # Almacena la velocidad del viento cargada por el usuario desde el archivo csv
   
    pruebaDatos = "" # Almaceno los datos del usuario subidos por archivo csv
    municipioG = ""
    estadoG = ""
    paisG = ""
    
    #print("ppmunicipioG: ",municipioG)
    
   
   
    
        
    
        
        

    # forms.TextInput(attrs={'class':'form-control'})