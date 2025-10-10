# signals.py
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Roles,Profile

@receiver(post_migrate)
def crear_datos_base(sender, **kwargs):
    # --- Crear roles base ---
    roles_base = [
        {
            "rolName": "Admin de Contratos",
            "codigo": "ADM",
            "descripcion": "Administra la información contractual y financiera de la empresa.",
            "responsabilidad": "Sube los informes mensuales con las ventas, gastos y remuneraciones de la empresa."
        },
        {
            "rolName": "Consultor",
            "codigo": "CON",
            "descripcion": "Accede a los datos del sistema para análisis y seguimiento de resultados.",
            "responsabilidad": "Visualiza y consulta los contratos, e interactúa con los dashboards de análisis y predicciones."
        },
        {
            "rolName": "Seguridad",
            "codigo": "SEG",
            "descripcion": "Supervisa los accesos y permisos del sistema.",
            "responsabilidad": "Gestiona a los usuarios, administra sus roles y verifica la seguridad de las cuentas."
        }
    ]

    for rol in roles_base:
        Roles.objects.get_or_create(codigo=rol["codigo"], defaults=rol)

    from decouple import config
    # --- Crear usuario base ---
    if not User.objects.filter(username=config('ADMIN_USER')).exists():
        User.objects.create_superuser(
            username=config('ADMIN_USER'),
            email=config('ADMIN_EMAIL'),
            password=config('ADMIN_PASS')
        )
        print("Usuario admin creado automáticamente")
    
    # --- Crear Perfil a Usuario base ---
    user_admin=User.objects.get(username="admin")
    rol_admin=Roles.objects.get(codigo='ADM')
    Profile.objects.get_or_create(
        user=user_admin,
        defaults={
            'user':user_admin,
            'avatar': None,
            'rol': rol_admin
        }
        )