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

git clone https://github.com/fonsiga03-droid/proyecto-meteorologia.git
cd proyecto-meteorologia
uv sync --group dev

## Descarga de datos

Los datos no están incluidos en el repositorio. Para descargarlos:

python scripts/download_nasa_power.py

## Uso

uv run pytest tests/ --cov=src -v
uv run mkdocs serve
uv run ruff check src/ tests/
uv run ruff format src/ tests/

## Estructura del proyecto

proyecto-meteorologia/
├── .github/workflows/   # CI/CD: tests, docs, releases
├── data/                # Datos (no incluidos en git)
├── docs/                # Fuentes de documentación MkDocs
├── notebooks/           # Notebooks exploratorios
├── src/weather/         # Código fuente del paquete
│   ├── __init__.py
│   └── utils.py         # Funciones POA, producción FV, conversiones
├── tests/               # Tests unitarios (cobertura 100%)
├── mkdocs.yml           # Configuración documentación
├── pyproject.toml       # Dependencias y configuración
└── README.md

## Autor

fonsi — Grado en Matemáticas, UNIE Universidad
