"""
Enhanced Monte Carlo simulation
Adds:
- Student-t fat tails
- EWMA volatility clustering
- Distributed jump shocks
- Volatility stress testing
"""

import numpy as np


def run_single_simulation(
    stock_price,
    mu,
    sigma,
    days_to_simulate,
    num_simulations,
    jump_prob=0.0,
    jump_magnitude=0.0,
    df=5,              # Student-t degrees of freedom
    lambda_=0.94       # EWMA decay factor
):
    """
    Run Monte Carlo block with:
    - Student-t shocks
    - Time-varying EWMA volatility
    - Jump process
    """

    # ==============================
    # 1. Student-t shocks
    # ==============================
    z = np.random.standard_t(df, size=(days_to_simulate, num_simulations))
    
    # Scale to unit variance
    z = z / np.sqrt(df / (df - 2))

    # ==============================
    # 2. EWMA Volatility Clustering
    # ==============================
    sigma_t = np.zeros((days_to_simulate, num_simulations))
    sigma_t[0] = sigma

    for t in range(1, days_to_simulate):
        sigma_t[t] = np.sqrt(
            lambda_ * sigma_t[t-1]**2 +
            (1 - lambda_) * (sigma_t[t-1] * z[t-1])**2
        )

    # ==============================
    # 3. Drift + Stochastic Vol
    # ==============================
    daily_returns = (
        mu / 252 +
        sigma_t / np.sqrt(252) * z
    )

    # ==============================
    # 4. Distributed Jump Process
    # ==============================
    if jump_prob > 0:
        jump_matrix = np.random.rand(days_to_simulate, num_simulations) < jump_prob
        daily_returns[jump_matrix] += jump_magnitude

    # ==============================
    # 5. Price Path Construction
    # ==============================
    paths = stock_price * np.cumprod(1 + daily_returns, axis=0)
    final_prices = paths[-1]
    final_returns = (final_prices / stock_price - 1) * 100

    return paths, final_prices, final_returns


def run_monte_carlo(stock_price, stats, days_to_simulate, num_simulations):
    """
    Run base simulation + volatility stress scenarios.
    """

    print(f"\nRunning {num_simulations:,} Monte Carlo simulations...")
    np.random.seed(42)

    mu = stats['stock_expected_return']
    base_sigma = stats['stock_volatility']

    # Volatility stress ladder
    vol_multipliers = [1.0, 1.25, 1.5]

    results = {}

    for multiplier in vol_multipliers:
        sigma = base_sigma * multiplier

        print(f"\n  → Volatility Stress: {multiplier:.2f}x ({sigma*100:.2f}%)")

        paths, final_prices, final_returns = run_single_simulation(
            stock_price,
            mu,
            sigma,
            days_to_simulate,
            num_simulations,
            jump_prob=0.02,       # 2% daily jump probability
            jump_magnitude=-0.04, # -4% shock
            df=5,
            lambda_=0.94
        )

        results[multiplier] = {
            "stock_paths": paths,
            "stock_final_prices": final_prices,
            "stock_final_returns": final_returns
        }

        # Quick tail metrics
        p5 = np.percentile(final_returns, 5)
        p1 = np.percentile(final_returns, 1)

        print(f"     5th percentile return:  {p5:.2f}%")
        print(f"     1st percentile return:  {p1:.2f}%")

    # Return base case for compatibility
    base_case = results[1.0]

    return {
        "stock_paths": base_case["stock_paths"],
        "stock_final_prices": base_case["stock_final_prices"],
        "stock_final_returns": base_case["stock_final_returns"],
        "stress_results": results
    }
