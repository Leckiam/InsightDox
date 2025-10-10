from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import User
import os
from datetime import datetime
# Create your models here.

def user_directory_path(instance, filename):
    extension = filename.split('.')[-1]
    filename = f"user_{instance.user.username}.{extension}"
    return f'avatars/{filename}'


class Roles(models.Model):
    codigo = models.CharField(max_length=10, unique=True, null=False, blank=False)
    rolName = models.CharField(max_length=255, null=False, blank=False)
    descripcion = models.TextField("Descripción", null=True, blank=True)
    responsabilidad = models.TextField("Responsabilidad principal", null=True, blank=True)

    class Meta:
        verbose_name = "Rol"
        verbose_name_plural = "Roles"
        ordering = ['rolName']

    def __str__(self):
        return f"{self.rolName} ({self.codigo})"


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to=user_directory_path, blank=True, null=True)
    rol = models.ForeignKey(Roles, on_delete=models.CASCADE, null=True, blank=True)

    def save(self, *args, **kwargs):
        try:
            this = Profile.objects.get(id=self.id)
            if this.avatar and this.avatar != self.avatar:
                this.avatar.delete(save=False)
        except Profile.DoesNotExist:
            pass
        super().save(*args, **kwargs)
        
class InformeCostos(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    archivo_url = models.URLField(max_length=500, blank=True, null=True)

    nombre = models.CharField(max_length=255, editable=False)
    mes = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(12)],editable=False)
    anio = models.PositiveIntegerField(editable=False,verbose_name="Año",validators=[MinValueValidator(1980), MaxValueValidator(3000)])
    fecha_subida = models.DateTimeField(auto_now_add=True)
    procesado = models.BooleanField(default=False)

    filas_detectadas = models.PositiveIntegerField(default=0)
    resumen_ventas = models.DecimalField(max_digits=12, decimal_places=0, default=0, null=False, blank=False)
    resumen_gastos = models.DecimalField(max_digits=12, decimal_places=0, default=0, null=False, blank=False)
    resumen_remuneraciones = models.DecimalField(max_digits=12, decimal_places=0, default=0, null=False, blank=False)
    
    observaciones = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = "InformeCosto"
        verbose_name_plural = "InformeCostos"
        ordering = ['nombre']
    
    def save(self, *args, **kwargs):
        # Generar nombre automáticamente si no existe
        if not self.nombre:
            self.nombre = f"Informe_{self.anio}_{self.mes:02d}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.nombre} ({self.mes} {self.anio})"

#Modelo Temporales (Se espera crearlos en BigQuery)
#Nro    Fecha   Descripción     Categoria	Tipo	Cant.	Unidad	Precio  unitario	Total
class MovimientoEconomico(models.Model):
    NATURALEZA_CHOICES = [
        ('VE', 'Venta'),
        ('GA', 'Gasto'),
        ('RE', 'Remuneración'),
    ]
    CATEGORIA_CHOICES = [
        ('EdP', 'Estado de Pago'),
        ('MO', 'Mano de obra'),
        ('EPP', 'Elementos de protección personal'),
        ('M', 'Material'),
        ('H', 'Herramienta'),
        ('GG', 'Gastos Generales'),
    ]
    
    id = models.IntegerField(primary_key=True, editable=False)
    nro = models.CharField(max_length=6,editable=False)
    fecha_venta = models.DateField()
    descripcion= models.TextField(max_length=80)
    naturaleza=models.CharField(max_length=50, choices=NATURALEZA_CHOICES)
    categoria=models.CharField(max_length=50, choices=CATEGORIA_CHOICES)
    cantidad = models.PositiveIntegerField(default=0)
    unidad = models.CharField(max_length=20)
    precio_unitario = models.PositiveIntegerField(default=0)
    total_venta= models.PositiveIntegerField(blank=True)
    
    class Meta:
        ordering = ['id']
        constraints = [
        models.UniqueConstraint(
            fields=['fecha_venta', 'descripcion'],
            name='unique_fecha_descripcion'
        )
    ]
        
    def save(self, *args, **kwargs):
        self.nro = str(self.nro).zfill(5)
        self.total_venta = self.cantidad * self.precio_unitario
        if not self.id:
            self.id = int(str(self.fecha_venta.strftime('%Y%m%d'))+''+self.nro)
        super().save(*args, **kwargs)
    
    @property
    def año(self):
        return self.fecha_venta.year

    @property
    def mes(self):
        return self.fecha_venta.month

    @property
    def día(self):
        return self.fecha_venta.day