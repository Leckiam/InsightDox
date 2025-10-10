from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import InformeCostos,Profile
from . import lecturaxlsx


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
        context={"all_Usuarios":allUsers}
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
    if request.user.is_authenticated and request.method == "POST" and request.user.profile.rol.codigo == "SEG":
        email_tmp = request.POST.get("correoLog")
        password_tmp = request.POST.get("contrasenaLog")
        user_tmp = User.objects.create_user(email=email_tmp,
                                            username='',
                                            password=password_tmp)
    return redirect("perfil")  # Ajusta al nombre real de tu vista de perfil

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
    return redirect("home")

@login_required
def eliminar_informe(request, id):
    if request.method == "POST" and request.user.profile.rol.codigo == "ADM":
        informe = get_object_or_404(InformeCostos, id=id)
        informe.delete()
    return redirect('home')