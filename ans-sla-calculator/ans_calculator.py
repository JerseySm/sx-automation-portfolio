"""
ANS / SLA Calculator — Reporte Mensual de Suspensiones
-------------------------------------------------------
Automatización del cálculo de cumplimiento de ANS (Acuerdo de Nivel de Servicio)
para el proceso de suspensión. Ajusta fechas según horario hábil y festivos
colombianos, y determina si cada caso cumple el límite de 8 horas.

Elimina el proceso manual de filtrar día a día y ajustar fechas fuera de horario.

Autor: Citlalli Jersey Sanchez Montero
"""

import pandas as pd
import numpy as np
from datetime import datetime, time, timedelta
import holidays


# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────

ARCHIVO_ENTRADA = "archivo.xlsx"
ARCHIVO_SALIDA = "resultado_final.xlsx"

HORARIO_INICIO = time(8, 0, 0)
HORARIO_FIN = time(17, 0, 0)
ANS_HORAS = 8
AÑOS_FESTIVOS = [2025, 2026]

festivos = holidays.Colombia(years=AÑOS_FESTIVOS)


# ──────────────────────────────────────────────
# FUNCIONES DE FECHA HÁBIL
# ──────────────────────────────────────────────

def es_dia_habil(fecha: datetime) -> bool:
    """Retorna True si la fecha es día hábil (lun-vie, no festivo colombiano)."""
    return fecha.weekday() < 5 and fecha.date() not in festivos


def siguiente_dia_habil(fecha: datetime) -> datetime:
    """Avanza al siguiente día hábil."""
    fecha += timedelta(days=1)
    while not es_dia_habil(fecha):
        fecha += timedelta(days=1)
    return fecha


def ajustar_fecha_inicio(fecha: datetime) -> datetime:
    """
    Ajusta la fecha de inicio al horario hábil:
    - Si es fin de semana o festivo → primer día hábil siguiente a las 8 AM
    - Si es antes de las 8 AM → mismo día a las 8 AM
    - Si es después de las 5 PM → siguiente día hábil a las 8 AM
    """
    if not es_dia_habil(fecha):
        fecha = siguiente_dia_habil(fecha)
        return datetime.combine(fecha.date(), HORARIO_INICIO)

    if fecha.time() < HORARIO_INICIO:
        return datetime.combine(fecha.date(), HORARIO_INICIO)

    if fecha.time() > HORARIO_FIN:
        fecha = siguiente_dia_habil(fecha)
        return datetime.combine(fecha.date(), HORARIO_INICIO)

    return fecha


# ──────────────────────────────────────────────
# PROCESAMIENTO
# ──────────────────────────────────────────────

def reconstruir_fechas(df: pd.DataFrame) -> pd.DataFrame:
    """Construye columnas datetime a partir de los campos separados del Excel."""
    df["FechaInicio"] = pd.to_datetime(
        df["Dia_ini"].astype(str) + " " +
        df["Mes_ini"] + " 2026 " +
        df["Hora_ini"].astype(str)
    )
    df["FechaFin"] = pd.to_datetime(
        df["Dia_Fin"].astype(str) + " " +
        df["Mes_Fin"] + " 2026 " +
        df["Hora_Fin"].astype(str)
    )
    return df


def calcular_ans(df: pd.DataFrame) -> pd.DataFrame:
    """Aplica ajuste de horario hábil y calcula cumplimiento de ANS."""

    df["FechaInicio_Ajustada"] = df["FechaInicio"].apply(ajustar_fecha_inicio)
    df["FechaFin_Ajustada"] = df.apply(
        lambda row: max(row["FechaInicio_Ajustada"], row["FechaFin"]),
        axis=1
    )

    # Recalcular campos
    df["Fecha_Ini"] = df["FechaInicio_Ajustada"].dt.strftime("%a")
    df["Mes_ini"] = df["FechaInicio_Ajustada"].dt.strftime("%b")
    df["Dia_ini"] = df["FechaInicio_Ajustada"].dt.day
    df["Hora_ini"] = df["FechaInicio_Ajustada"].dt.strftime("%H:%M:%S")

    df["Dias_Igual"] = np.where(df["Dia_ini"] == df["Dia_Fin"], "VERDADERO", "FALSO")
    df["Fecha_Iguales"] = np.where(df["Mes_ini"] == df["Mes_Fin"], "VERDADERO", "FALSO")

    diff = df["FechaFin_Ajustada"] - df["FechaInicio_Ajustada"]
    df["Horas_Num"] = diff.dt.total_seconds() / 3600
    df["Cumple"] = np.where(df["Horas_Num"] <= ANS_HORAS, "SI", "NO")
    df["Diff_Horas"] = diff.astype(str).str.split(" ").str[-1]

    df.drop(columns=["FechaInicio", "FechaFin", "FechaInicio_Ajustada", "FechaFin_Ajustada", "Horas_Num"], inplace=True)
    return df


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n Iniciando cálculo de ANS...\n")

    df_original = pd.read_excel(ARCHIVO_ENTRADA)
    df = df_original.copy()

    print(" Reconstruyendo fechas...")
    df = reconstruir_fechas(df)

    print("  Calculando cumplimiento de ANS...")
    df = calcular_ans(df)

    cumple = (df["Cumple"] == "SI").sum()
    no_cumple = (df["Cumple"] == "NO").sum()
    print(f"\n Resumen:")
    print(f"   Cumple ANS ({ANS_HORAS}h): {cumple}")
    print(f"   No cumple:              {no_cumple}")
    print(f"   Total:                  {len(df)}")

    with pd.ExcelWriter(ARCHIVO_SALIDA, engine="openpyxl") as writer:
        df_original.to_excel(writer, sheet_name="Original", index=False)
        df.to_excel(writer, sheet_name="Corregido", index=False)

    print(f"\n Resultado guardado: {ARCHIVO_SALIDA}")
    print("\n Proceso completado.\n")
