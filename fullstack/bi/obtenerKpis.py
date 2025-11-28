from django.db.models import Sum
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from dateutil.relativedelta import relativedelta
from datetime import date,datetime
from . models import InformeCostos, MovimientoEconomico

def obtDF():
    df = pd.DataFrame(list(MovimientoEconomico.objects.all().values(
        'descripcion', 'categoria', 'naturaleza', 'cantidad', 'unidad',
        'precio_unitario', 'total', 'fecha', 'informe__observaciones'
    )))
    df.rename(columns={'informe__observaciones': 'observacion'}, inplace=True)
    return df

def obtn_meses_rango(anio_param=None, mes_param=None):
    # Si el usuario entrega parámetros válidos → se usan
    if anio_param is not None and mes_param is not None:
        hoy = date(anio_param, mes_param, 1)
    else:
        # Si NO entrega parámetros → usar fecha actual
        hoy = date.today()

    meses_rango = []
    for i in range(12):
        fecha = hoy - relativedelta(months=11 - i)
        meses_rango.append((fecha.year, fecha.month))

    return meses_rango

def obtKpi_01(anio_param=None, mes_param=None):
    meses_rango = obtn_meses_rango(anio_param, mes_param)

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

    desc = {
        "explicacion": "Muestra las ventas comparadas con los gastos y remuneraciones durante los últimos 12 meses.",
        "interpretacion": [
            "Ventas arriba de gastos + remuneraciones → Negocio rentable",
            "Ventas cerca o debajo de gastos + remuneraciones → Reducción de margen o posibles pérdidas",
            "Picos o valles → Identifica meses de alto o bajo desempeño"
        ]
    }
    valores = [etiquetas, ventas_mensuales, gastos_mensuales]
    kpi_id = "kpi_01"
    canva_id = "ventasGastosChart"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

def obtKpi_02(anio_param=None, mes_param=None):
    if anio_param==None and mes_param==None:
        ultimo_informe = InformeCostos.objects.order_by('-anio','-mes').first()
        anio = ultimo_informe.anio
        mes = ultimo_informe.mes
    else:
        anio = anio_param
        mes = mes_param
    gastos = (
        MovimientoEconomico.objects
        .filter(naturaleza='GA', fecha__year=anio, fecha__month=mes)
        .values('categoria')
        .annotate(total=Sum('total'))
        .order_by('categoria')
    )
    if not gastos.exists():
        return None
    
    etiquetas = [g['categoria'] for g in gastos]
    valores = [float(g['total'] or 0) for g in gastos]

    desc = {
        "explicacion": "Muestra la distribución de los gastos por categoría en el mes más reciente.",
        "interpretacion": [
            "Cada porción representa el peso relativo de cada categoría en los gastos totales del mes",
            "Porciones grandes → Categoría con mayor gasto",
            "Permite identificar rápidamente dónde se concentra el gasto mensual"
        ]
    }
    valores = [etiquetas, valores]
    kpi_id = "kpi_02"
    canva_id = "gastosCategoriaChart"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

def obtKpi_03(anio_param=None, mes_param=None):
    #Número de transacciones y crecimiento mensual
    meses_rango = obtn_meses_rango(anio_param, mes_param)

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

    desc = {
        "explicacion": "Cuenta la cantidad de contratos u órdenes de servicio facturados cada mes y muestra cómo crece o decrece la actividad.",
        "interpretacion": [
            "Si la línea sube → Aumento de clientes o servicios prestados",
            "Si baja → Caída en la demanda."
            ]
    }

    valores = [[etiquetas, num_transacciones_mensual],[etiquetas_crecimiento, crecimiento_mensual]]
    kpi_id = "kpi_03"
    canva_id = "transaccionesChart"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

def obtKpi_04(anio_param=None, mes_param=None):
    #Ticket Promedio Mensual
    meses_rango = obtn_meses_rango(anio_param, mes_param)
    
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
    
    desc = {
        "explicacion": "Mide cuánto, en promedio, paga un cliente por cada contrato u orden de servicio.",
        "interpretacion": [
            "Si sube → Servicios más complejos o de mayor valor",
            "Si baja → Servicios más pequeños o descuentos aplicados"
            ]
    }
    valores = [etiquetas, valores_ticket]
    kpi_id = "kpi_04"
    canva_id = "graficoTicket"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

def obtKpi_05(anio_param=None, mes_param=None):
    #Gasto promedio por transacción
    meses_rango = obtn_meses_rango(anio_param, mes_param)
    
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

    desc = {
        "explicacion": "Indica cuánto cuesta, en promedio, prestar un servicio (considerando solo gastos, no remuneraciones).",
        "interpretacion": [
            "Un valor bajo → Eficiente en costos operativos",
            "Un valor alto → Costos directos elevados."
            ]
    }
    
    valores = [etiquetas, valores]
    kpi_id = "kpi_05"
    canva_id = "graficoGastoPromedio"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

def obtKpi_06(anio_param=None, mes_param=None):
    #Gráfico de eficiencia de gastos
    meses_rango = obtn_meses_rango(anio_param, mes_param)
    
    etiquetas = []
    valores = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        total_gastos = MovimientoEconomico.objects.filter(naturaleza='GA', fecha__year=anio, fecha__month=mes).aggregate(total=Sum('total'))['total'] or 0
        total_ventas = MovimientoEconomico.objects.filter(naturaleza='VE', fecha__year=anio, fecha__month=mes).aggregate(total=Sum('total'))['total'] or 0
        porcentaje = (total_gastos / total_ventas * 100) if total_ventas else 0
        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        valores.append(round(porcentaje,2))
        
    desc = {
        "explicacion": "Muestra qué porcentaje de los ingresos se gasta en costos operativos (sin remuneraciones).",
        "interpretacion": [
            "Bajo porcentaje → Buena eficiencia operativa.",
            "Alto porcentaje → Gastos operativos consumen gran parte de los ingresos."
            ]
    }
    
    valores = [etiquetas, valores]
    kpi_id = "kpi_06"
    canva_id = "graficoEficienciaGastos"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

def obtKpi_07(anio_param=None, mes_param=None):
    #evolucion_y_eficiencia_gastos
    meses_rango = obtn_meses_rango(anio_param, mes_param)
    
    etiquetas = []
    gastos_mensuales = []

    MESES_CHOICES = dict(InformeCostos.MESES_CHOICES)

    for anio, mes in meses_rango:
        total_gastos = MovimientoEconomico.objects.filter(naturaleza='GA', fecha__year=anio, fecha__month=mes).aggregate(total=Sum('total'))['total'] or 0
        
        etiquetas.append(f"{MESES_CHOICES[mes][:3]} {anio}")
        gastos_mensuales.append(float(total_gastos))
    
    desc = {
        "explicacion": "Muestra cómo cambian los gastos operativos totales mes a mes.",
        "interpretacion": [
            "Si la línea sube constantemente → Aumento de costos.",
            "Si baja → control o reducción de costos."
            ]
    }
    
    valores = [etiquetas, gastos_mensuales]
    kpi_id = "kpi_07"
    canva_id = "graficoEvolucionGastos"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]
    
def obtKpi_08(anio_param=None, mes_param=None):
    meses_rango = obtn_meses_rango(anio_param, mes_param)
    
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

    desc = {
        "explicacion": "Calcula la rentabilidad considerando Ventas – (Gastos + Remuneraciones), expresada como porcentaje de las ventas.",
        "interpretacion": [
            "Barras verdes → Los ingresos cubren costos operativos y remuneraciones, negocio rentable.",
            "Barras rojas → Los costos y sueldos superan los ingresos, alerta de pérdidas."
            ]
    }
    
    valores = [etiquetas, rentabilidad_mensual]
    kpi_id = "kpi_08"
    canva_id = "graficoRentabilidadMensual"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]