"""src/cargar_datos.py.

Módulo para cargar, limpiar y transformar las series de tiempo de Cuentas Nacionales
del Banco Central del Ecuador (BCE).
"""

from pathlib import Path
import numpy as np
import pandas as pd


def generar_datos_simulados_bce(
    inicio: str = "2010-01-01", periodos: int = 60
) -> pd.DataFrame:
    """Genera un DataFrame trimestral realista con cointegración para pruebas de pipeline

    cuando no se dispone inmediatamente del archivo oficial del BCE.
    """
    np.random.seed(42)
    fechas = pd.date_range(start=inicio, periods=periodos, freq="QE")

    # Componente de tendencia común (Raíz unitaria compartida / Cointegración)
    tendencia_comun = np.cumsum(np.random.normal(0.5, 1.2, periodos)) + 100

    # Generación de series en niveles (USD millones)
    gasto_gobierno = (
        1200
        + 12 * tendencia_comun
        + np.random.normal(0, 30, periodos)
        + np.sin(np.linspace(0, 10 * np.pi, periodos)) * 40
    )
    pib_real = (
        15000
        + 85 * tendencia_comun
        + np.random.normal(0, 150, periodos)
        + np.sin(np.linspace(0, 10 * np.pi, periodos)) * 200
    )
    importaciones = (
        3000
        + 0.25 * pib_real
        + 0.4 * gasto_gobierno
        + np.random.normal(0, 80, periodos)
    )
    exportaciones_no_pet = (
        2000
        + 15 * tendencia_comun
        + np.random.normal(0, 50, periodos)
        + np.cos(np.linspace(0, 10 * np.pi, periodos)) * 60
    )

    df = pd.DataFrame(
        {
            "gasto_gobierno": gasto_gobierno,
            "importaciones": importaciones,
            "pib_real": pib_real,
            "exportaciones_no_pet": exportaciones_no_pet,
        },
        index=fechas,
    )

    return df


def transformar_series(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica transformaciones logarítmicas y diferencias para análisis econométrico."""
    cols_base = [
        "gasto_gobierno",
        "importaciones",
        "pib_real",
        "exportaciones_no_pet",
    ]
    df_transformed = df.copy()

    # 1. Aplicar logaritmo natural
    for col in cols_base:
        df_transformed[f"log_{col}"] = np.log(df_transformed[col])

    # 2. Primeras diferencias de los logaritmos (tasas de crecimiento aproximadas)
    for col in cols_base:
        df_transformed[f"d_log_{col}"] = df_transformed[f"log_{col}"].diff()

    return df_transformed.dropna()


def ejecutar_pipeline_datos():
    """Ejecuta la ingesta, transformación y almacenamiento del dataset procesado."""
    BASE_DIR = Path(__file__).resolve().parent.parent
    ruta_raw = BASE_DIR / "data" / "raw" / "bce_cuentas_nacionales.xlsx"
    ruta_out = BASE_DIR / "data" / "processed" / "series_macro_ecuador.csv"

    print("🔄 Iniciando pipeline de carga de datos...")

    if ruta_raw.exists():
        print(f"📄 Archivo oficial encontrado en: {ruta_raw}")
        df_raw = pd.read_excel(ruta_raw, sheet_name="Cuentas_Trimestrales")
        df_raw["fecha"] = pd.date_range(
            start="2010-01-01", periods=len(df_raw), freq="QE"
        )
        df_raw.set_index("fecha", inplace=True)
    else:
        print(
            "⚠️ No se encontró el archivo 'bce_cuentas_nacionales.xlsx' en 'data/raw/'."
        )
        print(
            "💡 Generando datos trimestrales con estructura macroeconómica de Ecuador..."
        )
        df_raw = generar_datos_simulados_bce()

    # Transformación
    df_procesado = transformar_series(df_raw)

    # Guardar en data/processed/
    ruta_out.parent.mkdir(parents=True, exist_ok=True)
    df_procesado.to_csv(ruta_out)

    inicio_str = f"{df_procesado.index.min().year}-Q{df_procesado.index.min().quarter}"
    fin_str = f"{df_procesado.index.max().year}-Q{df_procesado.index.max().quarter}"

    print(
        f"✅ Dataset procesado guardado exitosamente en: {ruta_out.relative_to(BASE_DIR)}"
    )
    print(f"📊 Total de observaciones: {len(df_procesado)}")
    print(f"📅 Período: {inicio_str} a {fin_str}\n")


if __name__ == "__main__":
    ejecutar_pipeline_datos()