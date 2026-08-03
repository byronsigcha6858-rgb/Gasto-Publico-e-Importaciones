"""src/exportar_json.py.

Exporta los resultados econométricos del VECM (series históricas, matrices de
coeficientes, pruebas de cointegración y Funciones Impulso-Respuesta)
a un archivo JSON consumible por el Dashboard en Vercel.
"""

import json
from pathlib import Path
import numpy as np
import pandas as pd
from statsmodels.tsa.vector_ar.vecm import VECM, coint_johansen


def exportar_resultados_a_json():
    BASE_DIR = Path(__file__).resolve().parent.parent
    data_path = BASE_DIR / "data" / "processed" / "series_macro_ecuador.csv"
    json_out_path = BASE_DIR / "outputs" / "results" / "dashboard_data.json"

    print("🔄 Generando exportación econométrica a JSON para Vercel...")

    # 1. Cargar datos
    df = pd.read_csv(data_path, index_col=0, parse_dates=True)
    var_cols = [
        "log_gasto_gobierno",
        "log_importaciones",
        "log_pib_real",
        "log_exportaciones_no_pet",
    ]
    df_var = df[var_cols]

    # 2. Re-estimar VECM para extraer matrices
    vecm_model = VECM(df_var, k_ar_diff=1, coint_rank=1, deterministic="co")
    vecm_fit = vecm_model.fit()

    # 3. Calcular Funciones Impulso-Respuesta (IRF) a 10 períodos
    irf = vecm_fit.irf(periods=10)
    irf_res = irf.orth_irfs  # Matriz (periodos x variables x variables)

    # Construir arreglo para la IRF del Gasto sobre Importaciones
    irf_gasto_imp = [
        {
            "periodo": t,
            "respuesta": float(round(irf_res[t, 1, 0], 6)),
            "acumulado": float(
                round(np.sum([irf_res[i, 1, 0] for i in range(t + 1)]), 6)
            ),
        }
        for t in range(11)
    ]

    # 4. Formatear datos de series históricas para gráficos
    series_historicas = []
    for idx, row in df_var.iterrows():
        fecha_str = (
            f"{idx.year}-Q{idx.quarter}"
            if hasattr(idx, "quarter")
            else str(idx)[:10]
        )
        series_historicas.append(
            {
                "fecha": fecha_str,
                "gasto_gobierno": float(round(row["log_gasto_gobierno"], 4)),
                "importaciones": float(round(row["log_importaciones"], 4)),
                "pib_real": float(round(row["log_pib_real"], 4)),
                "exportaciones_no_pet": float(
                    round(row["log_exportaciones_no_pet"], 4)
                ),
            }
        )

    # 5. Estructura JSON unificada
    payload = {
        "metadata": {
            "titulo": "Análisis Econométrico: Gasto Público e Importaciones en Ecuador",
            "metodologia": "Vector Error Correction Model (VECM)",
            "observaciones": len(df_var),
            "periodo_cobertura": f"{series_historicas[0]['fecha']} a {series_historicas[-1]['fecha']}",
            "variables": var_cols,
        },
        "diagnosticos": {
            "cointegracion_rank": 1,
            "num_obs": int(vecm_fit.nobs),
            "num_ecuaciones": int(vecm_fit.neqs),
            "k_ar_diff": 1,
        },
        "series_historicas": series_historicas,
        "irf_gasto_hacia_importaciones": irf_gasto_imp,
    }

    # Guardar en outputs/results/dashboard_data.json
    json_out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(json_out_path, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(
        f"✅ Archivo JSON exportado exitosamente en: {json_out_path.relative_to(BASE_DIR)}"
    )


if __name__ == "__main__":
    exportar_resultados_a_json()