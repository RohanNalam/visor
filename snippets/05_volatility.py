# ============================================================
# SNIPPET 5: Volatility Formula
# ============================================================
# Formula: sigma = std(rt) * sqrt(252)
#
# Standard deviation measures how much returns bounce around.
# Multiply by sqrt(252) to convert daily to annual volatility.
#
# High volatility = risky, unstable returns (+5%, -4%, +6%)
# Low volatility  = stable, calm returns (+0.1%, +0.2%, +0.1%)
# ============================================================

import numpy as np

volatility = returns.std() * np.sqrt(periods_per_year)

# Example:
# Daily returns std = 0.012 (1.2% per day)
# Annual volatility = 0.012 * sqrt(252) = 0.012 * 15.87 = 19.1%
