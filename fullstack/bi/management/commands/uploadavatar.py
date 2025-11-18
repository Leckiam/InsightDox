import os
from django.core.management.base import BaseCommand
from django.core.files.storage import default_storage
from django.conf import settings

class Command(BaseCommand):
    help = "Sube el avatar default al bucket de media"

    def handle(self, *args, **options):
        media_root = settings.BASE_DIR / "media"
        if not media_root or not os.path.exists(media_root):
            self.stdout.write(self.style.ERROR("No se encontró MEDIA_ROOT local."))
            return
        local_path = media_root / "avatars/user_0_unknown.jpg"
        relative_path = "avatars/user_0_unknown.jpg"

        if default_storage.exists(relative_path):
            self.stdout.write(f"Ya existe: {relative_path}")
        else:
            with open(local_path, "rb") as f:
                default_storage.save(relative_path, f)
            self.stdout.write(self.style.SUCCESS(f"Subido: {relative_path}"))
