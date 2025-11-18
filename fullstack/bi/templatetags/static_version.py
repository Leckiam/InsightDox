import os
from django import template
from django.conf import settings
from pathlib import Path
from django.contrib.staticfiles.storage import staticfiles_storage

register = template.Library()

@register.simple_tag
def static_version(path):
    """
    Devuelve la ruta del archivo estático con versionado:
    - En DEBUG=True: agrega query string basado en timestamp del archivo.
    - En producción (DEBUG=False): usa la URL versionada generada por STATICFILES_STORAGE.
    """
    if settings.DEBUG:
        # Buscar archivo en STATICFILES_DIRS
        for dir in settings.STATICFILES_DIRS:
            full_path = Path(dir) / path
            if full_path.exists():
                timestamp = int(full_path.stat().st_mtime)
                return f"{settings.STATIC_URL}{path}?v={timestamp}"
        # Si no se encuentra, devolver ruta normal
        return f"{settings.STATIC_URL}{path}"
    
    else:
        # Producción: usar URL versionada generada por STATICFILES_STORAGE
        # Esto funciona si usas ManifestStaticFilesStorage o GSStaticStorage
        return staticfiles_storage.url(path)