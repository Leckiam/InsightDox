from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from . import lecturaxlsx
from django.views.generic import ListView
from .models import ResumenMensual, InformeCostos
from .forms import InformeCostosUploadForm


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
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        allInforme = InformeCostos.objects.order_by('-id')[:3]
        context={
            "all_Informes":allInforme,
            "ultimo_Informe":allInforme.first(),
            "balance":allInforme.first().resumen_ventas-allInforme.first().resumen_gastos
            }
        return render(request,urlBase+'index.html',context=context)
    
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

class RegistroInformesView(ListView):
    model = ResumenMensual
    template_name = "bi/registro_informes.html"
    context_object_name = "resumenes"
    paginate_by = 50

@login_required
def analisis_costos(request):
    context = {}
    if request.method == "POST":
        form = InformeCostosUploadForm(request.POST, request.FILES)
        if form.is_valid():
            archivo = form.cleaned_data["archivo"]
            import pandas as pd
            try:
                if archivo.name.lower().endswith((".xls", ".xlsx")):
                    df = pd.read_excel(archivo)
                else:
                    df = pd.read_csv(archivo)
            except Exception as e:
                context["error"] = f"Error al leer el archivo: {e}"
                form = InformeCostosUploadForm()
            else:
                ventas_df = df[df["Categoria"] == "EdP"]
                remuneraciones_df = df[df["Categoria"] == "MO"]
                gastos_df = df[df["Categoria"].isin(["EPP", "M", "H", "GG"])]

                total_ventas = ventas_df["Total"].sum()
                total_remuneraciones = remuneraciones_df["Total"].sum()
                total_gastos = gastos_df["Total"].sum()

                context.update({
                    "total_ventas": total_ventas,
                    "total_remuneraciones": total_remuneraciones,
                    "total_gastos": total_gastos,
                    "ventas_table": ventas_df.to_html(classes="table table-striped table-sm", index=False),
                    "remuneraciones_table": remuneraciones_df.to_html(classes="table table-striped table-sm", index=False),
                    "gastos_table": gastos_df.to_html(classes="table table-striped table-sm", index=False),
                })
        else:
            context["error"] = "Formulario inválido. Verifica el archivo subido."
            form = InformeCostosUploadForm()
    else:
        form = InformeCostosUploadForm()
    context["form"] = form
    return render(request, "bi/analisis_costos.html", context)