"""agents/analyst_agent.py.

Agente Econométrico para evaluación de supuestos, selección de modelos (VAR/VECM)
e interpretación técnica.
"""

import numpy as np
import pandas as pd
from statsmodels.tsa.stattools import adfuller


class AnalystAgent:

    def __init__(self, df: pd.DataFrame):
        self.df = df

    def diagnosticar_estacionariedad(
        self, variable: str, significance: float = 0.05
    ) -> dict:
        """Ejecuta la prueba Augmented Dickey-Fuller (ADF) y emite un veredicto."""
        serie = self.df[variable].dropna()
        resultado_adf = adfuller(serie, autolag="AIC")

        p_value = resultado_adf[1]
        es_estacionaria = p_value < significance

        diagnostico = {
            "variable": variable,
            "adf_statistic": float(resultado_adf[0]),
            "p_value": float(p_value),
            "lags_usados": int(resultado_adf[2]),
            "es_estacionaria": es_estacionaria,
            "recomendacion": (
                "La serie es estacionaria I(0)."
                if es_estacionaria
                else "La serie NO es estacionaria I(1). Se requiere tomar primeras diferencias."
            ),
        }
        return diagnostico

    def evaluar_orden_integracion_panel(
        self, variables: list[str]
    ) -> pd.DataFrame:
        """Audita la estacionariedad en niveles y en primeras diferencias para todas las variables."""
        resumen = []
        for var in variables:
            # Prueba en niveles
            diag_niv = self.diagnosticar_estacionariedad(var)

            # Prueba en diferencias
            self.df[f"d_{var}"] = self.df[var].diff()
            diag_dif = self.diagnosticar_estacionariedad(f"d_{var}")

            resumen.append(
                {
                    "Variable": var,
                    "p-val (Niveles)": round(diag_niv["p_value"], 4),
                    "Estacionaria (Niveles)": diag_niv["es_estacionaria"],
                    "p-val (Diferencia)": round(diag_dif["p_value"], 4),
                    "Estacionaria (Diferencia)": diag_dif["es_estacionaria"],
                    "Orden Sugerido": (
                        "I(0)" if diag_niv["es_estacionaria"] else "I(1)"
                    ),
                }
            )
        return pd.DataFrame(resumen)

    def sugerir_modelo(
        self, tiene_cointegracion: bool, max_integration_order: int = 1
    ) -> str:
        """Recomienda entre VAR en diferencias o VECM basándose en los supuestos econométricos."""
        if tiene_cointegracion and max_integration_order == 1:
            return (
                "Sugerencia: Estimar un Modelo de Vector de Corrección de Errores (VECM).\n"
                "Razón: Las series están integradas de orden I(1) y comparten al menos una relación de equilibrio a largo plazo."
            )
        elif not tiene_cointegracion and max_integration_order == 1:
            return (
                "Sugerencia: Estimar un Modelo VAR en primeras diferencias.\n"
                "Razón: No se encontró relación de cointegración; diferenciar previene la regresión espuria."
            )
        else:
            return "Sugerencia: Estimar un Modelo VAR estándar en niveles (series I(0))."


if __name__ == "__main__":
    print("Agente Analista configurado correctamente.")