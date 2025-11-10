import requests, json
import pandas as pd
from . import mineriaDatos as md
from ..models import MovimientoEconomico

def obtenerPromptMD(pregunta):
    prompt = f"""
    Eres un asistente que selecciona el método más adecuado para analizar movimientos económicos.
    Devuelve SOLO un JSON con:
    - accion: nombre del método a usar
    - parametros: diccionario de filtros posibles (dia, mes, anio, tipo)

    Parametro "mes" debe ser un tipo de dato int. Ej: "Enero" es 1

    Tipo suele ser: VE = Ventas; GA = Gastos; RE = Remuneraciones
    
    Métodos disponibles: 
    - cantidad_movimientos(dia=None, mes=None, anio=None): Devuelve el número total de movimientos registrados en el rango de fecha indicado.
    - cantidad_movimientos_tipo(tipo, dia=None, mes=None, anio=None): Devuelve la cantidad de movimientos registrados por el tipo y por el rango de fecha indicado.
    - categorias_disponibles(dia=None, mes=None, anio=None): Devuelve la lista de categorías únicas presentes en los movimientos del rango de fecha.
    - categorias_por_tipo(tipo, dia=None, mes=None, anio=None) : Devuelve una lista de categorías distintas presentes en los movimientos del tipo especificado ('VE', 'GA' o 'RE') y rango de fecha indicado.
    - cantidad_movimientos_por_categoria(dia=None, mes=None, anio=None): Devuelve un conteo de movimientos agrupados por categoría en el rango de fecha.
    - resumen_numerico(dia=None, mes=None, anio=None): Devuelve estadísticas de los movimientos (promedio, mediana, moda, total más alto y total más bajo).
    - movimiento_mas_reciente(dia=None, mes=None, anio=None): Devuelve el movimiento más reciente registrado en el rango de fecha.
    - movimiento_mas_antiguo(dia=None, mes=None, anio=None): Devuelve el movimiento más antiguo registrado en el rango de fecha.
    - precio_unitario_extremos(dia=None, mes=None, anio=None): Devuelve los movimientos con el precio unitario más alto y más bajo en el rango de fecha.
    - total_extremos(dia=None, mes=None, anio=None): Devuelve los movimientos con el total más alto y más bajo en el rango de fecha.
    - cantidad_extremos(dia=None, mes=None, anio=None): Devuelve los movimientos con la cantidad más alta y más baja en el rango de fecha.
    - por_naturaleza(tipo, dia=None, mes=None, anio=None): Devuelve estadísticas de los movimientos filtrados por tipo ('VE', 'GA', 'RE'), incluyendo la cantidad de movimientos, el promedio del total, el total más alto y el total más bajo dentro del rango de fecha indicado.
    - mayor_menor_por_tipo(tipo, dia=None, mes=None, anio=None): Devuelve los movimientos de un tipo específico ('VE', 'GA', 'RE') con total más alto y más bajo en el rango de fecha.

    Pregunta: "{pregunta}"
    """

    return prompt

def limpiar_null(d):
    if isinstance(d, dict):
        return {k: limpiar_null(v) for k, v in d.items() if v is not None}
    elif isinstance(d, list):
        return [limpiar_null(x) for x in d if x is not None]
    else:
        return d

def interpretar_pregunta(pregunta):
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "mistral:7b",
        "prompt": obtenerPromptMD(pregunta),
        "stream": False
    }
    response = requests.post(url, json=data)
    respuesta = response.json().get("response", "")

    try:
        # Intenta parsear el JSON devuelto
        respuesta_json_valido = respuesta.replace("None", "null")
        print(respuesta_json_valido)
        return json.loads(respuesta_json_valido)
    except Exception as e:
        print(f"Error al parsear JSON: {e}")
        print(f"Respuesta recibida: {repr(respuesta)}")
        return {"accion": None, "parametros": {}}

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


def generarRespuesta(request):
    pregunta_tmp = request.data.get("pregunta", "").strip()
    pregunta = normalizar_pregunta(pregunta_tmp)
    
    df = pd.DataFrame(list(MovimientoEconomico.objects.all().values(
        'descripcion', 'categoria', 'naturaleza', 'cantidad', 'unidad',
        'precio_unitario', 'total', 'fecha', 'informe__observaciones'
    )))
    df.rename(columns={'informe__observaciones': 'observacion'}, inplace=True)

    # Analizar
    analizador = md.AnalizadorMovimientos(df)
    interpretacion = interpretar_pregunta(pregunta)
    resultado = ejecutar_accion(analizador, interpretacion)
    print(resultado)
    
    # Crear prompt de redacción
    prompt_respuesta = f"""
    Eres un asistente contable que redacta respuestas breves y claras en español
    basadas en los resultados del análisis de movimientos económicos.

    Instrucciones:
    - Redacta la respuesta en un solo enunciado claro y natural.
    - Corrige cualquier error ortográfico o palabra mal escrita del usuario.
    - No agregues contexto extra ni inventes información.
    - Si hay filtros (día, mes, año, tipo), menciónalos naturalmente.
    - Sé conciso (máximo 2 líneas).
    - El dinero como total o precio_unitario siempres son pesos chilenos (usar $X.XXX CLP), no olvidar el separador de miles (usar '.' no ',').

    Datos:
    - Pregunta del usuario: "{pregunta}"
    - Resultado del análisis: {resultado}
    - Parámetros usados: {interpretacion.get('parametros', {})}

    Ejemplos:
    - "En total hay 54 movimientos registrados en septiembre de 2025."
    - "Durante 2024 se realizaron 120 movimientos de tipo venta (VE) en la Empresa Fenix Ingenieria y Servicios Ltda."
    - "El total más alto registrado este mes fue de $2.500.000 CLP."
    ---

    Escribe solo la respuesta final, sin notas ni marcas de fin.
    """
    
    # === Solicitud a phi3:mini (streaming) ===
    url = "http://localhost:11434/api/generate"
    data = {
        "model": "phi3:mini",
        "prompt": prompt_respuesta,
        "stream": True
        }

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
                        texto_final += fragmento
                        yield fragmento
                except json.JSONDecodeError:
                    continue
