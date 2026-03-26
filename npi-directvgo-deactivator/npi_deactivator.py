"""
NPI DirecTVGO Mass Deactivator
-------------------------------
Automatización para desactivación masiva de servicios OTT/auxiliares
en cuentas fallidas durante la fase NPI del proceso de suspensión.

Conecta directamente con la API de DirecTVGO para evitar gestión manual
cuenta por cuenta desde el portal.

Autor: Citlalli Jersey Sanchez Montero
"""

import pandas as pd
import requests

# ──────────────────────────────────────────────
# CONFIGURACIÓN
# ──────────────────────────────────────────────

BASE_URL = "http://dtv-prov.tbxapis.com/v1/subscriber/CO"
TOKEN = "Q1kAKAPJezx6lhvJVT0omIAXhRfGgWwn"

ARCHIVO_ENTRADA = "cuentas.xlsx"
ARCHIVO_SALIDA = "resultado_inactivacion.xlsx"

HEADERS = {
    "Authorization": TOKEN
}


# ──────────────────────────────────────────────
# LÓGICA DE NEGOCIO
# ──────────────────────────────────────────────

def generar_subscriber_id(tipo_doc: str, documento: str) -> str | None:
    """
    Genera el subscriber_id requerido por la API de DirecTVGO.

    Lógica:
    - CC  → prefijo 101 + documento invertido
    - NIT → prefijo 104 + documento invertido
    """
    documento_invertido = str(documento)[::-1]

    tipo = str(tipo_doc).strip().lower()
    if tipo == "cc":
        return "101" + documento_invertido
    elif tipo == "nit":
        return "104" + documento_invertido
    else:
        return None


# ──────────────────────────────────────────────
# PROCESAMIENTO
# ──────────────────────────────────────────────

def procesar_cuenta(row: pd.Series) -> dict:
    """Procesa una cuenta: genera el ID, llama a la API y retorna el resultado."""
    documento = str(row["documento"])
    tipo_doc = row["tipo de documento"]

    subscriber_id = generar_subscriber_id(tipo_doc, documento)

    if subscriber_id is None:
        return {
            "subscriber_id": None,
            "resultado": "Tipo doc inválido",
            "detalle": f"Tipo de documento no reconocido: {tipo_doc}",
        }

    url = f"{BASE_URL}/{subscriber_id}/deactivate"

    try:
        response = requests.patch(url, headers=HEADERS, timeout=10)

        if response.status_code == 200:
            estado = "Inactivado ✓"
        elif response.status_code == 404:
            estado = "No existe en sistema"
        else:
            estado = f"Error HTTP {response.status_code}"

        return {
            "subscriber_id": subscriber_id,
            "resultado": estado,
            "detalle": response.text,
        }

    except requests.exceptions.Timeout:
        return {"subscriber_id": subscriber_id, "resultado": "Error conexión", "detalle": "Timeout"}
    except Exception as e:
        return {"subscriber_id": subscriber_id, "resultado": "Error conexión", "detalle": str(e)}


def ejecutar(archivo_entrada: str, archivo_salida: str):
    print("\n🔄 Iniciando desactivación masiva NPI DirecTVGO...\n")

    df = pd.read_excel(archivo_entrada)
    df.columns = df.columns.str.strip().str.lower()

    print(f"📂 Cuentas a procesar: {len(df)}\n")

    resultados = df.apply(procesar_cuenta, axis=1, result_type="expand")
    df = pd.concat([df, resultados], axis=1)

    df.to_excel(archivo_salida, index=False)

    print("📊 Resumen:")
    print(df["resultado"].value_counts().to_string())
    print(f"\n💾 Resultado guardado en: {archivo_salida}")
    print("\n✅ Proceso completado.\n")


# ──────────────────────────────────────────────
# MAIN
# ──────────────────────────────────────────────

if __name__ == "__main__":
    ejecutar(ARCHIVO_ENTRADA, ARCHIVO_SALIDA)
