"""Dashboard de presentación — Radiación Solar y Energía Fotovoltaica en España."""

from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from weather.utils import calculate_poa_irradiance, pv_power_output

# ── Configuración de página ───────────────────────────────────────────────────
st.set_page_config(
    page_title="Solar FV España",
    page_icon="☀️",
    layout="wide",
)


# ── Carga de datos ────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_parquet(Path("data") / "solar_spain_all.parquet")
    df = df.dropna(subset=["GHI"])
    df["month"] = df.index.month
    df["hour"] = df.index.hour
    df["year"] = df.index.year
    solar_zenith = (90 - 45 * np.sin(np.pi * df["hour"] / 12)).clip(0, 89)
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
    df["P_kwh"] = (
        df.apply(lambda r: pv_power_output(poa=r["POA"], temp_air=r["T2M"]), axis=1)
        / 1000
    )
    return df


MONTH_NAMES = [
    "Ene",
    "Feb",
    "Mar",
    "Abr",
    "May",
    "Jun",
    "Jul",
    "Ago",
    "Sep",
    "Oct",
    "Nov",
    "Dic",
]
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

with st.spinner("Cargando datos NASA POWER..."):
    df = load_data()

# ── Header ────────────────────────────────────────────────────────────────────
st.title("☀️ Radiación Solar y Energía Fotovoltaica en España")
st.markdown(
    "**Proyecto Final Big Data** · Línea 8 · NASA POWER 2022–2023 · 8 ciudades · 140,160 registros"
)

# ── KPIs ──────────────────────────────────────────────────────────────────────
resumen = (
    df.groupby("location")
    .agg(
        GHI_mean=("GHI", "mean"),
        P_anual=("P_kwh", lambda x: x.sum() / 2),
        lat=("lat", "first"),
        lon=("lon", "first"),
    )
    .reset_index()
    .sort_values("P_anual", ascending=False)
)

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    "🏆 Ciudad más solar",
    resumen.iloc[0]["location"],
    f"{resumen.iloc[0]['GHI_mean']:.0f} W/m² media",
)
col2.metric(
    "⚡ Producción máxima",
    f"{resumen.iloc[0]['P_anual']:.0f} kWh/año",
    "por panel de 340W",
)
col3.metric(
    "📉 Ciudad menos solar",
    resumen.iloc[-1]["location"],
    f"{resumen.iloc[-1]['GHI_mean']:.0f} W/m² media",
)
col4.metric(
    "📊 Diferencia Norte-Sur",
    f"{((resumen.iloc[0]['P_anual'] / resumen.iloc[-1]['P_anual']) - 1) * 100:.0f}%",
    "más energía en el sur",
)

st.divider()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    [
        "🗺️ Mapa de recurso solar",
        "📈 Radiación mensual",
        "🔍 Análisis por ciudad",
        "⚡ Producción fotovoltaica",
    ]
)

# ── Tab 1: Mapa ───────────────────────────────────────────────────────────────
with tab1:
    st.subheader("Potencial fotovoltaico por localización")
    fig = px.scatter_geo(
        resumen,
        lat="lat",
        lon="lon",
        size="P_anual",
        color="GHI_mean",
        hover_name="location",
        hover_data={"GHI_mean": ":.1f", "P_anual": ":.0f", "lat": False, "lon": False},
        labels={"GHI_mean": "GHI media (W/m²)", "P_anual": "Producción anual (kWh)"},
        color_continuous_scale="YlOrRd",
        size_max=40,
        scope="europe",
        center={"lat": 40, "lon": -3},
    )
    fig.update_geos(
        lataxis_range=[35, 45],
        lonaxis_range=[-10, 5],
        showcoastlines=True,
        coastlinecolor="gray",
        showland=True,
        landcolor="#f5f5f5",
        showocean=True,
        oceancolor="#e8f4fd",
    )
    fig.update_layout(height=500, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    st.plotly_chart(fig, use_container_width=True)

# ── Tab 2: GHI mensual ────────────────────────────────────────────────────────
with tab2:
    st.subheader("Radiación Global Horizontal media mensual")
    monthly = df.groupby(["location", "month"])["GHI"].mean().reset_index()
    monthly["mes"] = monthly["month"].apply(lambda x: MONTH_NAMES[x - 1])

    fig = go.Figure()
    for city in sorted(df["location"].unique()):
        grp = monthly[monthly["location"] == city]
        fig.add_trace(
            go.Scatter(
                x=grp["mes"],
                y=grp["GHI"],
                mode="lines+markers",
                name=city,
                line=dict(color=COLORS[city], width=2),
                marker=dict(size=6),
            )
        )
    fig.update_layout(
        xaxis_title="Mes",
        yaxis_title="GHI (W/m²)",
        height=420,
        hovermode="x unified",
        legend=dict(orientation="h", yanchor="bottom", y=1.02),
    )
    st.plotly_chart(fig, use_container_width=True)
    st.caption(
        "Fuente: NASA POWER · Datos horarios 2022–2023 · Resolución espacial 0.5°"
    )

# ── Tab 3: Análisis interactivo por ciudad ────────────────────────────────────
with tab3:
    st.subheader("Explorador interactivo por ciudad")

    col_a, col_b, col_c = st.columns(3)
    ciudad = col_a.selectbox("Ciudad", sorted(df["location"].unique()))
    variable = col_b.selectbox(
        "Variable",
        {
            "GHI": "Radiación Global Horizontal (W/m²)",
            "DHI": "Radiación Difusa Horizontal (W/m²)",
            "T2M": "Temperatura a 2m (°C)",
            "POA": "Irradiancia en plano del panel (W/m²)",
            "P_kwh": "Producción fotovoltaica (kWh)",
        },
    )
    año = col_c.selectbox("Año", [2022, 2023, "Ambos"])

    ciudad_df = df[df["location"] == ciudad].copy()
    if año != "Ambos":
        ciudad_df = ciudad_df[ciudad_df["year"] == año]

    subtab1, subtab2 = st.tabs(["Por mes", "Perfil intradiario"])

    with subtab1:
        monthly_city = ciudad_df.groupby("month")[variable].mean().reset_index()
        monthly_city["mes"] = monthly_city["month"].apply(lambda x: MONTH_NAMES[x - 1])
        fig = px.bar(
            monthly_city, x="mes", y=variable, color_discrete_sequence=[COLORS[ciudad]]
        )
        fig.update_layout(
            height=350, xaxis_title="Mes", yaxis_title=variable, showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)

    with subtab2:
        hourly_city = (
            ciudad_df.groupby(["hour", "month"])[variable].mean().reset_index()
        )
        hourly_pivot = hourly_city.pivot(index="hour", columns="month", values=variable)
        hourly_pivot.columns = [MONTH_NAMES[c - 1] for c in hourly_pivot.columns]

        fig = go.Figure()
        for mes in ["Ene", "Mar", "Jun", "Sep", "Dic"]:
            if mes in hourly_pivot.columns:
                fig.add_trace(
                    go.Scatter(
                        x=hourly_pivot.index,
                        y=hourly_pivot[mes],
                        mode="lines",
                        name=mes,
                        fill="tozeroy",
                        opacity=0.6,
                    )
                )
        fig.update_layout(
            height=350,
            xaxis_title="Hora UTC",
            yaxis_title=variable,
            hovermode="x unified",
        )
        st.plotly_chart(fig, use_container_width=True)

# ── Tab 4: Producción FV ──────────────────────────────────────────────────────
with tab4:
    st.subheader("Estimador de producción fotovoltaica")

    col_p1, col_p2, col_p3 = st.columns(3)
    tilt = col_p1.slider("Inclinación del panel (°)", 0, 90, 30)
    n_panels = col_p2.number_input("Número de paneles", 1, 100, 10)
    precio_kwh = col_p3.number_input("Precio electricidad (€/kWh)", 0.05, 0.50, 0.18)

    prod_anual = resumen.copy()
    prod_anual["P_total_kwh"] = prod_anual["P_anual"] * n_panels
    prod_anual["Ahorro_anual_€"] = prod_anual["P_total_kwh"] * precio_kwh

    fig = px.bar(
        prod_anual.sort_values("P_total_kwh", ascending=False),
        x="location",
        y="P_total_kwh",
        color="GHI_mean",
        color_continuous_scale="YlOrRd",
        text="P_total_kwh",
        labels={"P_total_kwh": "Producción anual (kWh)", "location": "Ciudad"},
    )
    fig.update_traces(texttemplate="%{text:.0f} kWh", textposition="outside")
    fig.update_layout(height=380, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("### 💰 Ahorro económico estimado")
    cols = st.columns(len(prod_anual))
    for col, (_, row) in zip(
        cols, prod_anual.sort_values("Ahorro_anual_€", ascending=False).iterrows()
    ):
        col.metric(
            row["location"],
            f"{row['Ahorro_anual_€']:.0f} €/año",
            f"{row['P_total_kwh']:.0f} kWh",
        )

st.divider()
st.caption(
    "Datos: NASA POWER API · Modelo: POA isotrópico, NOCT térmico · Panel: 340W, η=20%, 1.7m² · Proyecto Final Big Data 2025–2026"
)
