"""agents/data_agent.py.

Agente de Validación e Ingesta de Datos Econométricos.
"""

from pathlib import Path
import numpy as np
import pandas as pd


class DataAgent:

    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.df = None

    def cargar_datos(self) -> pd.DataFrame:
        """Carga el dataset en formato CSV o Excel."""
        if self.data_path.suffix == ".csv":
            self.df = pd.read_csv(
                self.data_path, index_col=0, parse_dates=True
            )
        elif self.data_path.suffix in [".xlsx", ".xls"]:
            self.df = pd.read_excel(self.data_path)
        else:
            raise ValueError(
                f"Formato de archivo no soportado: {self.data_path.suffix}"
            )
        return self.df

    def auditar_calidad() -> dict:
        """Ejecuta un diagnóstico completo sobre la salud de las series temporal."""
        if self.df is None:
            self.cargar_datos()

        reporte = {
            "num_observaciones": len(self.df),
            "columnas": list(self.df.columns),
            "valores_nulos": self.df.isnull().sum().to_dict(),
            "duplicados": int(self.df.index.duplicated().sum()),
            "rango_fechas": {
                "inicio": str(self.df.index.min()),
                "fin": str(self.df.index.max()),
            },
        }
        return reporte

    def generar_diccionario_md(self, ruta_salida: Path):
        """Genera automáticamente la documentación de las variables en Markdown."""
        reporte = self.auditar_calidad()

        md_content = "# 📖 Diccionario de Variables y Reporte de Datos\n\n"
        md_content += f"**Período evaluado:** {reporte['rango_fechas']['inicio']} a {reporte['rango_fechas']['fin']}\n"
        md_content += f"**Total observaciones:** {reporte['num_observaciones']}\n\n"
        md_content += "| Variable | Tipo de Dato | Nulos | Descripción / Transformación |\n"
        md_content += "|---|---|---|---|\n"

        for col in self.df.columns:
            dtype = str(self.df[col].dtype)
            nulos = self.df[col].isnull().sum()
            md_content += (
                f"| `{col}` | {dtype} | {nulos} | Serie procesada del BCE |\n"
            )

        with open(ruta_salida, "w", encoding="utf-8") as f:
            f.write(md_content)

        print(f"✅ Diccionario de variables generado en: {ruta_salida}")


if __name__ == "__main__":
    # Test rápido de ejecución
    path_datos = (
        Path(__file__).parent.parent
        / "data"
        / "processed"
        / "series_macro_ecuador.csv"
    )
    if path_datos.exists():
        agent = DataAgent(path_datos)
        agent.generar_diccionario_md(
            path_datos.parent / "diccionario_variables.md"
        )
        