# 📋 OP Suspension Validator

Automatización de la **prevalidación masiva de órdenes de proceso (OP)** del ciclo de suspensión. Clasifica miles de cuentas por tipología en segundos, antes de la gestión manual.

---

## 🧩 Problema que resuelve

Mensualmente se reciben archivos OP con **8.000+ cuentas** que deben ser validadas para determinar si pueden suspenderse o por qué se rechazan. Hacerlo manualmente implicaba revisar cada cuenta en múltiples sistemas.

Esta automatización cruza los datos de tres fuentes y clasifica cada cuenta automáticamente.

---

## 🔄 Flujo del proceso

```
CSV (OP)  ─┐
            ├──► Cruce de datos ──► Validaciones en cascada ──► Excel de resultados
XLSX       ─┘
(Cruces)
  ├── ULTIMO TRAMITE
  ├── ESTADO DE LOS SERVICIOS
  └── VS HIS
```

## ✅ Tipologías de clasificación

| Tipología | Descripción |
|---|---|
| `SERVICIO INACTIVO TOTAL` | Ningún servicio activo en la cuenta |
| `PRODUCTO NO SOPORTADO` | Servicios activos pero fuera de lista soportada |
| `ULTIMO TRAMITE RX` | Último trámite fue reconexión (código 10197) |
| `SERVICIOS ACTIVOS SOPORTADOS` | Cuenta con al menos un servicio soportado activo |
| `EXTERNAL SINCRONIZADO CORRECTAMENTE` | EXT_SRVC_ID activo sin fecha fin de suspensión |

---

## 🚀 Uso

```bash
pip install pandas openpyxl
python op_validator.py
```

**Archivos requeridos en la misma carpeta:**
- `revision_suspension_XXXXXXXX(opXXX).csv` — archivo OP del mes
- `CRUZES.xlsx` — archivo de cruces con 3 hojas: `ULTIMO TRAMITE`, `ESTADO DE LOS SERVICIOS`, `VS HIS`

**Salida:** `OP_PREVALIDADO.xlsx` con hoja de resultados + hojas originales de referencia.

---

## 🛠️ Tecnologías

`Python` · `pandas` · `openpyxl`
