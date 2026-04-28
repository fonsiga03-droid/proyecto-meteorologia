"""
Análisis de radiación solar y potencial fotovoltaico en España.
Script ejecutable equivalente al notebook de análisis.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

from weather.utils import calculate_poa_irradiance, pv_power_output

# ── 0. Configuración ──────────────────────────────────────────────────────────
DATA_DIR = Path("data")
FIG_DIR = Path("docs") / "figures"
FIG_DIR.mkdir(exist_ok=True)

plt.rcParams.update({"figure.dpi": 130, "figure.figsize": (10, 5)})

COLORS = {
    "Sevilla": "#e63946",
    "Madrid": "#457b9d",
    "Barcelona": "#2a9d8f",
    "Valencia": "#f4a261",
    "Bilbao": "#264653",
    "Almeria": "#e9c46a",
    "Zaragoza": "#a8dadc",
    "Malaga": "#e76f51",
}

# ── 1. Carga de datos ─────────────────────────────────────────────────────────
print("Cargando datos...")
df = pd.read_parquet(DATA_DIR / "solar_spain_all.parquet")
df = df.dropna(subset=["GHI"])
df["month"] = df.index.month
df["hour"] = df.index.hour
df["year"] = df.index.year
print(f"  {len(df):,} registros cargados")

# ── 2. Cálculo POA y producción FV ────────────────────────────────────────────
print("Calculando POA e irradiancia...")
solar_zenith = 90 - 45 * np.sin(np.pi * df["hour"] / 12)
solar_zenith = solar_zenith.clip(0, 89)

df["POA"] = [
    calculate_poa_irradiance(
        ghi=row["GHI"],
        dni=max(0, row["GHI"] - row["DHI"]),
        dhi=row["DHI"],
        solar_zenith=sz,
        tilt=30,
        azimuth=180,
    )
    for (_, row), sz in zip(df.iterrows(), solar_zenith)
]

df["P_watts"] = df.apply(
    lambda r: pv_power_output(poa=r["POA"], temp_air=r["T2M"]), axis=1
)
df["P_kwh"] = df["P_watts"] / 1000

# ── 3. GHI medio mensual por ciudad ───────────────────────────────────────────
print("Generando figura 1: GHI mensual...")
monthly = df.groupby(["location", "month"])["GHI"].mean().reset_index()

fig, ax = plt.subplots()
for city, grp in monthly.groupby("location"):
    ax.plot(grp["month"], grp["GHI"], marker="o", label=city, color=COLORS[city])

ax.set_title("Radiación Global Horizontal media mensual (NASA POWER 2022–2023)")
ax.set_xlabel("Mes")
ax.set_ylabel("GHI (W/m²)")
ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Ene","Feb","Mar","Abr","May","Jun","Jul","Ago","Sep","Oct","Nov","Dic"])
ax.legend(fontsize=8)
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "ghi_mensual.png")
plt.close()
print("  Guardada: ghi_mensual.png")

# ── 4. Perfil intradiario por estación ────────────────────────────────────────
print("Generando figura 2: perfil intradiario...")
estaciones = {
    "Invierno (Dic-Feb)": [12, 1, 2],
    "Primavera (Mar-May)": [3, 4, 5],
    "Verano (Jun-Ago)": [6, 7, 8],
    "Otoño (Sep-Nov)": [9, 10, 11],
}
sevilla = df[df["location"] == "Sevilla"]

fig, axes = plt.subplots(2, 2, figsize=(12, 7), sharey=True)
for ax, (season, months) in zip(axes.flat, estaciones.items()):
    subset = sevilla[sevilla["month"].isin(months)]
    hourly = subset.groupby("hour")["GHI"].mean()
    ax.fill_between(hourly.index, hourly.values, alpha=0.6, color="#e63946")
    ax.plot(hourly.index, hourly.values, color="#e63946")
    ax.set_title(season)
    ax.set_xlabel("Hora UTC")
    ax.set_ylabel("GHI (W/m²)")
    ax.set_xticks(range(0, 24, 3))
    ax.grid(alpha=0.3)

fig.suptitle("Perfil intradiario de radiación solar — Sevilla", fontsize=13)
fig.tight_layout()
fig.savefig(FIG_DIR / "perfil_intradiario.png")
plt.close()
print("  Guardada: perfil_intradiario.png")

# ── 5. Producción FV anual por ciudad ─────────────────────────────────────────
print("Generando figura 3: producción fotovoltaica anual...")
anual = df.groupby("location")["P_kwh"].sum().sort_values(ascending=False) / 2

fig, ax = plt.subplots(figsize=(9, 5))
bars = ax.bar(anual.index, anual.values,
              color=[COLORS[c] for c in anual.index], edgecolor="white")
ax.bar_label(bars, fmt="%.0f kWh", padding=3, fontsize=9)
ax.set_title("Producción fotovoltaica anual estimada por ciudad\n(panel 340W, inclinación 30°, orientación sur)")
ax.set_ylabel("Energía anual (kWh)")
ax.set_ylim(0, anual.max() * 1.15)
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "produccion_anual.png")
plt.close()
print("  Guardada: produccion_anual.png")

# ── 6. Variabilidad interanual ────────────────────────────────────────────────
print("Generando figura 4: variabilidad interanual...")
interanual = df.groupby(["location", "year"])["GHI"].sum().reset_index()

fig, ax = plt.subplots(figsize=(9, 5))
x = np.arange(len(df["location"].unique()))
cities = sorted(df["location"].unique())
width = 0.35

for i, year in enumerate([2022, 2023]):
    vals = [interanual[(interanual["location"] == c) & (interanual["year"] == year)]["GHI"].values[0]
            for c in cities]
    ax.bar(x + i * width, vals, width, label=str(year),
           color=["#457b9d", "#e63946"][i], alpha=0.85)

ax.set_xticks(x + width / 2)
ax.set_xticklabels(cities, rotation=15)
ax.set_ylabel("GHI acumulada anual (W/m²·h)")
ax.set_title("Variabilidad interanual de la radiación solar (2022 vs 2023)")
ax.legend()
ax.grid(axis="y", alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "variabilidad_interanual.png")
plt.close()
print("  Guardada: variabilidad_interanual.png")

# ── 7. Mapa de recurso solar ──────────────────────────────────────────────────
print("Generando figura 5: mapa de recurso solar...")
resumen = df.groupby("location").agg(
    GHI_mean=("GHI", "mean"),
    lat=("lat", "first"),
    lon=("lon", "first"),
    P_anual=("P_kwh", lambda x: x.sum() / 2),
).reset_index()

fig, ax = plt.subplots(figsize=(8, 7))
sc = ax.scatter(resumen["lon"], resumen["lat"],
                c=resumen["GHI_mean"], cmap="YlOrRd",
                s=resumen["P_anual"] / 2, edgecolors="black", linewidths=0.5,
                vmin=140, vmax=220)

for _, row in resumen.iterrows():
    ax.annotate(f"{row['location']}\n{row['GHI_mean']:.0f} W/m²",
                (row["lon"], row["lat"]),
                textcoords="offset points", xytext=(8, 4), fontsize=8)

plt.colorbar(sc, ax=ax, label="GHI media (W/m²)")
ax.set_xlabel("Longitud")
ax.set_ylabel("Latitud")
ax.set_title("Mapa de recurso solar en España\n(tamaño = producción FV anual)")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(FIG_DIR / "mapa_recurso_solar.png")
plt.close()
print("  Guardada: mapa_recurso_solar.png")

# ── 8. Resumen estadístico ────────────────────────────────────────────────────
print("\n=== RESUMEN FOTOVOLTAICO ===")
print(resumen[["location", "GHI_mean", "P_anual"]].sort_values("P_anual", ascending=False).to_string(index=False))
print("\nAnálisis completado. Figuras en docs/figures/")
