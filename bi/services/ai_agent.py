from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from django.conf import settings
from datetime import datetime
import os
import joblib
import requests, json
import pandas as pd
from . import mineriaDatos as md
from ..models import MovimientoEconomico

url = "http://localhost:11434/api/generate"

def extraer_parametros(pregunta: str):
    parametros = {}

    # ---- Tipo ----
    ventas_kw = [
        "venta", "ventas", "vender", "vendí", "vendido",
        "ingreso", "ingresos", "entró dinero", "entradas de dinero",
        "facturación", "facturar", "boleta de venta", "ticket de venta"
    ]

    gastos_kw = [
        "gasto", "gastos", "gastar", "pagado", "pagué", "pagar",
        "costo", "costos", "egreso", "egresos",
        "salida de dinero", "desembolso", "compras", "consumo"
    ]

    remuneraciones_kw = [
        "sueldo", "sueldos", "salario", "salarios",
        "remuneración", "remuneraciones",
        "pago de empleados", "personal", "nomina", "honorarios"
    ]

    if any(t in pregunta for t in ventas_kw):
        parametros["tipo"] = "VE"
    if any(t in pregunta for t in gastos_kw):
        parametros["tipo"] = "RE"
    if any(t in pregunta for t in remuneraciones_kw):
        parametros["tipo"] = "GA"
        
    # ---- Meses ----
    meses = {
        "enero": 1, "febrero": 2, "marzo": 3, "abril": 4, "mayo": 5, "junio": 6,
        "julio": 7, "agosto": 8, "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
    }

    for nombre, numero in meses.items():
        if nombre in pregunta.lower():
            parametros["mes"] = numero

    # Mes actual / anterior
    mes_actual = datetime.now().month

    if "mes pasado" in pregunta.lower() or "mes anterior" in pregunta.lower():
        parametros["mes"] = mes_actual - 1 if mes_actual > 1 else 12

    if "este mes" in pregunta.lower() or "mes actual" in pregunta.lower():
        parametros["mes"] = mes_actual

    # ---- Año ----
    import re
    anio_especifico = re.search(r"(19|20)\d{2}", pregunta)
    if anio_especifico:
        parametros["anio"] = int(anio_especifico.group())
    else:
        anio_actual = datetime.now().year
        print(anio_especifico)
        if "este ano" in pregunta:
            parametros["anio"] = anio_actual
        elif "ano pasado" in pregunta:
            parametros["anio"] = anio_actual - 1
        elif "ano anterior" in pregunta:
            parametros["anio"] = anio_actual - 1
    
    # ---- Categoría ----
    categorias = ["EdP", "MO", "M", "H", "GG", "EPP"]  # Todas las categorías que manejes
    for cat in categorias:
        if cat.lower() in pregunta.lower():
            parametros["categoria"] = cat
            break
    
    # ---- Ordenamiento para ranking ----
    if "ranking" in pregunta.lower() or "ordenadas" in pregunta.lower() or "mayor" in pregunta.lower():
        if "cantidad" in pregunta.lower():
            parametros["ordenar_por"] = "cantidad"
        elif "precio" in pregunta.lower() or "unitario" in pregunta.lower():
            parametros["ordenar_por"] = "precio_unitario"
        else:
            parametros["ordenar_por"] = "total"  # default

    return parametros

def entrenaModelo():
    # Ruta al CSV de entrenamiento
    ruta = os.path.join(settings.BASE_DIR, "config", "data", "intenciones.csv")
    df = pd.read_csv(ruta, comment="#")

    modelo = Pipeline([
        ("vectorizer", TfidfVectorizer()),
        ("classifier", LogisticRegression(max_iter=200))
    ])

    modelo.fit(df["texto"], df["intencion"])

    # Guardar modelo
    ruta_modelo = os.path.join(settings.BASE_DIR, "config", "modelo", "clasificador_intenciones.pkl")
    joblib.dump(modelo, ruta_modelo)

    print("Modelo entrenado y guardado en:", ruta_modelo)

def limpiar_null(d):
    if isinstance(d, dict):
        return {k: limpiar_null(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [limpiar_null(x) for x in d if x is not None]
    else:
        return d

def interpretar_pregunta(pregunta: str):
    ruta_modelo = os.path.join(settings.BASE_DIR, "config", "modelo", "clasificador_intenciones.pkl")
    modelo = joblib.load(ruta_modelo)

    intencion = modelo.predict([pregunta])[0]
    parametros = extraer_parametros(pregunta)

    return {
        "accion": intencion,
        "parametros": parametros
    }

def ejecutar_accion(analizador, interpretacion):
    accion = interpretacion.get("accion")
    parametros = interpretacion.get("parametros", {})

    if not hasattr(analizador, accion):
        return {"error": f"Método '{accion}' no encontrado."}

    metodo = getattr(analizador, accion)
    return metodo(**parametros)

import re
import unicodedata

def normalizar_pregunta(pregunta: str) -> str:
    # Pasar a minúsculas
    pregunta = pregunta.lower().strip()

    # Quitar tildes y acentos
    pregunta = ''.join(
        c for c in unicodedata.normalize('NFD', pregunta)
        if unicodedata.category(c) != 'Mn'
    )

    # Quitar signos de puntuación y caracteres especiales
    pregunta = re.sub(r'[^a-z0-9áéíóúñü\s]', '', pregunta)

    # Normalizar espacios
    pregunta = re.sub(r'\s+', ' ', pregunta).strip()

    # Reemplazar abreviaturas comunes
    reemplazos = {
        " sep ": "septiembre",
        " ene ": "enero",
        " feb ": "febrero",
        " mar ": "marzo",
        " abr ": "abril",
        " ago ": "agosto",
        " dic ": "diciembre",
    }
    for clave, valor in reemplazos.items():
        pregunta = pregunta.replace(clave, valor)

    return pregunta

def abreviar_numero(valor):
    """Convierte números grandes a formato K/M/B"""
    if valor >= 1_000_000_000:
        return f"{valor/1_000_000_000:.2f}B"
    elif valor >= 1_000_000:
        return f"{valor/1_000_000:.2f}M"
    elif valor >= 1_000:
        return f"{valor/1_000:.2f}K"
    else:
        return str(valor)

def formatear_resultado(resultado):
    """Recorre dicts, listas y valores individuales y aplica abreviación"""
    if isinstance(resultado, dict):
        return {k: formatear_resultado(v) for k, v in resultado.items()}
    elif isinstance(resultado, list):
        return [formatear_resultado(v) for v in resultado]
    elif isinstance(resultado, (int, float)):
        return abreviar_numero(resultado)
    return resultado

def generarRespuesta(request):
    pregunta_tmp = request.data.get("pregunta", "").strip()
    pregunta = normalizar_pregunta(pregunta_tmp)
    
    df = pd.DataFrame(list(MovimientoEconomico.objects.all().values(
        'descripcion', 'categoria', 'naturaleza', 'cantidad', 'unidad',
        'precio_unitario', 'total', 'fecha', 'informe__observaciones'
    )))
    df.rename(columns={'informe__observaciones': 'observacion'}, inplace=True)

    # Analizar
    entrenaModelo()
    analizador = md.AnalizadorMovimientos(df)
    interpretacion = interpretar_pregunta(pregunta)
    print(interpretacion)
    resultado = ejecutar_accion(analizador, interpretacion)
    resultado_formateado = formatear_resultado(resultado)
    
    fecha_actual = datetime.now()
    mes = fecha_actual.month
    anio = fecha_actual.year
    fecha_formateada = fecha_actual.strftime("%d-%m-%Y")
    # Crear prompt de redacción
    prompt_respuesta = f"""
    ## Eres un asistente contable que responde brevemente en español sobre movimientos económicos de Fenix Ing. y Servicios Ltda. y la fecha actual es '{fecha_formateada}'

    Instrucciones:
    - Responde en un solo enunciado claro y natural.
    - Menciona día, mes, año o tipo solo si aplica.
    - Sé conciso (máx. 2 líneas).
    - Totales y precios unitarios siempre en pesos chilenos ($X.XXX CLP), con separador de miles.
    - Si en prediccion pide mas de 1 mes, entonces decir que solo se pude calcular hasta el proximo mes.
    - Siempre trata de dar descripcion, categoria, cantidad, total y fecha en la respuesta al movimiento obtenido.
    - Si 'Pregunta' no tiene ano ni mes, entonces mencionar 'hasta el mes {mes} del {anio}'.
    - K: miles
    - M: millones
    - B: miles de millones

    Datos:
    - Pregunta: '{ pregunta }'
    - Resultado: { resultado_formateado }
    - Parámetros usados: {interpretacion.get('parametros', {}) }

    Ejemplos:
    - 'En total hay 54 movimientos registrados en septiembre de 2025.'
    - 'Gastos estimados para octubre 2025: $1K CLP a $10K CLP, promedio $5K CLP.'
    - 'El proximo mes (Diciembre 2025) se espera un gasto estimado de alrededor de $5K CLP (rango entre $4K CLP y $6K CLP).'
    - 'El ranking de categorías [Acendente por total] de los movimientos económicos hasta Diciembre del 2025 es: EPP ($1.00M CLP), GG ($1.11M CLP)'

    Escribe solo la respuesta final.
    """
    
    # === Solicitud a phi3:mini (streaming) ===
    data = {
        "model": "phi3_contable",
        "prompt": prompt_respuesta,
        "stream": True
    }
    print(data)

    texto_final = ""

    with requests.post(url, json=data, stream=True) as response:
        for line in response.iter_lines():
            if line:
                try:
                    token_data = json.loads(line.decode("utf-8"))
                    if "response" in token_data:
                        fragmento = token_data["response"]
                        if "[FIN]" in fragmento:
                            texto_final += fragmento.split("[FIN]")[0]
                            break
                        elif "---" in fragmento or "##" in fragmento:
                            texto_final += fragmento.split("---")[0].split("##")[0]
                            break
                        texto_final += fragmento
                        yield fragmento
                except json.JSONDecodeError:
                    continue
