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

def obtn_meses_rango(hoy=True):
    if hoy == True:
        hoy = date.today()
    else:
        lastMovEco = MovimientoEconomico.objects.all().order_by('-id').first()
        hoy = lastMovEco.fecha
    
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

    desc = {
        "explicacion": "Este gráfico muestra cuántas transacciones se realizaron cada mes y cómo fue su crecimiento porcentual. Las barras indican el número total de transacciones y la línea muestra si hubo aumento o disminución en comparación con el mes anterior.",
        "interpretacion": [
            "Si la línea sube → hay más actividad comercial.",
            "Si baja → disminuye el flujo de transacciones."
            ]
    }

    valores = [[etiquetas, num_transacciones_mensual],[etiquetas_crecimiento, crecimiento_mensual]]
    kpi_id = "kpi_03"
    canva_id = "ventasGastosChart"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

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
    
    desc = {
        "explicacion": "Mide el monto promedio que los clientes gastan por transacción cada mes. Permite entender cuánto está dispuesto a pagar un cliente en cada compra.",
        "interpretacion": [
            "Si sube → los clientes gastan más en cada compra.",
            "Si baja → las ventas por cliente son más bajas."
            ]
    }
    valores = [etiquetas, valores_ticket]
    kpi_id = "kpi_04"
    canva_id = "graficoTicket"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

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

    desc = {
        "explicacion": "Indica cuánto se gasta en promedio por cada transacción. Ayuda a evaluar la eficiencia de los costos operacionales asociados a las ventas.",
        "interpretacion": [
            "Un valor bajo → proceso eficiente.",
            "Un valor alto → los costos por venta están aumentando."
            ]
    }
    
    valores = [etiquetas, valores]
    kpi_id = "kpi_05"
    canva_id = "graficoGastoPromedio"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

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
        
    desc = {
        "explicacion": "Este indicador muestra qué porcentaje de las ventas totales se destina a gastos. Permite evaluar la eficiencia operativa de la empresa.",
        "interpretacion": [
            "Bajo porcentaje → buena eficiencia.",
            "Alto porcentaje → los gastos están consumiendo la rentabilidad."
            ]
    }
    
    valores = [etiquetas, valores]
    kpi_id = "kpi_06"
    canva_id = "graficoEficienciaGastos"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]

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
    
    desc = {
        "explicacion": "Muestra cómo han variado los gastos totales mes a mes. Permite identificar tendencias de aumento o reducción en los costos de operación.",
        "interpretacion": [
            "Si la línea sube constantemente → gastos creciendo.",
            "Si baja → la empresa está controlando mejor sus costos."
            ]
    }
    
    valores = [etiquetas, gastos_mensuales]
    kpi_id = "kpi_07"
    canva_id = "graficoEvolucionGastos"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]
    
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

    desc = {
        "explicacion": "Indica el porcentaje de rentabilidad obtenido cada mes del año. Valores positivos indican ganancias y valores negativos indican pérdidas.",
        "interpretacion": [
            "Barras verdes → meses con rentabilidad positiva.",
            "Barras rojas → meses con pérdida (rentabilidad negativa)."
            ]
    }
    
    valores = [etiquetas, rentabilidad_mensual]
    kpi_id = "kpi_08"
    canva_id = "graficoRentabilidadMensual"
    descripcion = desc
    return [valores,kpi_id,canva_id,descripcion]