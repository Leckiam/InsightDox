from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from .models import Profile,Roles,InformeCostos

# Register your models here.
admin.site.register(Roles)
admin.site.register(InformeCostos)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "avatar")
    search_fields = ("user__username",)
    
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = "Perfil"

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)

# Reemplazar admin por defecto
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
