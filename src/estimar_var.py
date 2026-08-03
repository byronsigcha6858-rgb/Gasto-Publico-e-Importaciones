"""
src/estimar_var.py
Módulo para la estimación econométrica de modelos VAR y VECM,
diagnósticos de residuos, IRF y FEVD para macroeconomía de Ecuador.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from statsmodels.tsa.api import VAR
from statsmodels.tsa.vector_ar.vecm import coint_johansen, VECM
from statsmodels.tsa.stattools import adfuller, kpss

class EconometricModeler:
    def __init__(self, data_path: Path, variables: list):
        self.data_path = data_path
        self.variables = variables
        self.df = pd.read_csv(data_path, index_col=0, parse_dates=True)[variables]
        self.var_model = None
        self.vecm_model = None
        self.results = {}

    def probar_raiz_unitaria(self) -> pd.DataFrame:
        """
        Ejecuta la prueba Augmented Dickey-Fuller (ADF) en niveles y primeras diferencias.
        """
        resultados = []
        for var in self.variables:
            # Niveles
            adf_niv = adfuller(self.df[var].dropna(), autolag='AIC')
            # Primeras diferencias
            adf_dif = adfuller(self.df[var].diff().dropna(), autolag='AIC')
            
            resultados.append({
                'Variable': var,
                'ADF_Stat_Niveles': round(adf_niv[0], 4),
                'p_value_Niveles': round(adf_niv[1], 4),
                'Estacionaria_Niveles': adf_niv[1] < 0.05,
                'ADF_Stat_Diferencia': round(adf_dif[0], 4),
                'p_value_Diferencia': round(adf_dif[1], 4),
                'Estacionaria_Diferencia': adf_dif[1] < 0.05
            })
        
        df_res = pd.DataFrame(resultados)
        self.results['unit_root'] = df_res
        return df_res

    def seleccionar_rezagos(self, max_lags: int = 6) -> dict:
        """
        Determina el número óptimo de rezagos para el VAR usando AIC, BIC y HQIC.
        """
        model = VAR(self.df)
        order_selection = model.select_order(maxlags=max_lags)
        
        selected = {
            'aic': int(order_selection.selected_orders['aic']),
            'bic': int(order_selection.selected_orders['bic']),
            'hqic': int(order_selection.selected_orders['hqic'])
        }
        self.results['lags'] = selected
        return selected

    def prueba_cointegracion_johansen(self, k_ar_diff: int = 1) -> pd.DataFrame:
        """
        Realiza la prueba de Cointegración de Johansen (Estadístico de la Traza y Máximo Autovalor).
        """
        # det_order=0 supone término constante dentro del espacio de cointegración
        johansen_test = coint_johansen(self.df, det_order=0, k_ar_diff=k_ar_diff)
        
        df_joh = pd.DataFrame({
            'Hipótesis_Nula': [f'r <= {i}' for i in range(len(self.variables))],
            'Estadístico_Traza': np.round(johansen_test.lr1, 4),
            'Valor_Crítico_95%': np.round(johansen_test.cvt[:, 1], 4),
            'Cointegrado': johansen_test.lr1 > johansen_test.cvt[:, 1]
        })
        
        self.results['johansen'] = df_joh
        return df_joh

    def estimar_vecm(self, k_ar_diff: int = 1, coint_rank: int = 1):
        """
        Estima el Modelo de Corrección de Errores Vectorial (VECM).
        """
        vecm = VECM(self.df, k_ar_diff=k_ar_diff, coint_rank=coint_rank, deterministic="co")
        self.vecm_fit = vecm.fit()
        print("✅ Modelo VECM estimado exitosamente.")
        return self.vecm_fit

def ejecutar_diagnostico_completo():
    BASE_DIR = Path(__file__).resolve().parent.parent
    data_path = BASE_DIR / "data" / "processed" / "series_macro_ecuador.csv"
    
    variables_muro = ["log_gasto_gobierno", "log_importaciones", "log_pib_real", "log_exportaciones_no_pet"]
    
    modeler = EconometricModeler(data_path, variables_muro)
    
    print("\n--- 1. PRUEBAS DE RAÍZ UNITARIA (ADF) ---")
    df_adf = modeler.probar_raiz_unitaria()
    print(df_adf.to_string(index=False))
    
    print("\n--- 2. SELECCIÓN ÓPTIMA DE REZAGOS (VAR) ---")
    rezagos = modeler.seleccionar_rezagos(max_lags=5)
    print(f"Rezagos recomendados por AIC: {rezagos['aic']}, BIC: {rezagos['bic']}")
    
    print("\n--- 3. PRUEBA DE COINTEGRACIÓN DE JOHANSEN ---")
    k_diff = max(1, rezagos['aic'] - 1)
    df_joh = modeler.prueba_cointegracion_johansen(k_ar_diff=k_diff)
    print(df_joh.to_string(index=False))
    
    print("\n--- 4. ESTIMACIÓN VECM ---")
    vecm_res = modeler.estimar_vecm(k_ar_diff=k_diff, coint_rank=1)
    
    # Guardar tablas de salida en outputs/tables/
    out_tables = BASE_DIR / "outputs" / "tables"
    out_tables.mkdir(parents=True, exist_ok=True)
    df_adf.to_csv(out_tables / "raiz_unitaria.csv", index=False)
    df_joh.to_csv(out_tables / "johansen_cointegracion.csv", index=False)
    
    print(f"\n💾 Tablas guardadas en: {out_tables.relative_to(BASE_DIR)}")

if __name__ == "__main__":
    ejecutar_diagnostico_completo()