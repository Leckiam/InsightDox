
from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from .models import InformeCostos,Profile,MovimientoEconomico

def permisosSEG():
    # Obtener content type del modelo
    ct_user = ContentType.objects.get_for_model(User)
    ct_profile = ContentType.objects.get_for_model(Profile)
    
    # Obtener permisos del modelo User
    permisos_user = Permission.objects.filter(
        content_type=ct_user,
        codename__in=['add_user', 'change_user', 'delete_user', 'view_user']
    )
    # Obtener permisos del modelo Profile
    permisos_profile = Permission.objects.filter(
        content_type=ct_profile,
        codename__in=['add_profile', 'change_profile', 'delete_profile', 'view_profile']
    )
    # Juntar los permisos
    return list(permisos_user) + list(permisos_profile)
    

def permisosADM():
    # Obtener content type del modelo
    ct_informeCostos = ContentType.objects.get_for_model(InformeCostos)
    ct_movEconomico = ContentType.objects.get_for_model(MovimientoEconomico)
    
    # Obtener permisos del modelo InformeCostos
    permisos_informeCostos = Permission.objects.filter(
        content_type=ct_informeCostos,
        codename__in=[
            'add_informecostos','change_informecostos','delete_informecostos','view_informecostos'
        ]
    )
    permisos_movEconomico = Permission.objects.filter(
        content_type=ct_movEconomico,
        codename__in=[
            'add_movimientoeconomico','change_movimientoeconomico','delete_movimientoeconomico','view_movimientoeconomico'
        ]
    )
    return list(permisos_informeCostos) + list(permisos_movEconomico)

# Crear grupo
grupo_SEG , created_seg = Group.objects.get_or_create(name="Gestion_SEG")
grupo_ADM , created_adm = Group.objects.get_or_create(name="Gestion_ADM")
grupo_CON , created_adm = Group.objects.get_or_create(name="Gestion_CON")

# Asignar permisos al grupo
if created_adm:
    grupo_ADM.permissions.set(permisosADM())
if created_seg:
    grupo_SEG.permissions.set(permisosSEG())

def addPermisoUser(p_user,p_rolCodigo):
    nombre_grupo = "Gestion_"+p_rolCodigo
    try:
        grupo = Group.objects.get(name=nombre_grupo)
        p_user.groups.add(grupo)
    except Group.DoesNotExist:
        print(f"El grupo '{nombre_grupo}' no existe")

def removePermisoUser(p_user,p_rolCodigo):
    nombre_grupo = "Gestion_"+p_rolCodigo
    try:
        grupo = Group.objects.get(name=nombre_grupo)
        p_user.groups.remove(grupo)
    except Group.DoesNotExist:
        print(f"El grupo '{nombre_grupo}' no existe")

def setPermisoUser(p_user,p_rolCodigo):
    # Solo actualiza a un solo grupo
    nombre_grupo = "Gestion_"+p_rolCodigo
    try:
        grupo = Group.objects.get(name=nombre_grupo)
        p_user.groups.set([grupo])
    except Group.DoesNotExist:
        print(f"El grupo '{nombre_grupo}' no existe")