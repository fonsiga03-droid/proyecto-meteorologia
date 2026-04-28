"""Download solar radiation data from NASA POWER for Spanish locations."""

import json
import time
from pathlib import Path

import pandas as pd
import requests

LOCATIONS = {
    "Sevilla": {"lat": 37.3891, "lon": -5.9845},
    "Madrid": {"lat": 40.4168, "lon": -3.7038},
    "Barcelona": {"lat": 41.3874, "lon": 2.1686},
    "Valencia": {"lat": 39.4699, "lon": -0.3763},
    "Bilbao": {"lat": 43.2630, "lon": -2.9350},
    "Almeria": {"lat": 36.8340, "lon": -2.4637},
    "Zaragoza": {"lat": 41.6488, "lon": -0.8891},
    "Malaga": {"lat": 36.7213, "lon": -4.4214},
}

PARAMETERS = "ALLSKY_SFC_SW_DWN,CLRSKY_SFC_SW_DWN,ALLSKY_SFC_SW_DIFF,T2M"
START = "20220101"
END = "20231231"
DATA_DIR = Path("data")


def download_location(name: str, lat: float, lon: float) -> pd.DataFrame:
    """Download NASA POWER hourly data for a single location.

    Args:
        name: Location name.
        lat: Latitude in degrees.
        lon: Longitude in degrees.

    Returns:
        DataFrame with hourly solar radiation data.
    """
    url = (
        "https://power.larc.nasa.gov/api/temporal/hourly/point"
        f"?parameters={PARAMETERS}"
        f"&community=RE"
        f"&longitude={lon}&latitude={lat}"
        f"&start={START}&end={END}"
        f"&format=JSON"
    )
    print(f"Descargando {name}...")
    response = requests.get(url, timeout=120)
    response.raise_for_status()
    data = response.json()

    params = data["properties"]["parameter"]
    df = pd.DataFrame(params)
    df.index = pd.to_datetime(df.index, format="%Y%m%d%H")
    df.index.name = "datetime"
    df.columns = ["GHI", "GHI_clear", "DHI", "T2M"]
    df["location"] = name
    df["lat"] = lat
    df["lon"] = lon

    # NASA usa -999 para datos faltantes
    df = df.replace(-999.0, float("nan"))
    return df


def main() -> None:
    """Download data for all Spanish locations and save to parquet."""
    DATA_DIR.mkdir(exist_ok=True)
    all_dfs = []

    for name, coords in LOCATIONS.items():
        cache_file = DATA_DIR / f"{name.lower()}_nasa_power.parquet"
        if cache_file.exists():
            print(f"{name} ya descargado, cargando desde caché...")
            df = pd.read_parquet(cache_file)
        else:
            df = download_location(name, coords["lat"], coords["lon"])
            df.to_parquet(cache_file)
            print(f"  Guardado en {cache_file}")
            time.sleep(2)  # respetar rate limit de la API
        all_dfs.append(df)

    combined = pd.concat(all_dfs)
    combined.to_parquet(DATA_DIR / "solar_spain_all.parquet")
    print(f"\nDatos combinados: {combined.shape[0]:,} filas")
    print(combined.groupby("location")["GHI"].describe().round(2))


if __name__ == "__main__":
    main()
