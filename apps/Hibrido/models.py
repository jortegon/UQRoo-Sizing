from django.db import models

tipo_paneles = [
    (1, 'Panel genérico'),
    (2, 'Panel Monocristalino'),
    (3, 'Panel Policristalino'),   
]

tipo_generador_eolico = [
    (1, 'Generador eólico genérico'),
    (2, 'Generador eólico horizontal'),
    (3, 'Generador eólico vertical'),  
]

tipo_celdas = [
    (1, 'Celda tipo PEM'),
    (2, 'Alcalina'),
        
]

tipo_carga = [
    (1, 'KWh/día'),
    (2, 'KWh/mes'),
    (3, 'KWh'),
        
]

class Solar(models.Model):
    carga = models.TextField('Carga demandada por el sistema',blank = False, null = False) # Carga
    
    elegir_energia_solar = models.BooleanField('Agregar energía solar',blank = True, null = True)# Datos referentes a la energía solar
    tipo_paneles = models.CharField('Seleccione el tipo de panel',
        max_length=255,
        choices = tipo_paneles,
        default='Panel genérico',
    )
    
    
    elegir_generador_eolico = models.BooleanField('Agregar generador eólico',blank = True, null = True) #Datos referentes a la energía eólica
    tipo_generador_eolico = models.CharField('Seleccione el tipo de generador eólico',
        max_length=255,
        choices = tipo_generador_eolico,
        default='Generador eólico genérico',
    )
    
    elegir_celda = models.BooleanField('Agregar almacenamiento en Hidrógeno',blank = True, null = True) #Datos referentes a la energía eólica
    tipo_celda = models.CharField('Seleccione el tipo de celda',
        max_length=255,
        choices = tipo_celdas,
        default='Celda tipo PEM',
    )
    
    elegir_carga = models.CharField('Seleccione el tipo de carga',
        max_length=255,
        choices = tipo_carga,
        default='KWh/día',
    )
    
    #Para el ejemplo de csv
    titulo = models.CharField(max_length=50)
    carga_o = models.FileField()
    
    municipio = models.TextField('Municipio',blank = False, null = False)
    estado = models.TextField('Estado',blank = False, null = False)
    pais = models.TextField('País',blank = False, null = False)
   
    
 
  
    
    



# Create your models here.
