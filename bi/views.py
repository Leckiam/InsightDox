from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.contrib.auth.models import User
from .models import InformeCostos,Profile,Roles
from . import lecturaxlsx,permisos


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

def recoverPass(request):
    if request.method != "POST":
        return render(request,urlBase+'recoverPass.html')
    else:
        email = request.POST["emailRec"]
        user = {
            'email':email,
        }
        '''
        if (metApis.seguridadRecoverApi(email)):
            return redirect(to='login')
        else:
            msg={
                'e_login': email,
            }
            return render(request,urlBase+'recoverPass.html',msg)
        '''
        msg={
            'e_login': email,
        }
        return render(request,urlBase+'recoverPass.html',msg)

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
            allInforme = InformeCostos.objects.order_by('-id')[:3]
            lastInform = allInforme.first()
            context={
                "all_Informes": allInforme,
                "ultimo_Informe": lastInform,
                "balance": lastInform.resumen_ventas-lastInform.resumen_gastos,
                "data":{
                    "kpi_01":[
                        [120000, 130000, 140000, 150000, 160000, 140000, 130000, 140000, 150000, 160000, 170000, 175000],
                        [2900000, 3000000, 3100000, 3050000, 3000000, 2950000, 3000000, 3050000, 3000000, 3100000, 3050000, 3053576]
                    ],
                    "kpi_02":[4000000, 7500000, 3000000, 14056743]
                }
            }
        except:
            print('No hay Informes Registrados')
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
        allUsers = User.objects.all()
        allRoles = Roles.objects.all()
        context={
            "all_Usuarios":allUsers,
            "all_roles":allRoles
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
        password_tmp = request.POST.get("contrasena")
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
            else:
                user_tmp = User.objects.create_user(email=email_tmp,
                                            username=username_tmp,
                                            password=password_tmp)
                addProfile(user_tmp,avatar_tmp,rolID_tmp)
        except:
            print('Fallo el agregar Usuario')
    return redirect("perfil")  # Ajusta al nombre real de tu vista de perfil

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
                print("Usuario eliminado correctamente")
        except Exception as e:
            print(f"No se pudo eliminar el usuario: {e}")
    return redirect("perfil")

@login_required
def editUser(request,id):
    if request.method == "POST" and request.user.profile.rol.codigo == "SEG":
        password_tmp = request.POST.get("contrasena")
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
                if password_tmp:
                    user_tmp.set_password(password_tmp)
                    user_tmp.save()
                    update = True
                if update:
                    print( "Usuario editado correctamente")
                else:
                    print('No se realizaron cambios al Usuario')
        except Exception as e:
            print(f"No se pudo editar el usuario: {e}")
    return redirect("perfil")

@login_required
def addInformeCosto(request):
    if request.method == "POST" and request.user.profile.rol.codigo == "ADM":
        informe_excel = request.FILES['archivo_informe']
        df = lecturaxlsx.procesar_informe(informe_excel)
        
        url='https://storage.googleapis.com/mi-bucket/informes/'
        mes,anno = lecturaxlsx.obtenerMesAnno(df)
        
        df_ventas = df[df['Categoria'] == 'EdP']
        df_remuneracion = df[df['Categoria'] == 'MO']
        df_gastos = df[~df['Categoria'].isin(['EdP', 'MO'])]
        
        try:
            informe = InformeCostos(
                usuario=request.user,
                archivo_url=f'{url}{anno}/{mes}/Informe_{anno}_{mes}.xlsx',
                mes=mes,
                anio=anno,
                filas_detectadas=0,
                resumen_ventas=float(df_ventas['Total'].sum()),
                resumen_gastos=float(df_gastos['Total'].sum()),
                resumen_remuneraciones=float(df_remuneracion['Total'].sum())
            )
            informe.save()
        except:
            print('No cumple con el formato')
    return redirect("home")

@login_required
def eliminar_informe(request, id):
    if request.method == "POST" and request.user.profile.rol.codigo == "ADM":
        informe = get_object_or_404(InformeCostos, id=id)
        informe.delete()
    return redirect('home')