# ============================================================
# SNIPPET 19: Financial Advisor Model
# ============================================================
# Based on SPIVA scorecard data, the average financial advisor
# UNDERPERFORMS the S&P 500 by about 1.5% per year.
# On top of that, they charge a 1% annual management fee.
#
# Advisor return = S&P 500 return - 1.5%/year - 1%/year fee
# ============================================================

# Advisor underperforms by 1.5% annually (SPIVA data)
advisor_underperformance_annual = 0.015

# Advisor charges 1% annual fee
advisor_fee_annual = 0.01

# Calculate per-period drag (for monthly data, divide by 12)
periods_per_year = 12  # monthly
advisor_drag = advisor_underperformance_annual / periods_per_year
# advisor_drag = 0.015 / 12 = 0.00125 per month

# Advisor returns = S&P returns minus the drag
advisor_returns = spy_returns - advisor_drag

# Then subtract the management fee
def apply_annual_fee(returns, fee_annual, frequency):
    periods_per_year = {"D": 252, "W": 52, "M": 12}[frequency]
    fee_period = (1 + fee_annual) ** (1 / periods_per_year) - 1
    return returns - fee_period

advisor_returns = apply_annual_fee(advisor_returns, 0.01, "M")

# Example for one month:
# S&P 500 return  = +2.00%
# Minus 1.5%/12   = -0.125%  (underperformance)
# Minus 1%/12     = -0.083%  (fee)
# Advisor return   = +1.79%  (advisor always trails the S&P)
