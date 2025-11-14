from django.conf import settings
from .gcp_gsc import subir_modelo
import pandas as pd
import numpy as np
import os
import joblib

class AnalizadorMovimientos:
    def __init__(self, df: pd.DataFrame):
        """
        Inicializa el analizador con un DataFrame de movimientos.
        Convierte la columna 'fecha' a tipo datetime.
        """
        self.df = df.copy()
        self.df['fecha'] = pd.to_datetime(self.df['fecha'], errors='coerce')
        self.df = self.df.sort_values('fecha').reset_index(drop=True)

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
    def cantidad_movimientos(self, tipo=None, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        if tipo:
            df = df[df['naturaleza'] == tipo]
        return len(df) if not df.empty else 0

    def categorias_por_tipo(self, tipo=None, dia=None, mes=None, anio=None, ordenar_por="total", descendente=True):
        """
        Devuelve las categorías filtradas por tipo y fecha.
        - tipo: 'VE', 'GA', 'RE', o None para todas.
        - ordenar_por: 'total', 'cantidad', 'precio_unitario' o None.
        - descendente: True para orden descendente, False para ascendente.
        """
        df = self._filtrar_fecha(dia, mes, anio)
        por = ''
        if tipo:
            df = df[df["naturaleza"] == tipo]
        
        if df.empty:
            return []

        if ordenar_por == "total":
            serie = df.groupby("categoria")["total"].sum().sort_values(ascending=descendente).to_dict()
            por = 'tot'
        elif ordenar_por == "cantidad":
            serie = df.groupby("categoria").size().sort_values(ascending=descendente).to_dict()
            por = 'cant'
        elif ordenar_por == "precio_unitario":
            serie = df.groupby("categoria")["precio_unitario"].mean().sort_values(ascending=descendente).to_dict()
            por = 'precio_unitario'
        else:
            categorias = df['categoria'].unique().tolist()
            return {i+1: {"cat": cat, "tot": None} for i, cat in enumerate(categorias)}
        # Convertir a lista de tuplas (posición, categoría, valor)
        resultado = {i+1: {"cat": cat, por: valor} for i, (cat, valor) in enumerate(serie.items())}
        return resultado


    def cantidad_movimientos_por_categoria(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        return df.groupby('categoria').size().to_dict()

    def estadisticas_basicas_tipo(self, tipo, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df["naturaleza"] == tipo]
        if df.empty:
            return None
        moda = df["total"].mode()
        return {
            "cantidad": len(df),
            "promedio": df["total"].mean(),
            "mediana": df["total"].median(),
            "moda": moda.iloc[0] if not moda.empty else None
        }

    def _extremos_por_columna(self, df, columna):
        if df.empty:
            return None
        return {
            "mas_alto": df.loc[df[columna].idxmax()].to_dict(),
            "mas_bajo": df.loc[df[columna].idxmin()].to_dict()
        }

    def precio_unitario_extremos(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        return self._extremos_por_columna(df, "precio_unitario")

    def total_extremos(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        return self._extremos_por_columna(df, "total")

    def cantidad_extremos(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        return self._extremos_por_columna(df, "cantidad")

    def movimiento_mas_reciente(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        return df.loc[df['fecha'].idxmax()].to_dict() if not df.empty else None

    def movimiento_mas_antiguo(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        return df.loc[df['fecha'].idxmin()].to_dict() if not df.empty else None
    
    def _preparar_dataset_gastos(self):
        df = self.df[self.df['naturaleza'] == 'GA'][['fecha', 'total']]
        df = df.sort_values('fecha')
        df['t'] = (df['fecha'] - df['fecha'].min()).dt.days
        return df
    
    def total_por_tipo(self, tipo, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df["naturaleza"] == tipo]
        return df["total"].sum() if not df.empty else 0

    def total_por_categoria(self, categoria, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df["categoria"].str.lower() == categoria.lower()]
        return df["total"].sum() if not df.empty else 0

    def distribucion_por_tipo(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        cantidad_total = len(df)
        if cantidad_total == 0:
            return None
        return df["naturaleza"].value_counts(normalize=True).mul(100).round(2).to_dict()

    def acumulado_mensual(self, tipo=None, anio=None):
        df = self._filtrar_fecha(None, None, anio)
        if tipo:
            df = df[df["naturaleza"] == tipo]
        if df.empty:
            return None
        return df.groupby(df["fecha"].dt.month)["total"].sum().to_dict()

    def variacion_mensual(self, tipo=None, anio=None):
        acumulado = self.acumulado_mensual(tipo, anio)
        if not acumulado or len(acumulado) < 2:
            return None
        
        meses = sorted(acumulado.keys())
        tendencia = {}

        for i in range(1, len(meses)):
            anterior = acumulado[meses[i-1]]
            actual = acumulado[meses[i]]
            variacion = ((actual - anterior) / anterior * 100) if anterior != 0 else None
            
            tendencia[meses[i]] = round(variacion, 2) if variacion is not None else None
        
        return tendencia

    def mayor_movimiento_por_categoria(self, categoria, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        df = df[df["categoria"].str.lower() == categoria.lower()]
        return df.loc[df["total"].idxmax()].to_dict() if not df.empty else None

    def categoria_mas_frecuente(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        return df["categoria"].mode().iloc[0]

    def resumen_periodo(self, dia=None, mes=None, anio=None):
        df = self._filtrar_fecha(dia, mes, anio)
        if df.empty:
            return None
        return {
            "total_movimientos": len(df),
            "total_gastos": df[df["naturaleza"] == "GA"]["total"].sum(),
            "total_ventas": df[df["naturaleza"] == "VE"]["total"].sum(),
            "categoria_mas_frecuente": df["categoria"].mode().iloc[0],
            "promedio_totales": df["total"].mean(),
        }

    def _entrenar_modelo_gastos(self, df):
        from sklearn.model_selection import train_test_split
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
        X = df[['t']]
        y = df['total']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        modelo = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        modelo.fit(X, y)
        
        # Predicciones en test
        y_pred = modelo.predict(X_test)

        # Métricas
        mae = mean_absolute_error(y_test, y_pred)
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        print(f"MAE: {mae}, MSE: {mse}, RMSE: {rmse}, R2: {r2}")
        
        # Guardar el modelo localmente
        local_path = os.path.join(settings.BASE_DIR, "config", "modelo", "predecir_gastos.pkl")
        joblib.dump(modelo, local_path)
        if settings.DEBUG == False:
            # Subir el modelo a Google Cloud Storage
            subir_modelo(local_path, "predecir_gastos.pkl")
        
        return modelo

    def _predecir_futuro(self, modelo, df, n):
        ult_fecha = df["fecha"].max()
        ult_t = df["t"].max()

        pred = []
        for i in range(1, n + 1):
            futuro_t = ult_t + 30 * i
            fecha = ult_fecha + pd.DateOffset(months=i)
            valor = modelo.predict([[futuro_t]])[0]

            pred.append({
                "mes": fecha.strftime("%B %Y"),
                "total": round(valor),
                "min": round(valor * 0.85),
                "max": round(valor * 1.15),
            })

        return pred

    def predecir_gastos(self, tipo=None,categoria=None,cant_meses_futuros=1):
        df = self._preparar_dataset_gastos()
        modelo = self._entrenar_modelo_gastos(df)
        return self._predecir_futuro(modelo, df, cant_meses_futuros)
