from django.db.models import Sum
from datetime import date
from dateutil.relativedelta import relativedelta
import datetime
from . models import InformeCostos, MovimientoEconomico

def ultimoMesAnno():
    ultimoInforme = InformeCostos.objects.order_by('-anio', '-mes').first()
    if not ultimoInforme:
        return [], []  # No hay datos
    
    ultimo_anio = ultimoInforme.anio
    ultimo_mes = ultimoInforme.mes
    
    return ultimo_anio,ultimo_mes

def obtKpi_01():
    hoy = date.today()
    
    # Generar los últimos 12 meses desde el último registro
    meses_rango = []
    for i in range(12):
        fecha = hoy - relativedelta(months=11-i)  # 11-i para que quede en orden cronológico
        meses_rango.append((fecha.year, fecha.month))

    ventas_mensuales = []
    gastos_mensuales = []
    etiquetas = []

    # Diccionario para traducir número de mes → nombre
    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    datos_presentes = False  # variable para detectar si hay al menos un registro

    for anio, mes in meses_rango:
        inf = InformeCostos.objects.filter(anio=anio, mes=mes).first()
        if inf:
            ventas_mensuales.append(float(inf.resumen_ventas))
            gastos_mensuales.append(float(inf.resumen_gastos+inf.resumen_remuneraciones))
            datos_presentes = True
        else:
            ventas_mensuales.append(0)
            gastos_mensuales.append(0)

        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")

    if not datos_presentes:  # si todos los meses son cero / no hay registros
        return None

    return [etiquetas, ventas_mensuales, gastos_mensuales]

def obtKpi_02():
    hoy = date.today()
    anio_actual = hoy.year
    mes_actual = hoy.month

    gastos = (
        MovimientoEconomico.objects
        .filter(naturaleza='GA', fecha__year=anio_actual, fecha__month=mes_actual)
        .values('categoria')
        .annotate(total=Sum('total'))
        .order_by('categoria')
    )
    if not gastos.exists():
        return None
    
    etiquetas = [g['categoria'] for g in gastos]
    valores = [float(g['total'] or 0) for g in gastos]

    return [etiquetas, valores]