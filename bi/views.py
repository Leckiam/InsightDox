from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User


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
        return render(request,urlBase+'index.html')
    
def perfil(request):
    if not request.user.is_authenticated:
        return redirect("login")
    else:
        return render(request,urlBase+'verPerfil.html')

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
