"""Tests for the pure cycling math engine."""

import math

from app.core.formulas import (
    atl_update,
    best_efforts,
    ctl_update,
    ftp_from_20min_test,
    ftp_from_best_efforts,
    hr_zones,
    intensity_factor,
    normalized_power,
    power_zones,
    rider_type_profile,
    time_in_zones,
    training_stress_score,
    tsb,
    variability_index,
    w_per_kg,
)


class TestNormalizedPower:
    def test_steady_effort_equals_average(self):
        """NP of a perfectly steady effort should equal average power."""
        # 60 seconds at 200W
        samples = [200] * 60
        np = normalized_power(samples)
        assert abs(np - 200.0) < 1.0

    def test_variable_effort_higher_than_average(self):
        """NP of a variable effort should be higher than average power."""
        # 60s blocks of 100W and 300W (avg=200W, but NP should be higher
        # because 30s rolling averages will capture the high/low blocks)
        samples = [100] * 60 + [300] * 60 + [100] * 60 + [300] * 60
        np = normalized_power(samples)
        avg = sum(samples) / len(samples)
        assert np > avg

    def test_insufficient_data_returns_zero(self):
        """Less than 30 seconds of data returns 0."""
        samples = [200] * 20
        assert normalized_power(samples) == 0.0

    def test_empty_data_returns_zero(self):
        assert normalized_power([]) == 0.0

    def test_handles_none_values(self):
        """None values should be filtered out."""
        samples = [200] * 60
        samples[10] = None
        np = normalized_power(samples)
        assert np > 0


class TestIntensityFactor:
    def test_at_ftp(self):
        """IF should be 1.0 when NP equals FTP."""
        assert intensity_factor(250.0, 250) == 1.0

    def test_below_ftp(self):
        assert intensity_factor(200.0, 250) == 0.8

    def test_above_ftp(self):
        assert intensity_factor(275.0, 250) == 1.1

    def test_zero_ftp(self):
        assert intensity_factor(200.0, 0) == 0.0


class TestVariabilityIndex:
    def test_steady_effort(self):
        """VI should be 1.0 for a perfectly steady effort."""
        assert variability_index(200.0, 200.0) == 1.0

    def test_variable_effort(self):
        """VI > 1.0 for variable efforts."""
        assert variability_index(220.0, 200.0) == 1.1

    def test_zero_avg_power(self):
        assert variability_index(200.0, 0.0) == 0.0


class TestTrainingStressScore:
    def test_one_hour_at_ftp(self):
        """1 hour at FTP should be 100 TSS."""
        tss = training_stress_score(3600, 250.0, 1.0, 250)
        assert abs(tss - 100.0) < 0.1

    def test_easy_ride(self):
        """Easy ride should have low TSS."""
        tss = training_stress_score(3600, 175.0, 0.7, 250)
        assert tss < 100

    def test_hard_ride(self):
        """Hard ride above FTP should have high TSS."""
        tss = training_stress_score(3600, 275.0, 1.1, 250)
        assert tss > 100

    def test_zero_duration(self):
        assert training_stress_score(0, 250.0, 1.0, 250) == 0.0

    def test_zero_ftp(self):
        assert training_stress_score(3600, 250.0, 1.0, 0) == 0.0


class TestCTLATLTSB:
    def test_ctl_increases_with_training(self):
        """CTL should increase when TSS > current CTL."""
        new_ctl = ctl_update(50.0, 100.0)
        assert new_ctl > 50.0

    def test_ctl_decreases_on_rest(self):
        """CTL should decrease on rest days (TSS=0)."""
        new_ctl = ctl_update(50.0, 0.0)
        assert new_ctl < 50.0

    def test_atl_responds_faster(self):
        """ATL should change more than CTL for the same TSS input."""
        new_ctl = ctl_update(50.0, 100.0)
        new_atl = atl_update(50.0, 100.0)
        assert (new_atl - 50.0) > (new_ctl - 50.0)

    def test_tsb_calculation(self):
        """TSB = CTL - ATL."""
        assert tsb(70.0, 85.0) == -15.0
        assert tsb(70.0, 50.0) == 20.0

    def test_fresh_athlete(self):
        """Starting from 0, 7 days of 50 TSS should build ATL faster."""
        ctl = 0.0
        atl = 0.0
        for _ in range(7):
            ctl = ctl_update(ctl, 50.0)
            atl = atl_update(atl, 50.0)
        assert atl > ctl  # ATL responds faster


class TestFTPEstimation:
    def test_20min_test(self):
        """FTP from 20-min test = avg * 0.95."""
        assert ftp_from_20min_test(300.0) == 285
        assert ftp_from_20min_test(263.0) == 250

    def test_best_efforts_uses_longest_reliable(self):
        """Should pick the highest reliable estimate."""
        efforts = {
            300: 350,   # 5min: 350 * 0.75 = 262
            1200: 280,  # 20min: 280 * 0.95 = 266
            3600: 260,  # 60min: direct = 260
        }
        ftp = ftp_from_best_efforts(efforts)
        assert ftp == 266  # 20-min gives highest

    def test_no_efforts(self):
        assert ftp_from_best_efforts({}) == 0


class TestPowerZones:
    def test_zone_boundaries(self):
        """Check zone boundaries for FTP=200."""
        zones = power_zones(200)
        assert zones["Z1"]["low"] == 0
        assert zones["Z1"]["high"] == 110  # 200 * 0.55
        assert zones["Z4"]["low"] == 182   # 200 * 0.91
        assert zones["Z4"]["high"] == 210  # 200 * 1.05

    def test_all_seven_zones(self):
        zones = power_zones(250)
        assert len(zones) == 7
        assert all(z in zones for z in ["Z1", "Z2", "Z3", "Z4", "Z5", "Z6", "Z7"])


class TestHRZones:
    def test_max_hr_only(self):
        """Simple percentage of max HR."""
        zones = hr_zones(190)
        assert zones["Z1"]["low"] == 95   # 190 * 0.50
        assert zones["Z1"]["high"] == 114  # 190 * 0.60

    def test_karvonen_formula(self):
        """With resting HR, should use Karvonen formula."""
        zones = hr_zones(190, resting_hr=50)
        # Z1 low = 50 + (190-50) * 0.50 = 50 + 70 = 120
        assert zones["Z1"]["low"] == 120
        # Z1 high = 50 + (190-50) * 0.60 = 50 + 84 = 134
        assert zones["Z1"]["high"] == 134

    def test_all_five_zones(self):
        zones = hr_zones(185)
        assert len(zones) == 5


class TestWPerKg:
    def test_calculation(self):
        assert w_per_kg(300, 75.0) == 4.0
        assert w_per_kg(265, 72.0) == 3.68

    def test_zero_weight(self):
        assert w_per_kg(300, 0.0) == 0.0


class TestRiderTypeProfile:
    def test_climber_profile(self):
        efforts = {5: 900, 60: 450, 300: 380, 1200: 320, 3600: 290}
        profile = rider_type_profile(efforts, 280, 70.0)
        assert profile["type"] in ["climber", "time_trialist", "all_rounder"]
        assert isinstance(profile["strengths"], list)
        assert isinstance(profile["weaknesses"], list)

    def test_zero_weight(self):
        profile = rider_type_profile({}, 250, 0.0)
        assert profile["type"] == "all_rounder"


class TestTimeInZones:
    def test_all_zone2(self):
        """All power in Z2 should show time only in Z2."""
        ftp = 200
        # Z2 = 112-150W for FTP=200
        samples = [140] * 100
        zones = time_in_zones(samples, ftp)
        assert zones["Z2"] == 100
        assert zones["Z1"] == 0
        assert zones["Z3"] == 0

    def test_mixed_zones(self):
        ftp = 200
        samples = [50] * 30 + [150] * 30 + [200] * 30  # Z1 + Z2 + Z4
        zones = time_in_zones(samples, ftp)
        assert zones["Z1"] == 30
        assert zones["Z2"] == 30


class TestBestEfforts:
    def test_finds_best_window(self):
        # 100 seconds of data, with a spike at seconds 20-24
        samples = [200] * 100
        for i in range(20, 25):
            samples[i] = 400
        results = best_efforts(samples, [5])
        assert results[5] == 400.0  # Best 5s average is the spike

    def test_insufficient_data(self):
        samples = [200] * 10
        results = best_efforts(samples, [60])
        assert results[60] == 0.0

    def test_multiple_durations(self):
        samples = [250] * 3600
        results = best_efforts(samples, [5, 60, 300])
        assert results[5] == 250.0
        assert results[60] == 250.0
        assert results[300] == 250.0
