import pytest

from weather.utils import (
    calculate_poa_irradiance,
    celsius_to_fahrenheit,
    pv_power_output,
)


class TestCelsiusToFahrenheit:
    def test_freezing_point(self):
        assert celsius_to_fahrenheit(0) == 32.0

    def test_boiling_point(self):
        assert celsius_to_fahrenheit(100) == 212.0

    def test_negative_forty_equal_in_both_scales(self):
        assert celsius_to_fahrenheit(-40) == -40.0

    def test_body_temperature(self):
        assert celsius_to_fahrenheit(37) == pytest.approx(98.6, rel=1e-3)


class TestCalculatePoaIrradiance:
    def test_zero_irradiance_returns_zero(self):
        result = calculate_poa_irradiance(0, 0, 0, 45)
        assert result == 0.0

    def test_returns_float(self):
        result = calculate_poa_irradiance(800, 600, 200, 30)
        assert isinstance(result, float)

    def test_high_zenith_reduces_beam(self):
        """Near sunset (high zenith) beam component should be small."""
        result_noon = calculate_poa_irradiance(800, 600, 200, 10)
        result_sunset = calculate_poa_irradiance(800, 600, 200, 85)
        assert result_noon > result_sunset

    def test_south_facing_panel_default(self):
        """Default azimuth should be 180 degrees (south)."""
        result = calculate_poa_irradiance(800, 600, 200, 30, tilt=30, azimuth=180)
        assert result > 0

    def test_flat_panel_equals_ghi_at_zero_zenith(self):
        """A flat panel (tilt=0) should receive approximately GHI."""
        result = calculate_poa_irradiance(800, 600, 200, 0, tilt=0)
        assert result == pytest.approx(800, rel=0.05)


class TestPvPowerOutput:
    def test_zero_poa_returns_zero(self):
        assert pv_power_output(0, 25) == 0.0

    def test_negative_poa_returns_zero(self):
        assert pv_power_output(-10, 25) == 0.0

    def test_returns_float(self):
        result = pv_power_output(900, 25)
        assert isinstance(result, float)

    def test_higher_temperature_reduces_output(self):
        """Higher temperature should reduce power due to negative temp coefficient."""
        power_cold = pv_power_output(900, 10)
        power_hot = pv_power_output(900, 40)
        assert power_cold > power_hot

    def test_standard_conditions(self):
        """At STC (1000 W/m², 25°C) output should be close to nameplate power."""
        # 1000 W/m² × 20% efficiency × 1.7 m² = 340 W (approx, with temp correction)
        result = pv_power_output(1000, 25)
        assert 280 < result < 380
