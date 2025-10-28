from django.db.models import Sum,Count
from datetime import date,timedelta
from dateutil.relativedelta import relativedelta
import datetime
from . models import InformeCostos, MovimientoEconomico

def obtn_meses_rango():
    hoy = date.today()
    
    # Generar los últimos 12 meses desde el último registro
    meses_rango = []
    for i in range(12):
        fecha = hoy - relativedelta(months=11-i)  # 11-i para que quede en orden cronológico
        meses_rango.append((fecha.year, fecha.month))
    return meses_rango

def obtKpi_01():
    meses_rango = obtn_meses_rango()

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
    ultimo_informe = InformeCostos.objects.order_by('-anio','-mes').first()
    
    gastos = (
        MovimientoEconomico.objects
        .filter(naturaleza='GA', fecha__year=ultimo_informe.anio, fecha__month=ultimo_informe.mes)
        .values('categoria')
        .annotate(total=Sum('total'))
        .order_by('categoria')
    )
    if not gastos.exists():
        return None
    
    etiquetas = [g['categoria'] for g in gastos]
    valores = [float(g['total'] or 0) for g in gastos]

    return [etiquetas, valores]

def obtKpi_03():
    #Número de transacciones y crecimiento mensual
    meses_rango = obtn_meses_rango()

    num_transacciones_mensual = []
    ventas_totales_mensual = []
    etiquetas = []
    
    # Diccionario para traducir número de mes → nombre
    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)
    
    for anio, mes in meses_rango:
        ventas_mes = MovimientoEconomico.objects.filter(
            naturaleza='VE', fecha__year=anio, fecha__month=mes
        )
        num_transacciones_mensual.append(ventas_mes.count())
        
        total_mes = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
        ventas_totales_mensual.append(float(total_mes))

        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")

    # Calcular crecimiento mensual (%)
    crecimiento_mensual = []
    for i in range(1, len(ventas_totales_mensual)):
        anterior = ventas_totales_mensual[i-1]
        actual = ventas_totales_mensual[i]
        if anterior == 0:
            crecimiento_mensual.append(None)
        else:
            crecimiento_mensual.append(((actual - anterior) / anterior) * 100)
            
    etiquetas_crecimiento = etiquetas[1:]

    return [[etiquetas, num_transacciones_mensual],[etiquetas_crecimiento, crecimiento_mensual]]

def obtKpi_04():
    #Ticket Promedio Mensual
    meses_rango = obtn_meses_rango()
    
    etiquetas = []
    valores_ticket = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        ventas_mes = MovimientoEconomico.objects.filter(naturaleza='VE', fecha__year=anio, fecha__month=mes)
        total_ventas = ventas_mes.aggregate(total=Sum('total'))['total'] or 0
        num_transacciones = ventas_mes.count()
        
        # Ticket promedio
        if num_transacciones == 0:
            ticket = 0
        else:
            ticket = total_ventas / num_transacciones
        
        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        valores_ticket.append(round(ticket, 2))  # opcional: redondear a 2 decimales

    return [etiquetas, valores_ticket]

def obtKpi_05():
    #Gasto promedio por transacción
    meses_rango = obtn_meses_rango()
    
    etiquetas = []
    valores = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        gastos_mes = MovimientoEconomico.objects.filter(naturaleza='GA', fecha__year=anio, fecha__month=mes)
        total_gastos = gastos_mes.aggregate(total=Sum('total'))['total'] or 0
        num_gastos = gastos_mes.count()
        gasto_promedio = total_gastos / num_gastos if num_gastos else 0
        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        valores.append(round(gasto_promedio,2))

    return [etiquetas, valores]

def obtKpi_06():
    #Gráfico de eficiencia de gastos
    meses_rango = obtn_meses_rango()
    
    etiquetas = []
    valores = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        total_gastos = MovimientoEconomico.objects.filter(naturaleza='GA', fecha__year=anio, fecha__month=mes).aggregate(total=Sum('total'))['total'] or 0
        total_ventas = MovimientoEconomico.objects.filter(naturaleza='VE', fecha__year=anio, fecha__month=mes).aggregate(total=Sum('total'))['total'] or 0
        porcentaje = (total_gastos / total_ventas * 100) if total_ventas else 0
        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        valores.append(round(porcentaje,2))

    return [etiquetas, valores]

def obtKpi_07():
    #evolucion_y_eficiencia_gastos
    meses_rango = obtn_meses_rango()
    
    etiquetas = []
    gastos_mensuales = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        total_gastos = MovimientoEconomico.objects.filter(naturaleza='GA', fecha__year=anio, fecha__month=mes).aggregate(total=Sum('total'))['total'] or 0
        
        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        gastos_mensuales.append(float(total_gastos))
    
    return [etiquetas, gastos_mensuales]
    
def obtKpi_08():
    meses_rango = obtn_meses_rango()
    
    etiquetas = []
    rentabilidad_mensual = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        total_ventas = MovimientoEconomico.objects.filter(
            naturaleza='VE',
            fecha__year=anio,
            fecha__month=mes
        ).aggregate(total=Sum('total'))['total'] or 0

        total_gastos = MovimientoEconomico.objects.filter(
            naturaleza='GA',
            fecha__year=anio,
            fecha__month=mes
        ).aggregate(total=Sum('total'))['total'] or 0

        total_remu = MovimientoEconomico.objects.filter(
            naturaleza='RE',
            fecha__year=anio,
            fecha__month=mes
        ).aggregate(total=Sum('total'))['total'] or 0

        if total_ventas > 0:
            rent_mes = ((total_ventas - (total_gastos + total_remu)) / total_ventas) * 100
        else:
            rent_mes = 0

        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        rentabilidad_mensual.append(round(rent_mes, 2))

    return [etiquetas, rentabilidad_mensual]