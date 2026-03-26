# 🛠️ SX Automation Portfolio

Colección de automatizaciones desarrolladas para optimizar el proceso de **suspensión de servicios de telecomunicaciones** (ciclo SX), reduciendo trabajo manual y tiempos operativos en entornos reales.

---

## 📁 Proyectos

| Proyecto | Descripción | Tecnologías |
|---|---|---|
| [`op-suspension-validator`](./op-suspension-validator/) | Prevalidación masiva de órdenes de proceso (OP) con clasificación por tipología | `pandas`, `openpyxl` |
| [`npi-directvgo-deactivator`](./npi-directvgo-deactivator/) | Desactivación masiva de servicios OTT via API REST en fase NPI | `requests`, `pandas` |
| [`ans-sla-calculator`](./ans-sla-calculator/) | Cálculo automático de cumplimiento de ANS ajustando horarios hábiles y festivos colombianos | `pandas`, `numpy`, `holidays` |

---

## 🌐 Contexto de negocio

El **proceso de suspensión (SX)** en empresas de telecomunicaciones involucra múltiples fases de validación antes de que una cuenta pueda ser suspendida correctamente. Cada fase requiere cruzar datos de diferentes sistemas (MongoDB, PL/SQL, APIs externas) y aplicar reglas de negocio específicas.

Estas automatizaciones reemplazan tareas que antes se hacían manualmente — una cuenta a la vez — con procesos que manejan miles de registros en segundos.

---

## 🧰 Stack general

- **Python 3.10+**
- `pandas` — manipulación y cruce de datos
- `requests` — integración con APIs REST
- `openpyxl` — lectura/escritura de Excel
- `numpy` — operaciones vectorizadas
- `holidays` — festivos colombianos

---

## 👩‍💻 Sobre la autora

**Citlalli Jersey Sanchez Montero**
Ingeniera de Sistemas | Soporte Técnico & Automatización | Bogotá, Colombia

[![LinkedIn](https://img.shields.io/badge/LinkedIn-Citlalli_Sanchez-0077B5?style=flat&logo=linkedin)](https://linkedin.com/in/citlalli-jersey-sanchez-montero-a656b5190)

---

> 💡 *Todos los scripts fueron desarrollados a partir de necesidades operativas reales. Los datos sensibles (tokens, URLs de producción) deben reemplazarse por variables de entorno antes de usar en otro entorno.*
