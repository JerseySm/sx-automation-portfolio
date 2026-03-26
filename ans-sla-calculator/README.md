# ⏱️ ANS / SLA Calculator

Automatización del **reporte mensual de cumplimiento de ANS** para el proceso de suspensión. Ajusta automáticamente fechas según horario hábil y festivos colombianos, eliminando el filtrado manual día a día.

---

## 🧩 Problema que resuelve

El reporte mensual requería revisar manualmente cada caso para:
- Excluir fines de semana y festivos
- Ajustar casos que llegaron fuera del horario (antes de 8 AM / después de 5 PM)
- Calcular si el tiempo de atención cumplía el ANS de 8 horas

Con cientos de registros al mes, esto tomaba horas. Esta automatización lo hace en segundos.

---

## 🔄 Lógica de ajuste de fechas

```
Fecha de inicio recibida
        │
        ├── ¿Es fin de semana o festivo? ──► Siguiente día hábil a las 8:00 AM
        │
        ├── ¿Antes de las 8:00 AM? ──────► Mismo día a las 8:00 AM
        │
        ├── ¿Después de las 5:00 PM? ────► Siguiente día hábil a las 8:00 AM
        │
        └── ¿Dentro del horario? ────────► Se usa tal cual
```

---

## ✅ Campos calculados

| Campo | Descripción |
|---|---|
| `FechaInicio_Ajustada` | Fecha de inicio corregida según horario hábil |
| `Diff_Horas` | Tiempo transcurrido en formato HH:MM:SS |
| `Cumple` | `SI` si ≤ 8 horas hábiles, `NO` si supera el ANS |
| `Dias_Igual` | Si inicio y fin son el mismo día |

---

## 🚀 Uso

```bash
pip install pandas numpy openpyxl holidays
python ans_calculator.py
```

**Archivo requerido:** `archivo.xlsx` con columnas `Dia_ini`, `Mes_ini`, `Hora_ini`, `Dia_Fin`, `Mes_Fin`, `Hora_Fin`

**Salida:** `resultado_final.xlsx` con dos hojas:
- `Original` — datos sin modificar
- `Corregido` — datos con fechas ajustadas y cumplimiento calculado

---

## ⚙️ Configuración

```python
HORARIO_INICIO = time(8, 0, 0)   # 8:00 AM
HORARIO_FIN    = time(17, 0, 0)  # 5:00 PM
ANS_HORAS      = 8               # Límite de cumplimiento
AÑOS_FESTIVOS  = [2025, 2026]    # Festivos Colombia
```

---

## 🛠️ Tecnologías

`Python` · `pandas` · `numpy` · `openpyxl` · `holidays`
