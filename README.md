
# Predicción de Radiación Solar para Energía Fotovoltaica

[![CI](https://github.com/fonsiga03-droid/proyecto-meteorologia/actions/workflows/ci.yml/badge.svg)](https://github.com/fonsiga03-droid/proyecto-meteorologia/actions/workflows/ci.yml)

[![Docs](https://github.com/fonsiga03-droid/proyecto-meteorologia/actions/workflows/docs.yml/badge.svg)](https://github.com/fonsiga03-droid/proyecto-meteorologia/actions/workflows/docs.yml)

[![Release](https://img.shields.io/github/v/release/fonsiga03-droid/proyecto-meteorologia)](https://github.com/fonsiga03-droid/proyecto-meteorologia/releases)

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)

[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

## Descripción

Proyecto de análisis de datos de radiación solar (global, directa y difusa) para evaluar el

potencial fotovoltaico en diferentes localizaciones españolas. Trabajamos con datos satelitales

de NASA POWER y ERA5, modelizamos la producción energética de paneles solares, y exploramos

la relación entre nubosidad, estacionalidad y producción.

**Línea 8** del proyecto final de Big Data — Grado en Matemáticas, UNIE Universidad 2025–2026.

## Documentación

📖 [Ver documentación completa](https://fonsiga03-droid.github.io/proyecto-meteorologia/)

## Instalación

```bash

git clone https://github.com/fonsiga03-droid/proyecto-meteorologia.git

cd proyecto-meteorologia

uv sync --group dev

```

## Descarga de datos

Los datos no están incluidos en el repositorio. Para descargarlos:

```bash

python scripts/download_nasa_power.py

```

## Uso

```bash

# Ejecutar tests

uv run pytest tests/ --cov=src -v

# Servir documentación localmente

uv run mkdocs serve

# Lint y formato

uv run ruff check src/ tests/

uv run ruff format src/ tests/

# Lanzar dashboard Streamlit

uv run streamlit run app.py

```

## Estructura del proyecto

proyecto-meteorologia/ ├── .github/workflows/ # CI/CD: tests, docs, releases ├── data/ # Datos (no incluidos en git) ├── docs/ # Fuentes de documentación MkDocs ├── notebooks/ # Scripts de análisis ├── scripts/ # Scripts de descarga de datos ├── src/weather/ # Código fuente del paquete │ ├── init.py │ └── utils.py # Funciones POA, producción FV, conversiones ├── tests/ # Tests unitarios (cobertura 100%) ├── app.py # Dashboard Streamlit ├── mkdocs.yml # Configuración documentación ├── pyproject.toml # Dependencias y configuración └── README.md

## Resultados principales

| Ciudad | GHI media (W/m²) | Producción anual (kWh) |

|--------|-----------------|----------------------|

| Málaga | 210 | 451 |

| Sevilla | 212 | 447 |

| Almería | 206 | 446 |

| Madrid | 197 | 433 |

| Valencia | 196 | 427 |

| Zaragoza | 194 | 425 |

| Barcelona | 185 | 412 |

| Bilbao | 155 | 358 |

> El sur de España genera un **26% más energía** que el norte con el mismo panel solar.

## Autor

**Alfonso González Avanzini** — Grado en Matemáticas, UNIE Universidad

