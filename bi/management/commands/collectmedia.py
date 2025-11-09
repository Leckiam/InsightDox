import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files.storage import default_storage

class Command(BaseCommand):
    help = "Sube los archivos de MEDIA_ROOT al almacenamiento configurado (por ejemplo, Google Cloud Storage)."

    def handle(self, *args, **options):
        media_root = settings.BASE_DIR / "media"
        if not media_root or not os.path.exists(media_root):
            self.stdout.write(self.style.ERROR("No se encontró MEDIA_ROOT local."))
            return

        for root, _, files in os.walk(media_root):
            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, media_root)
                
                if default_storage.exists(relative_path):
                    self.stdout.write(f"Ya existe: {relative_path}")
                    continue
                
                with open(local_path, "rb") as f:
                    default_storage.save(relative_path, f)

                self.stdout.write(self.style.SUCCESS(f"Subido: {relative_path}"))

        self.stdout.write(self.style.SUCCESS("Todos los archivos de media fueron subidos correctamente."))