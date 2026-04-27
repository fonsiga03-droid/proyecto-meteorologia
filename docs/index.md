# Predicción de Radiación Solar para Energía Fotovoltaica

## Descripción

Proyecto de análisis de datos de radiación solar (global, directa y difusa)
para evaluar el potencial fotovoltaico en diferentes localizaciones españolas.

## Fuentes de datos

- **NASA POWER** — datos satelitales de radiación solar desde 1981
- **ERA5 (Copernicus)** — reanálisis climático global horario

## Objetivos

- Descargar datos de radiación solar para múltiples localizaciones españolas
- Calcular la irradiancia en el plano del panel (POA)
- Modelizar la producción fotovoltaica considerando temperatura y pérdidas
- Analizar variabilidad interanual e intradiaria
- Comparar el potencial fotovoltaico entre regiones

## Instalación

```bash
git clone https://github.com/YOUR_USERNAME/proyecto-meteorologia.git
cd proyecto-meteorologia
uv sync --group dev
```

## Autor

fonsi — Grado en Matemáticas, UNIE Universidad, 2025–2026
