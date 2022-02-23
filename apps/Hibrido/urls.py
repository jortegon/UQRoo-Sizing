from django.urls import path
from .views import Paneles, Viento, Resumen, Hidrogeno, Resultado, Tipocarga, Camino, index, Ubicacion, Login, Configuracion, ConfiguracionJson

urlpatterns = [
    path('',index, name = 'index'),
    path('tipocarga/',Tipocarga, name = 'tipocarga'),
    path('camino/',Camino, name = 'camino'),
    path('paneles/',Paneles, name= 'paneles'),
    path('viento/',Viento, name = 'viento'),
    path('hidrogeno/',Hidrogeno, name = 'hidrogeno'),
    path('resumen/',Resumen, name = 'resumen'),
    path('resultado/',Resultado, name = 'resultado'),
    path('ubicacion/',Ubicacion, name = 'ubicacion'),
    path('login/',Login, name = 'login'),
    path('configuracion/',Configuracion, name = 'configuracion'),
    path('configuracionJson/',ConfiguracionJson, name = 'configuracionJson'),
    
      
]