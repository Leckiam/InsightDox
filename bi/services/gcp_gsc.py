from google.cloud import storage
from django.conf import settings

def descargar_informe(request, id,informe):
    # Nombre del blob dentro del bucket
    blob_name = informe.archivo_gcs.name
    if not blob_name.startswith("media/"):
        print("actuo if del media en descarga")
        blob_name = f"media/{blob_name}"
    
    client = storage.Client(credentials=settings.GS_CREDENTIALS)
    bucket = client.bucket(settings.GS_BUCKET_NAME)
    blob = bucket.blob(blob_name)
    
    # Generar enlace temporal (1 hora)
    signed_url = blob.generate_signed_url(
        version="v4",
        expiration=60,
        method="GET"
    )
    
    return signed_url