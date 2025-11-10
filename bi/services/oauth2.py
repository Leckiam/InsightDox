import base64
from email.mime.text import MIMEText
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from django.conf import settings

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def enviar_correo_gmail_api(destinatario, asunto, cuerpo):
    """
    Envía un correo usando Gmail API con OAuth2.
    Funciona con cuentas personales y evita problemas SMTP.
    """

    remitente = settings.EMAIL_OAUTH_ADDRESS  # tu Gmail autorizado

    if settings.DEBUG:
        # Desarrollo: flujo interactivo con JSON
        flow = InstalledAppFlow.from_client_secrets_file(
            settings.CLIENT_SECRETS_FILE, SCOPES
        )
        creds = flow.run_local_server(port=0)
    else:
        # Producción: usar refresh token
        creds = Credentials(
            None,
            refresh_token=settings.EMAIL_OAUTH_REFRESH_TOKEN,
            client_id=settings.EMAIL_OAUTH_CLIENT_ID,
            client_secret=settings.EMAIL_OAUTH_CLIENT_SECRET,
            token_uri='https://oauth2.googleapis.com/token'
        )
        creds.refresh(Request())

    # Crear mensaje MIME
    message = MIMEText(cuerpo)
    message['to'] = destinatario
    message['from'] = remitente
    message['subject'] = asunto

    # Codificar en base64 para Gmail API
    raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

    # Conectar con Gmail API
    service = build('gmail', 'v1', credentials=creds)
    message_body = {'raw': raw_message}

    # Enviar correo
    service.users().messages().send(userId='me', body=message_body).execute()
    print(f"Correo enviado a {destinatario} con asunto '{asunto}'")
