from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.db import transaction
from django.contrib.auth.models import User
from datetime import date
from .models import InformeCostos,Profile,Roles,MovimientoEconomico
from . import lecturaxlsx,permisos,obtenerKpis


# Create your views here.
urlBase="bi/body/"

def login_view(request):
    if not request.user.is_authenticated:
        if request.method == "POST":
            email = request.POST.get("correoLog")
            password = request.POST.get("contrasenaLog")

            user_tmp = buscar_user(email)
            
            user = authenticate(request, username=user_tmp.username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
            else:
                msg={
                    'error1': 'Correo o contraseña incorrectos.'
                }
                return render(request, urlBase+"login.html",context=msg)
        return render(request, urlBase+"login.html")
    else:
        return redirect("home")
    
def buscar_user(email):
    try:
        usuario = User.objects.get(email=email)
        return usuario
    except User.DoesNotExist:
        return User()

def logOut(request):
    logout(request)
    return redirect(to='login')

from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from .services import oauth2

def recoverPass(request):
    if request.method != "POST":
        return render(request, urlBase + 'recoverPass.html')
    
    email = request.POST.get("emailRec")
    
    try:
        user = User.objects.get(email=email)
        
        # Generar token y UID
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        
        reset_url = f"{request.scheme}://{request.get_host()}/reset-password/{uid}/{token}/"
        
        subject = 'Recuperación de Contraseña - InsightDox'
        message = f"""
        Hola {user.first_name},

        Has solicitado recuperar tu contraseña en InsightDox.

        Por favor, haz clic en el siguiente enlace para restablecer tu contraseña:
        {reset_url}

        Si no solicitaste este cambio, puedes ignorar este correo.

        Saludos,
        El equipo de InsightDox
"""
        # --- Enviar correo usando Gmail API ---
        oauth2.enviar_correo_gmail_api(email, subject, message)

        msg = {
            'success': True,
            'message': f'Correo de recuperación enviado a {email}. Revisa tu bandeja de entrada.',
            'reset_url': reset_url
        }
        
    except User.DoesNotExist:
        msg = {
            'e_login': email,
            'error': 'El correo ingresado no está registrado en el sistema. Por favor, verifica e intenta nuevamente.'
        }
    except Exception as e:
        msg = {
            'error': f'Ocurrió un error al enviar el correo: {str(e)}'
        }
    
    return render(request, urlBase + 'recoverPass.html', msg)

from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str

def reset_password_confirm(request, uidb64, token):
    """
    Vista para restablecer la contraseña usando UID y token de recuperación.
    """
    try:
        # Decodificar el UID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        error = None
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if not new_password or not confirm_password:
                error = 'Las contraseñas no pueden estar vacías.'
            elif new_password != confirm_password:
                error = 'Las contraseñas no coinciden.'
            elif len(new_password) < 8:
                error = 'La contraseña debe tener al menos 8 caracteres.'
            else:
                # Guardar nueva contraseña
                user.set_password(new_password)
                user.save()
                messages.success(
                    request,
                    'Tu contraseña ha sido restablecida exitosamente. Ahora puedes iniciar sesión con tu nueva contraseña.'
                )
                return redirect('login')

        return render(request, urlBase + 'reset_password_confirm.html', {'error': error})
    else:
        # Token inválido o expirado
        messages.error(request, 'El enlace de recuperación es inválido o ha expirado.')
        return redirect('login')

def home(request):
    if request.user.is_authenticated:
        Profile.objects.get_or_create(
            user=request.user,
            defaults={
                'bio': 'Nuevo usuario del sistema',
                'avatar': None
                }
            )
        try:
            hoy = date.today()
            anio_actual = hoy.year
            mes_actual = hoy.month
            context=None
            
            if InformeCostos.objects.exists():
                allInforme = InformeCostos.objects.all().order_by('-anio', '-mes')[:3]
                if InformeCostos.objects.filter(anio=anio_actual, mes=mes_actual).exists():
                    lastInform = InformeCostos.objects.filter(anio=anio_actual, mes=mes_actual).order_by('-id').first()
                elif InformeCostos.objects.filter(anio=anio_actual, mes=mes_actual-1).exists():
                    lastInform = InformeCostos.objects.filter(anio=anio_actual, mes=mes_actual-1).order_by('-id').first()
                else:
                    lastInform = InformeCostos()
                context={
                    "all_Informes": allInforme,
                    "ultimo_Informe": lastInform,
                    "balance": lastInform.resumen_ventas-(lastInform.resumen_gastos+lastInform.resumen_remuneraciones),
                    "data":{
                        "kpi_01":obtenerKpis.obtKpi_01(),
                        "kpi_02":obtenerKpis.obtKpi_02()
                    }
                }
        except Exception as e:
            print("Ocurrió un error:", e)
            context={
                "ultimo_Informe": InformeCostos(),
                "balance": 0
            }
        return render(request,urlBase+'index.html',context=context)
    else:
        return redirect("login")
    
def perfil(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        context={}
        if request.user.profile.rol.codigo == "SEG":
            allUsers = User.objects.filter(is_superuser=False)
            allRoles = Roles.objects.all()
            context={
                "all_Usuarios":allUsers,
                "all_roles":allRoles,
                "rows_per_page": 5
                }
        return render(request,urlBase+'verPerfil.html',context=context)

def dashboard(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        return render(request,urlBase+'dashboard.html')

@login_required
def update_avatar(request):
    if request.method == "POST" and request.FILES.get("avatar"):
        profile = request.user.profile
        profile.avatar = request.FILES["avatar"]
        profile.save()
    return redirect("perfil")  # Ajusta al nombre real de tu vista de perfil

@login_required
def addUser(request):
    if request.method == "POST" and request.user.profile.rol.codigo == "SEG":
        username_tmp = request.POST.get("username")
        email_tmp = request.POST.get("correo")
        nombre_tmp = request.POST.get("nombre")
        apellido_tmp = request.POST.get("apellido")
        password1_tmp = request.POST.get("contrasena1")
        password2_tmp = request.POST.get("contrasena2")
        rolID_tmp = request.POST.get("rol")
        avatar_tmp = request.FILES.get("avatar")
        if avatar_tmp == None:
            avatar_tmp = 'avatars/user_0_unknown.jpg'
        def addProfile(p_user,p_avatar,p_rolID):
            rolTmp = Roles.objects.get(id=p_rolID)
            default_profile={
                "avatar":p_avatar,
                "rol":rolTmp
            }
            Profile.objects.get_or_create(user=p_user,defaults=default_profile)
            codigo_rol = rolTmp.codigo
            permisos.setPermisoUser(p_user,codigo_rol)
        try:
            if User.objects.filter(username=username_tmp).exists():
                user_tmp = User.objects.get(username=username_tmp)
                if not Profile.objects.filter(user=user_tmp).exists():
                    addProfile(user_tmp,avatar_tmp,rolID_tmp)
                    messages.success(request, f'Perfil agregado al usuario existente {username_tmp}.')
                else:
                    messages.info(request, f'El usuario {username_tmp} ya existe con perfil.')
            else:
                if password1_tmp == password2_tmp:
                    user_tmp = User.objects.create_user(email=email_tmp,
                                                username=username_tmp,
                                                password=password1_tmp,
                                                first_name=nombre_tmp,
                                                last_name=apellido_tmp)
                    addProfile(user_tmp,avatar_tmp,rolID_tmp)
                    messages.success(request, f'Usuario {username_tmp} creado correctamente.')
                else:
                    messages.error(request, 'Las contraseñas no coinciden.')
        except Exception as exc:
            print('Fallo el agregar Usuario:', exc)
            messages.error(request, 'Ocurrió un error al crear el usuario. Revise los datos e intente nuevamente.')
    next_url = request.GET.get('next', 'home')
    return redirect(next_url)

@login_required
def deleteUser(request,id):
    if request.method == "POST" and request.user.profile.rol.codigo == "SEG":
        user_tmp = get_object_or_404(User, id=id)
        profile_tmp = Profile.objects.filter(user=user_tmp).first()
        try:
            with transaction.atomic():
                if profile_tmp:
                    profile_tmp.delete()
                user_tmp.delete()
                messages.success(request, 'Usuario eliminado correctamente.')
        except Exception as e:
            print(f"No se pudo eliminar el usuario: {e}")
            messages.error(request, 'No se pudo eliminar el usuario. Intente nuevamente.')
    next_url = request.GET.get('next', 'home')
    return redirect(next_url)

@login_required
def editUser(request,id):
    if request.method == "POST" and request.user.profile.rol.codigo == "SEG":
        password1_tmp = request.POST.get("contrasena1")
        password2_tmp = request.POST.get("contrasena2")
        nombre_tmp = request.POST.get("nombre")
        apellido_tmp = request.POST.get("apellido")
        rolID_tmp = request.POST.get("rol")
        avatar_tmp = request.FILES.get("avatar")
        
        user_tmp = get_object_or_404(User, id=id)
        rolTmp = Roles.objects.get(id=rolID_tmp)
        profile_tmp = Profile.objects.filter(user=user_tmp).first()
        
        update = False
        try:
            with transaction.atomic():
                if profile_tmp:
                    if avatar_tmp != None or rolTmp != profile_tmp.rol:
                        if avatar_tmp:
                            profile_tmp.avatar = avatar_tmp  # solo si se subió uno nuevo
                        profile_tmp.rol = rolTmp
                        profile_tmp.save()
                        codigo_rol = rolTmp.codigo
                        permisos.setPermisoUser(user_tmp,codigo_rol)
                        update = True
                if nombre_tmp:
                    user_tmp.first_name = nombre_tmp
                    update = True
                if apellido_tmp:
                    user_tmp.last_name = apellido_tmp
                    update = True
                if password1_tmp:
                    if (password1_tmp == password2_tmp):
                        user_tmp.set_password(password1_tmp)
                        update = True
                    else:
                        update = False
                if update:
                    user_tmp.save()
                    messages.success(request, 'Usuario editado correctamente.')
                else:
                    messages.info(request, 'No se realizaron cambios al usuario.')
        except Exception as e:
            print(f"No se pudo editar el usuario: {e}")
            messages.error(request, 'Ocurrió un error al editar el usuario. Revise los datos e intente nuevamente.')
    next_url = request.GET.get('next', 'home')
    return redirect(next_url)

@login_required
def gestUsers(request):
    if request.user.profile.rol.codigo == "SEG":
        allUsers = User.objects.filter(is_superuser=False)
        allRoles = Roles.objects.all()
        context={
            "all_Usuarios":allUsers,
            "all_roles":allRoles
            }
        return render(request, urlBase+"gestion/gestionUsers.html",context)
    else:
        return redirect('home')

@login_required
def addInformeCosto(request):
    if request.method == "POST" and request.user.profile.rol.codigo == "ADM":
        next_url = request.POST.get('next', 'registroInformes')
        informe_excel = request.FILES.get('archivo_informe')
        if not informe_excel:
            messages.error(request, 'No se seleccionó ningún archivo para subir.')
            return redirect(next_url)

        try:
            df = lecturaxlsx.procesar_informe(informe_excel)
            mes, anno = lecturaxlsx.obtenerMesAnno(df)

            df_ventas = df[df['Categoria'] == 'EdP']
            df_remuneracion = df[df['Categoria'] == 'MO']
            df_gastos = df[~df['Categoria'].isin(['EdP', 'MO'])]

            informe, created = InformeCostos.objects.get_or_create(
                usuario=request.user,
                mes=mes,
                anio=anno,
                defaults={
                    'filas_detectadas': len(df),
                    'resumen_ventas': float(df_ventas['Total'].sum()),
                    'resumen_gastos': float(df_gastos['Total'].sum()),
                    'resumen_remuneraciones': float(df_remuneracion['Total'].sum())
                }
            )
            if informe.archivo_gcs:
                informe.archivo_gcs.delete(save=False)
            informe.archivo_gcs.save(
                f"Informe_{anno}_{mes:02d}.xlsx",
                informe_excel,
                save=True
            )

            # Solo cargar movimientos si se creó recién
            if created:
                lecturaxlsx.cargar_movimientos_desde_df(df, informe)
            else:
                print('El informe ya existe')

            messages.success(request, 'Informe subido correctamente.')
            return redirect(next_url)

        except Exception as e:
            # Capturar errores de procesamiento del archivo (formato inválido, fechas NaN, etc.)
            err_msg = str(e)
            # Mensaje amigable para el usuario, manteniendo el detalle en logs
            messages.error(request, f"No se pudo procesar el archivo: {err_msg}")
            print(f"Error al procesar informe: {err_msg}")
            return redirect(next_url)

    return redirect('home')

@login_required
def eliminar_informe(request, id):
    if request.method == "POST" and request.user.profile.rol.codigo == "ADM":
        informe = get_object_or_404(InformeCostos, id=id)
        informe.delete()
    next_url = request.POST.get('next', 'home')
    return redirect(next_url)

from django.core.paginator import Paginator

@login_required
def gestInformes(request):
    allInformes = InformeCostos.objects.all().order_by('-anio', '-mes')
    
    annos_existentes = InformeCostos.objects.aggregate(
        anno_max=Max('anio'),
        anno_min=Min('anio')
    )
    if annos_existentes['anno_min'] and annos_existentes['anno_max']:
        anno_inicio = annos_existentes['anno_min']
        anno_fin = annos_existentes['anno_max']
        annos = list(range(anno_inicio, anno_fin + 1))
    else:
        annos = []
        
    anno = request.GET.get('anno','')
    if anno:
        allInformes = allInformes.filter(anio=anno)
        anno = int(anno)
    
    
    paginator = Paginator(allInformes, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        "all_Informes": page_obj,
        "selected_anno": anno,
        "annos": annos
    }
    return render(request, urlBase + "gestion/registroInformes.html", context)

@login_required
def editObservacion(request,id):
    if request.method == "POST" and request.user.profile.rol.codigo == "ADM":
        observacion = request.POST.get("observaciones")
        informe_tmp = get_object_or_404(InformeCostos, id=id)
        try:
            informe_tmp.observaciones = observacion
            informe_tmp.save()
        except Exception as e:
            print(f"No se pudo actualizar la observación: {e}")
    return redirect('gestInformes')

from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required

from django.db.models import Min, Max

@login_required
def gestMovEco(request):
    # Query base
    allMovimientos = MovimientoEconomico.objects.all().order_by('-fecha')

    # 
    annos_existentes = MovimientoEconomico.objects.aggregate(
        anno_min=Min('fecha'),
        anno_max=Max('fecha')
    )
    if annos_existentes['anno_min'] and annos_existentes['anno_max']:
        anno_inicio = annos_existentes['anno_min'].year
        anno_fin = annos_existentes['anno_max'].year
        annos = list(range(anno_inicio, anno_fin + 1))
    else:
        annos = []
    
    meses_choices = [
        (1, "Enero"), (2, "Febrero"), (3, "Marzo"), (4, "Abril"),
        (5, "Mayo"), (6, "Junio"), (7, "Julio"), (8, "Agosto"),
        (9, "Septiembre"), (10, "Octubre"), (11, "Noviembre"), (12, "Diciembre"),
    ]

    # --- FILTROS ---
    tipo = request.GET.get('tipo', '')  # VE, GA, RE
    mes = request.GET.get('mes', '')    # 1..12
    anno = request.GET.get('anno', '')
    per_page = request.GET.get('per_page', 15)  # default 14 por página

    if tipo:
        allMovimientos = allMovimientos.filter(naturaleza=tipo)
    if mes:
        allMovimientos = allMovimientos.filter(fecha__month=mes)
        mes = int(mes)
    if anno:
        allMovimientos = allMovimientos.filter(fecha__year=anno)
        anno = int(anno)

    # --- PAGINACIÓN ---
    paginator = Paginator(allMovimientos, int(per_page))
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    offset = (page_obj.number-1) * int(per_page)
    
    context = {
        "all_Movimientos": page_obj,
        "selected_tipo": tipo,
        "selected_mes": mes,
        "selected_anno": anno,
        "per_page": str(per_page),
        "offset":offset,
        "meses": meses_choices,
        "annos": annos
    }
    return render(request, urlBase+"gestion/registroMovEco.html", context)

@login_required
def dashboard(request):
    context={
        "data":{
            "kpi_03":obtenerKpis.obtKpi_03(),
            "kpi_04":obtenerKpis.obtKpi_04(),
            "kpi_05":obtenerKpis.obtKpi_05(),
            "kpi_06":obtenerKpis.obtKpi_06(),
            "kpi_07":obtenerKpis.obtKpi_07(),
            "kpi_08":obtenerKpis.obtKpi_08()
        }
    }
    return render(request, urlBase+"dashboard.html", context)

from rest_framework.decorators import api_view
from .services import ai_agent,gcp_gsc
from django.http import StreamingHttpResponse

@login_required
@api_view(['POST'])
def consultar_ia(request):
    return StreamingHttpResponse(ai_agent.generarRespuesta(request), content_type='text/plain')

from django.conf import settings

@login_required
def descargar_informe(request, id):
    informe = get_object_or_404(InformeCostos, id=id)
    if settings.DEBUG:
        url_archivo = informe.archivo_gcs.url
        return redirect(url_archivo)
    else:
        signed_url = gcp_gsc.descargar_informe(request, id, informe)
        return redirect(signed_url)