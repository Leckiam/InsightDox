import pandas as pd
import joblib
from django.conf import settings
import os
from .gcp_gsc import subir_modelo

class AnalizadorMovimientos:
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el analizador con un DataFrame de movimientos.
        Convierte la columna 'fecha' a tipo datetime.
        """
        self.df = df.copy()
        self.df['fecha'] = pd.to_datetime(self.df['fecha'], errors='coerce')

    # ====== 🔹 FILTROS DE FECHA ======
    def mes_nro(self, mes):
        """
        Convierte el nombre de un mes (str) a su número correspondiente (1-12).
        Devuelve None si no se reconoce el nombre del mes.
        """
        if isinstance(mes, str):
            meses = {
                "enero": 1, "febrero": 2, "marzo": 3, "abril": 4,
                "mayo": 5, "junio": 6, "julio": 7, "agosto": 8,
                "septiembre": 9, "octubre": 10, "noviembre": 11, "diciembre": 12
            }
            mes = meses.get(mes.lower(), None)
        return mes

    def _filtrar_fecha(self, dia=None, mes=None, anio=None):
        """
        Filtra el DataFrame según día, mes y año si se proporcionan.
        Devuelve un DataFrame filtrado.
        """
        df_filtrado = self.df.copy()
        
        if dia not in (None, "", "None"):
            df_filtrado = df_filtrado[df_filtrado['fecha'].dt.day == int(dia)]
        if mes not in (None, "", "None"):
            df_filtrado = df_filtrado[df_filtrado['fecha'].dt.month == self.mes_nro(mes)]
        if anio not in (None, "", "None"):
            df_filtrado = df_filtrado[df_filtrado['fecha'].dt.year == int(anio)]

        return df_filtrado

    # ====== 🔹 MÉTODOS INTERNOS ======
    def cantidad_movimientos(self, dia=None, mes=None, anio=None):
        """
        Devuelve la cantidad de movimientos registrados en el rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        return len(df)
    
    def cantidad_movimientos_tipo(self, tipo, dia=None, mes=None, anio=None):
        """
        Devuelve la cantidad de movimientos registrados por el tipo y por el rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df['naturaleza'] == tipo]
        if df.empty:
            return "No hay registros de este tipo en ese rango de fecha."
        return len(df)

    def categorias_disponibles(self, dia=None, mes=None, anio=None):
        """
        Devuelve una lista de categorías distintas presentes en los movimientos
        del rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        return df['categoria'].unique().tolist()
    
    def categorias_por_tipo(self, tipo, dia=None, mes=None, anio=None):
        """
        Devuelve una lista de categorías distintas presentes en los movimientos
        del tipo especificado ('VE', 'GA' o 'RE') y rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df['naturaleza'] == tipo]
        return df['categoria'].unique().tolist()

    def cantidad_movimientos_por_categoria(self, dia=None, mes=None, anio=None):
        """
        Devuelve un diccionario con la cantidad de movimientos por cada categoría
        en el rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        return df.groupby('categoria').size().to_dict()

    def resumen_numerico(self, dia=None, mes=None, anio=None):
        """
        Devuelve estadísticas numéricas de los movimientos del rango de fecha indicado:
        - promedio_total
        - mediana_total
        - moda_total
        - total_mas_alto
        - total_mas_bajo
        """
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return "No hay movimientos en ese rango de fecha."
        moda_total = df['total'].mode()
        return {
            'promedio_total': df['total'].mean(),
            'mediana_total': df['total'].median(),
            'moda_total': moda_total.iloc[0] if not moda_total.empty else None,
            'total_mas_alto': df['total'].max(),
            'total_mas_bajo': df['total'].min()
        }

    def movimiento_mas_reciente(self, dia=None, mes=None, anio=None):
        """
        Devuelve el movimiento más reciente dentro del rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        fila = df.loc[df['fecha'].idxmax()]
        return fila.to_dict()

    def movimiento_mas_antiguo(self, dia=None, mes=None, anio=None):
        """
        Devuelve el movimiento más antiguo dentro del rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        fila = df.loc[df['fecha'].idxmin()]
        return fila.to_dict()

    def precio_unitario_extremos(self, dia=None, mes=None, anio=None):
        """
        Devuelve los movimientos con el precio unitario más alto y más bajo
        en el rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        return {
            'mas_alto': df.loc[df['precio_unitario'].idxmax()].to_dict(),
            'mas_bajo': df.loc[df['precio_unitario'].idxmin()].to_dict()
        }

    def total_extremos(self, dia=None, mes=None, anio=None):
        """
        Devuelve los movimientos con el total más alto y más bajo
        en el rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        return {
            'mas_alto': df.loc[df['total'].idxmax()].to_dict(),
            'mas_bajo': df.loc[df['total'].idxmin()].to_dict()
        }

    def cantidad_extremos(self, dia=None, mes=None, anio=None):
        """
        Devuelve los movimientos con la cantidad más alta y más baja
        en el rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        return {
            'mas_alta': df.loc[df['cantidad'].idxmax()].to_dict(),
            'mas_baja': df.loc[df['cantidad'].idxmin()].to_dict()
        }

    def por_naturaleza(self, tipo, dia=None, mes=None, anio=None):
        """
        Devuelve estadísticas de los movimientos filtrados por tipo ('VE', 'GA', 'RE'):
        - cantidad de movimientos (cantidad)
        - promedio del total de movimientos (total_promedio)
        - total mas alto en movimientos (mayor_total)
        - total mas bajo en movimientos (menor_total)
        """
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df['naturaleza'] == tipo]
        if df.empty:
            return "No hay registros de este tipo en ese rango de fecha."
        return {
            'cantidad': len(df),
            'total_promedio': df['total'].mean(),
            'mayor_total': df.loc[df['total'].idxmax()].to_dict(),
            'menor_total': df.loc[df['total'].idxmin()].to_dict()
        }

    def mayor_menor_por_tipo(self, tipo, dia=None, mes=None, anio=None):
        """
        Devuelve los movimientos con el total más alto y más bajo
        para un tipo específico ('VE', 'GA' o 'RE') dentro del rango de fecha indicado.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df['naturaleza'] == tipo]
        if df.empty:
            return f"No hay registros del tipo '{tipo}' en ese rango de fecha."

        fila_mas_alta = df.loc[df['total'].idxmax()]
        fila_mas_baja = df.loc[df['total'].idxmin()]

        return {
            "mas_alta": fila_mas_alta.to_dict(),
            "mas_baja": fila_mas_baja.to_dict()
        }
    
    def predecir_gastos(self, meses_futuros=3):
        """
        Devuelve las predicciones de gastos futuros ('GA') para los próximos meses basadas en los movimientos históricos.
        """
        from prophet import Prophet
        import tempfile
        # Filtrar movimientos de tipo 'GA'
        df = self.df[self.df['naturaleza'] == 'GA'][['fecha', 'total']].copy()
        if df.empty:
            return "No hay datos de gastos ('GA') para generar predicciones."
        print(df.head(5))
        print(df.tail(5))
        
        # Preparar datos para Prophet
        df_prophet = df.rename(columns={'fecha': 'ds', 'total': 'y'})
        print(df_prophet.head(5))
        print(df_prophet.tail(5))

        # Entrenar modelo Prophet
        modelo = Prophet()
        modelo.fit(df_prophet)

        # Guardar modelo
        if settings.DEBUG:
            modelo_path = os.path.join(settings.MEDIA_ROOT, 'modelos', 'modelo_gastos.pkl')
            os.makedirs(os.path.dirname(modelo_path), exist_ok=True)
            joblib.dump(modelo, modelo_path)
            print(f"Modelo guardado localmente en: {modelo_path}")
        else:
            # Guardar en archivo temporal Windows-safe y subir a GCS
            tmp_file = tempfile.NamedTemporaryFile(suffix=".pkl", delete=False)
            tmp_file.close()  # cerrar para que joblib pueda escribir
            joblib.dump(modelo, tmp_file.name)
            subir_modelo(local_file_path=tmp_file.name, blob_name='media/modelos/prophet_gastos.pkl')
            print("Modelo subido a GCS correctamente.")
            os.remove(tmp_file.name)  # borrar el temporal

        # Generar predicción
        future = modelo.make_future_dataframe(periods=meses_futuros, freq='M')
        forecast = modelo.predict(future)
        
        # Filtrar solo meses futuros después del último dato histórico
        ultimo_mes = df_prophet['ds'].dt.to_period('M').max()
        predicciones = forecast[forecast['ds'].dt.to_period('M') > ultimo_mes][['ds','yhat','yhat_lower','yhat_upper']].head(meses_futuros)

        # Convertir a lista de diccionarios
        return predicciones.to_dict(orient='records')
