import math

from statsmodels.stats.power import FTestAnovaPower


def eta_squared_to_cohens_f(eta_squared: float) -> float:
    return math.sqrt(eta_squared / (1 - eta_squared))


def achieved_power(
    k_groups: int, n_total: int, epsilon_squared: float, alpha: float = 0.05
) -> dict:
    """Power achieved for the observed effect, using the ANOVA F-test as the parametric
    analogue to Kruskal-Wallis (KW has no closed-form power function, so this is the
    standard approximation in practice -- epsilon-squared and eta-squared coincide as
    the parametric analogue here).
    """
    f = eta_squared_to_cohens_f(max(epsilon_squared, 1e-6))
    power = FTestAnovaPower().power(effect_size=f, nobs=n_total, alpha=alpha, k_groups=k_groups)
    return {
        "k_groups": k_groups,
        "n_total": n_total,
        "epsilon_squared": epsilon_squared,
        "cohens_f": f,
        "alpha": alpha,
        "achieved_power": float(power),
    }


def minimum_detectable_effect(
    k_groups: int, n_total: int, alpha: float = 0.05, target_power: float = 0.8
) -> dict:
    """Smallest Cohen's f (and implied eta-squared) detectable at target_power, given
    the actual sample size -- reported alongside achieved_power so the brief can state
    both "here's what we found" and "here's the smallest effect we could have found".
    """
    f = FTestAnovaPower().solve_power(
        nobs=n_total, alpha=alpha, power=target_power, k_groups=k_groups
    )
    eta_sq = f**2 / (1 + f**2)
    return {
        "k_groups": k_groups,
        "n_total": n_total,
        "alpha": alpha,
        "target_power": target_power,
        "minimum_detectable_cohens_f": float(f),
        "minimum_detectable_eta_squared": float(eta_sq),
    }
