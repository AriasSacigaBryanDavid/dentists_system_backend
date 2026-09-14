import os
import re
from pathlib import Path

project_config_dir = 'core'

print('===============================================')
print('  DENTIST - GENERADOR DE MÓDULOS DJANGO     ')
print('===============================================')
print()

# Solicitar el nombre de la nueva aplicación
aplicacion = input('Ingresa el nombre de la aplicación (ej. user, product): ').strip().lower()
aplicacion_normalizada = re.sub(r'[^a-z0-9_]', '_', aplicacion)
modelo_clase = ''.join(word.capitalize() for word in aplicacion.split('_'))

print('\n===============================================')
print(f'Creando aplicación: {aplicacion_normalizada}')
print(f'Modelo principal:   {modelo_clase}')
print('===============================================')

# Rutas principales
ruta_base = Path(__file__).parent.resolve()
ruta_apps = ruta_base / 'apps'
ruta_app = ruta_apps / aplicacion_normalizada

# Crear la carpeta de la app y la carpeta migrations
os.makedirs(ruta_app / 'migrations', exist_ok=True)
(ruta_app / 'migrations' / '__init__.py').touch()

# --- CONTENIDO DE LOS ARCHIVOS ---

apps_content = f"""from django.apps import AppConfig

class {modelo_clase}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.{aplicacion_normalizada}'
"""

# Hereda automáticamente de tu BaseModel
models_content = f"""from django.db import models
from base.models import BaseModel

class {modelo_clase}(BaseModel):
    name = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return self.name or ''
"""

serializers_content = f"""from rest_framework import serializers
from .models import {modelo_clase}

class {modelo_clase}Serializer(serializers.ModelSerializer):
    class Meta:
        model = {modelo_clase}
        fields = '__all__'
"""

# Genera un CRUD completo por defecto
views_content = f"""from rest_framework import viewsets
from .models import {modelo_clase}
from .serializers import {modelo_clase}Serializer

class {modelo_clase}ViewSet(viewsets.ModelViewSet):
    # Filtramos por defecto los registros activos (status=1) de tu BaseModel
    queryset = {modelo_clase}.objects.filter(status=1)
    serializer_class = {modelo_clase}Serializer
"""

urls_content = f"""from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import {modelo_clase}ViewSet

router = DefaultRouter()
router.register(r'{aplicacion_normalizada}s', {modelo_clase}ViewSet, basename='{aplicacion_normalizada}')

urlpatterns = [
    path('', include(router.urls)),
]
"""

admin_content = f"""from django.contrib import admin
from .models import {modelo_clase}

@admin.register({modelo_clase})
class {modelo_clase}Admin(admin.ModelAdmin):
    list_display = ('id', 'name', 'status', 'created_at')
    list_filter = ('status',)
"""

# Mapeo de archivos y su contenido
ruta_archivos = {
    '__init__.py': '',
    'apps.py': apps_content,
    'models.py': models_content,
    'serializers.py': serializers_content,
    'views.py': views_content,
    'urls.py': urls_content,
    'admin.py': admin_content,
    'tests.py': 'from django.test import TestCase\n\n# Create your tests here.\n'
}

# Escribir los archivos en disco
for nombre_archivo, contenido in ruta_archivos.items():
    with open(ruta_app / nombre_archivo, 'w', encoding='utf-8') as f:
        f.write(contenido)

# --- INYECTAR EN SETTINGS.PY ---
settings_path = ruta_base / project_config_dir / 'settings.py'
app_config_path = f"    'apps.{aplicacion_normalizada}.apps.{modelo_clase}Config',\n"

try:
    with open(settings_path, 'r', encoding='utf-8') as file:
        lineas = file.readlines()

    app_ya_existe = any(app_config_path.strip() in linea.strip() for linea in lineas)

    if not app_ya_existe:
        with open(settings_path, 'w', encoding='utf-8') as file:
            for linea in lineas:
                file.write(linea)
                # Busca la declaración de la lista e inserta la app en la siguiente línea
                if linea.strip().startswith("OWN_APPS = ["):
                    file.write(app_config_path)
        print(f'--> [ÉXITO] Aplicación agregada a OWN_APPS en {project_config_dir}/settings.py')
    else:
        print('--> [INFO] La aplicación ya estaba registrada en settings.py')

except FileNotFoundError:
    print(f"--> [ERROR] No se encontró {settings_path}. Añade la app manualmente.")

print('===============================================')
print(' ¡Módulo generado e inyectado correctamente!   ')
print('===============================================')