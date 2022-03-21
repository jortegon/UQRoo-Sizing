# UQRoo-Sizing
Herramienta para el dimensionamiento de sistemas hibridos
Antes de usar la aplicación es necesario que se cuente con una cuenta para usar el API de NREL,
además se debe contar con una cuenta de correo electrónico válida donde se recibirá el enlace al 
archivo con los datos de irradiancia y velocidad del viento.
Ingresarla en apps/Hibrido/views.py
como sigue:
NREL_ID = asdifausifhlasjdnfasdf
USER_Mail = micorreo@sitio.com



Es recomendable manejar un ambiente virtual para la aplicación, puede venv o cualquier otro
Desde un directorio superior a la aplicación usar
#python3 -m venv UQRoo-Sizing

Cambiarse al directorio de la aplicación
#cd UQRoo-sizing

Activar el ambiente virtual
#. bin/activate
o de forma alternativa
#source bin/activate

Los paquetes requiridos son 
* django
* platypus-opt
* numpy
* geopy
* requests
* configparser
* matplotlib
* gpcharts
* future

Estos paquetes se pueden instalar usando pip3
#pip3 install django platypus-opt numpy geopy requests configparser matplotlib gpcharts future

Para ejecutar el servidor 
#python3 manage.py runserver

Después en un navegador web ingresar a la url
http://127.0.0.1:8000/hibrido/
