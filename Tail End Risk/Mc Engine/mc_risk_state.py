import numpy as np

def calculate_risk_state_score(
    stock_data,
    final_returns,
    stock_cvar
):
    """
    Build 4-component Risk State Score:
    1. Volatility regime ratio
    2. Tail thickness ratio
    3. Jump intensity proxy
    4. Distribution width
    """

    # =====================================
    # 1. Volatility Regime Ratio
    # =====================================
    returns = stock_data['Close'].pct_change().dropna()

    vol_20 = returns.rolling(20).std().iloc[-1] * np.sqrt(252)
    vol_100 = returns.rolling(100).std().iloc[-1] * np.sqrt(252)

    vol_ratio = vol_20 / vol_100 if vol_100 != 0 else 1.0

    # Normalize (1 = neutral)
    vol_score = min(max((vol_ratio - 0.7) / (1.5 - 0.7), 0), 1)


    # =====================================
    # 2. Tail Thickness Ratio
    # =====================================
    var_99 = abs(stock_cvar["var_99"])
    cvar_99 = abs(stock_cvar["cvar_99"])

    tail_ratio = cvar_99 / var_99 if var_99 != 0 else 1.0

    # Typical range ~1.1 – 1.6
    tail_score = min(max((tail_ratio - 1.1) / (1.6 - 1.1), 0), 1)


    # =====================================
    # 3. Jump Intensity Proxy
    # =====================================
    # Count large historical daily drops
    jump_threshold = -0.03
    jump_days = (returns < jump_threshold).sum()
    jump_freq = jump_days / len(returns)

    # Typical daily crash freq 0–3%
    jump_score = min(jump_freq / 0.03, 1)


    # =====================================
    # 4. Distribution Width
    # =====================================
    p95 = np.percentile(final_returns, 95)
    p5 = np.percentile(final_returns, 5)

    width = abs(p95 - p5)

    # Normalize assuming 10%–60% range
    width_score = min(max((width - 10) / (60 - 10), 0), 1)


    # =====================================
    # Composite
    # =====================================
    composite = np.mean([
        vol_score,
        tail_score,
        jump_score,
        width_score
    ])

    return {
        "vol_ratio": vol_ratio,
        "tail_ratio": tail_ratio,
        "jump_freq": jump_freq,
        "distribution_width": width,
        "risk_state_score": composite * 100
    }
