# ============================================================
# SNIPPET 4: Annualized Return Formula
# ============================================================
# Formula: Rannual = (1 + CR) ^ (252/T) - 1
#
# Converts a total return into a yearly average.
# 252 = trading days per year, T = number of days in the data.
#
# If you made +50% over 3 years:
#   Rannual = (1.50) ^ (1/3) - 1 = 14.5% per year
# ============================================================

periods_per_year = {"D": 252, "W": 52, "M": 12}

annualized = (1 + cumulative) ** (periods_per_year / len(returns)) - 1

# Example:
# cumulative = 1.14 (114% total growth over 73 monthly periods)
# annualized = (1 + 1.14) ^ (12/73) - 1 = 13.6% per year
