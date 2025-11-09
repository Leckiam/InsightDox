from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('login', views.login_view,name='login'),
    path('logOut/', views.logOut,name='logOut'),
    path('recover/', views.recoverPass,name='recover'),
    path('reset-password/<uidb64>/<token>/', views.reset_password_confirm, name='reset_password_confirm'),
    path('perfil/', views.perfil,name='perfil'),
    path("perfil/edit-avatar/", views.update_avatar, name="u_avatar"),
    path('dashboard/', views.dashboard,name='dashboard'),
    path('addInformeCosto/', views.addInformeCosto,name='addInformeCosto'),
    path('eliminar_informe/<int:id>/', views.eliminar_informe,name='eliminar_informe'),
    path('addUser/', views.addUser,name='addUser'),
    path('editUser/<int:id>/', views.editUser,name='editUser'),
    path('deleteUser/<int:id>/', views.deleteUser,name='deleteUser'),
    path('gestUsers/', views.gestUsers, name='gestUsers'),
    path('gestInformes/', views.gestInformes, name='gestInformes'),
    path('editObservacion/<int:id>/', views.editObservacion, name='editObservacion'),
    path('gestMovEco/', views.gestMovEco, name='gestMovEco'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path("consultar_ia/", views.consultar_ia, name="consultar_ia"),
    path("descargar_informe/<int:id>/", views.descargar_informe, name="descargar_informe"),
]