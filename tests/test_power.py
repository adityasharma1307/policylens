from policylens.analysis.power import (
    achieved_power,
    eta_squared_to_cohens_f,
    minimum_detectable_effect,
)


def test_eta_squared_to_cohens_f_zero():
    assert eta_squared_to_cohens_f(0.0) == 0.0


def test_eta_squared_to_cohens_f_known_value():
    # eta^2 = 0.5 -> f = sqrt(0.5 / 0.5) = 1.0
    assert eta_squared_to_cohens_f(0.5) == 1.0


def test_achieved_power_high_for_large_effect_and_n():
    result = achieved_power(k_groups=3, n_total=10000, epsilon_squared=0.3)
    assert result["achieved_power"] > 0.99


def test_achieved_power_low_for_tiny_effect_and_n():
    result = achieved_power(k_groups=3, n_total=30, epsilon_squared=0.001)
    assert result["achieved_power"] < 0.2


def test_minimum_detectable_effect_shrinks_with_more_data():
    small_n = minimum_detectable_effect(k_groups=3, n_total=100)
    large_n = minimum_detectable_effect(k_groups=3, n_total=100000)
    assert large_n["minimum_detectable_eta_squared"] < small_n["minimum_detectable_eta_squared"]
