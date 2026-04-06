"""
OP Suspension Validator
-----------------------
Automatización de prevalidación de órdenes de proceso (OP) de suspensión.
Clasifica cuentas según tipología antes de la gestión manual.

Autor: Citlalli Jersey Sanchez Montero
"""

import os
import pandas as pd


# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────

ARCHIVO_OP = "revision_suspension_20260105v1(op455).csv"
ARCHIVO_CRUZES = "CRUZES.xlsx"
ARCHIVO_SALIDA = "OP_PREVALIDADO.xlsx"

SERVICIOS_SOPORTADOS = [
    "Linea Telefonica",
    "Internet Banda Ancha (ADSL)",
    "IPTV",
    "DirecTVGO",
    "HBOMAX",
    "LTE",
    "Universal",
    "PARAMOUNT",
    "WIN SPORTS",
]


# ──────────────────────────────────────────────
# CARGA DE DATOS
# ──────────────────────────────────────────────

def cargar_op(path: str) -> pd.DataFrame:
    """Carga el archivo OP, elimina duplicados e inicializa columnas de resultado."""
    op = pd.read_csv(path, sep=",", dtype=str, encoding="utf-8")
    op = op.drop_duplicates(subset=["SUB_ID"])
    op["CUENTA_CONCAT"] = "'" + op["SUB_ID"] + "',"
    op["TIPOLOGIA"] = "PENDIENTE VALIDACION"
    op["DETALLE"] = ""
    print(f"  OP cargado: {len(op)} cuentas únicas")
    return op


def cargar_cruzes(path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Carga las tres hojas del archivo de cruces."""
    ult_tramite = pd.read_excel(path, sheet_name="ULTIMO TRAMITE", dtype=str)
    servicios = pd.read_excel(path, sheet_name="ESTADO DE LOS SERVICIOS", dtype=str)
    vs_his = pd.read_excel(path, sheet_name="VS HIS", dtype=str)

    ult_tramite = ult_tramite.rename(columns={"CUENTA": "SUB_ID", "TRAMITE": "TRAMITE_ULTIMO"})
    servicios = servicios.rename(columns={"CUENTA_PADRE": "SUB_ID"})
    vs_his.columns = vs_his.columns.str.strip()
    vs_his = vs_his.rename(columns={"CUENTA": "SUB_ID"})
    vs_his["FECHA_FIN_SUSPENSION"] = vs_his["FECHA_FIN_SUSPENSION"].fillna("")

    print(f"  Cruces cargados — Trámites: {len(ult_tramite)} | Servicios: {len(servicios)} | VS HIS: {len(vs_his)}")
    return ult_tramite, servicios, vs_his


# ──────────────────────────────────────────────
# VALIDACIONES (en orden de prioridad)
# ──────────────────────────────────────────────

def validar_servicios(op: pd.DataFrame, servicios: pd.DataFrame) -> pd.DataFrame:
    """
    Clasifica cuentas según estado de sus servicios:
    - SERVICIO INACTIVO TOTAL: ningún servicio activo
    - PRODUCTO NO SOPORTADO: activos pero fuera de lista soportada
    - SERVICIOS ACTIVOS SOPORTADOS: al menos uno soportado y activo
    """
    op_serv = op.merge(servicios, how="left", on="SUB_ID")
    resultados = []

    for sub_id, grupo in op_serv.groupby("SUB_ID"):
        activos = grupo[grupo["ESTADO"] == "A"]

        if activos.empty:
            resultados.append((sub_id, "SERVICIO INACTIVO TOTAL", "Ningún servicio activo"))
            continue

        lista_activos = activos["SERVICIO"].dropna().unique().tolist()
        activos_soportados = [s for s in lista_activos if s in SERVICIOS_SOPORTADOS]

        if not activos_soportados:
            resultados.append((sub_id, "PRODUCTO NO SOPORTADO", "Servicios activos no soportados"))
            continue

        resultados.append((sub_id, "SERVICIOS ACTIVOS SOPORTADOS", "Activos soportados: " + ", ".join(sorted(set(activos_soportados)))))

    df_result = pd.DataFrame(resultados, columns=["SUB_ID", "TIPOLOGIA", "DETALLE"])
    op = op.drop(columns=["TIPOLOGIA", "DETALLE"])
    op = op.merge(df_result, how="left", on="SUB_ID")
    return op


def validar_tramite(op: pd.DataFrame) -> pd.DataFrame:
    """Marca cuentas cuyo último trámite fue una reconexión (código 10197)."""
    mask_rx = op["TRAMITE_ULTIMO"] == "10197"
    op.loc[mask_rx, "TIPOLOGIA"] = "ULTIMO TRAMITE RX"
    op.loc[mask_rx, "DETALLE"] = "Código 10197: Reconexión detectada"
    return op


def validar_external(op: pd.DataFrame, vs_his: pd.DataFrame) -> pd.DataFrame:
    """
    Sobre cuentas con servicios activos soportados, verifica si el external
    está sincronizado correctamente (sin FECHA_FIN_SUSPENSION activa).
    """
    op_validar = op[op["TIPOLOGIA"] == "SERVICIOS ACTIVOS SOPORTADOS"]
    merge_ext = op_validar.merge(vs_his, how="left", on=["SUB_ID", "EXT_SRVC_ID"])

    sin_fecha_fin = merge_ext["FECHA_FIN_SUSPENSION"].astype(str).str.strip() == ""
    sub_ids_sync = merge_ext.loc[sin_fecha_fin, "SUB_ID"].unique()

    op.loc[op["SUB_ID"].isin(sub_ids_sync), ["TIPOLOGIA", "DETALLE"]] = [
        "EXTERNAL SINCRONIZADO CORRECTAMENTE",
        "EXT_SRVC_ID activo sin FECHA_FIN_SUSPENSION",
    ]
    return op


# ──────────────────────────────────────────────
# EXPORTAR
# ──────────────────────────────────────────────

def exportar(op: pd.DataFrame, ult_tramite: pd.DataFrame, servicios: pd.DataFrame, path: str):
    with pd.ExcelWriter(path) as writer:
        op.to_excel(writer, sheet_name="OP_RESULTADO", index=False)
        ult_tramite.to_excel(writer, sheet_name="ORIGINAL_ULTIMO_TRAMITE", index=False)
        servicios.to_excel(writer, sheet_name="ORIGINAL_SERVICIOS", index=False)
    print(f"  Archivo generado: {path}")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    print("\n Iniciando prevalidación de OP...\n")

    print(" Cargando archivos...")
    op = cargar_op(ARCHIVO_OP)
    ult_tramite, servicios, vs_his = cargar_cruzes(ARCHIVO_CRUZES)

    print("\n Combinando OP con trámites...")
    op = op.merge(ult_tramite[["SUB_ID", "TRAMITE_ULTIMO"]], how="left", on="SUB_ID")

    print("\n Ejecutando validaciones...")
    op = validar_servicios(op, servicios)
    op = validar_tramite(op)
    op = validar_external(op, vs_his)

    print("\n Resumen de tipologías:")
    print(op["TIPOLOGIA"].value_counts().to_string())

    print("\n Exportando resultados...")
    exportar(op, ult_tramite, servicios, ARCHIVO_SALIDA)

    print("\n Proceso completado exitosamente.\n")
