from django.urls import path,include
from . import views
from .views import RegistroInformesView, analisis_costos

urlpatterns = [
    path('', views.home,name='home'),
    path('login', views.login_view,name='login'),
    path('logOut/', views.logOut,name='logOut'),
    path('recover/', views.recoverPass,name='recover'),
    path('perfil/', views.perfil,name='perfil'),
    path("perfil/edit-avatar/", views.update_avatar, name="u_avatar"),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('addInformeCosto/', views.addInformeCosto,name='addInformeCosto'),
    path('eliminar_informe/<int:id>/', views.eliminar_informe,name='eliminar_informe'),
    path('registro-informes/', RegistroInformesView.as_view(), name='registro_informes'),
    path('analisis-costos/', analisis_costos, name='analisis_costos'),
]