from django.urls import path,include
from . import views

urlpatterns = [
    path('', views.home,name='home'),
    path('login', views.login_view,name='login'),
    path('logOut/', views.logOut,name='logOut'),
    path('recover/', views.recoverPass,name='recover'),
    path('perfil/', views.perfil,name='perfil'),
    path("perfil/edit-avatar/", views.update_avatar, name="u_avatar"),
    path('dashboard/', views.dashboard,name='dashboard'),
]