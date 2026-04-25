import math


def celsius_to_fahrenheit(temp_c: float) -> float:
    """Convert temperature from Celsius to Fahrenheit.

    Args:
        temp_c: Temperature in degrees Celsius.

    Returns:
        Temperature in degrees Fahrenheit.
    """
    return (temp_c * 9 / 5) + 32


def calculate_poa_irradiance(
    ghi: float,
    dni: float,
    dhi: float,
    solar_zenith: float,
    tilt: float = 30.0,
    azimuth: float = 180.0,
) -> float:
    """Calculate Plane of Array (POA) irradiance for a tilted PV panel.

    Uses the simple isotropic sky model.

    Args:
        ghi: Global Horizontal Irradiance (W/m²).
        dni: Direct Normal Irradiance (W/m²).
        dhi: Diffuse Horizontal Irradiance (W/m²).
        solar_zenith: Solar zenith angle in degrees.
        tilt: Panel tilt angle from horizontal in degrees (default 30°).
        azimuth: Panel azimuth angle in degrees — 180 = south (default).

    Returns:
        POA irradiance in W/m².
    """
    zenith_rad = math.radians(solar_zenith)
    tilt_rad = math.radians(tilt)

    # Beam component
    cos_aoi = math.cos(zenith_rad) * math.cos(tilt_rad) + math.sin(
        zenith_rad
    ) * math.sin(tilt_rad)
    cos_aoi = max(0.0, cos_aoi)
    beam = dni * cos_aoi

    # Diffuse component (isotropic sky model)
    diffuse = dhi * (1 + math.cos(tilt_rad)) / 2

    # Ground-reflected component (albedo = 0.2)
    ground = ghi * 0.2 * (1 - math.cos(tilt_rad)) / 2

    return beam + diffuse + ground


def pv_power_output(
    poa: float,
    temp_air: float,
    panel_efficiency: float = 0.20,
    panel_area: float = 1.7,
    temp_coefficient: float = -0.004,
    noct: float = 45.0,
) -> float:
    """Estimate PV panel power output accounting for temperature losses.

    Args:
        poa: Plane of Array irradiance in W/m².
        temp_air: Ambient air temperature in degrees Celsius.
        panel_efficiency: Panel efficiency at STC (default 0.20 = 20%).
        panel_area: Panel area in m² (default 1.7 m²).
        temp_coefficient: Power temperature coefficient per °C (default -0.004).
        noct: Nominal Operating Cell Temperature in °C (default 45°C).

    Returns:
        Estimated power output in Watts.
    """
    if poa <= 0:
        return 0.0

    # Cell temperature using NOCT model
    temp_cell = temp_air + (noct - 20) * (poa / 800)

    # Temperature correction factor
    temp_factor = 1 + temp_coefficient * (temp_cell - 25)

    return poa * panel_efficiency * panel_area * temp_factor