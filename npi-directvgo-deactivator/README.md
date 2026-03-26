# 📡 NPI DirecTVGO Mass Deactivator

Automatización de la **desactivación masiva de servicios OTT y auxiliares** en cuentas fallidas durante la fase NPI del proceso de suspensión.

---

## 🧩 Problema que resuelve

En la fase NPI, muchas cuentas fallan porque sus servicios auxiliares (DirecTVGO, OTTs) no se desactivan automáticamente. El proceso manual requería entrar al portal del cliente y desactivarlos **uno por uno**.

Esta automatización conecta directamente con la **API REST de DirecTVGO** y ejecuta la desactivación de forma masiva para todas las cuentas del archivo.

---

## 🔄 Flujo del proceso

```
Excel (cuentas)
  ├── documento
  └── tipo de documento (CC / NIT)
         │
         ▼
  Generar subscriber_id
  (prefijo + documento invertido)
         │
         ▼
  PATCH /v1/subscriber/CO/{id}/deactivate
         │
         ▼
  Excel de resultados con estado por cuenta
```

## 🔑 Lógica de generación de subscriber_id

| Tipo doc | Fórmula |
|---|---|
| CC | `101` + documento invertido |
| NIT | `104` + documento invertido |

---

## 🚀 Uso

```bash
pip install pandas requests openpyxl
python npi_deactivator.py
```

**Archivo requerido:** `cuentas.xlsx` con columnas `documento` y `tipo de documento`

**Salida:** `resultado_inactivacion.xlsx` con columnas de resultado y detalle de respuesta API por cuenta.

---

## 📊 Códigos de respuesta API

| HTTP | Significado |
|---|---|
| `200` | Inactivado correctamente |
| `404` | Cuenta no existe en el sistema |
| Otro | Error — se registra el código para revisión |

---

## ⚠️ Nota

El token de autorización debe reemplazarse por una variable de entorno en producción:
```python
TOKEN = os.environ.get("DTV_API_TOKEN")
```

---

## 🛠️ Tecnologías

`Python` · `requests` · `pandas` · `openpyxl`
