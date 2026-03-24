# ============================================================
# SNIPPET 2: Cumulative Return Formula
# ============================================================
# Formula: CR = Product of (1 + rt) for all t, minus 1
#
# Multiply all daily returns together to find total growth.
# If returns were +1%, +2%, -0.5%:
#   CR = (1.01 * 1.02 * 0.995) - 1 = +2.5%
# ============================================================

cumulative = (1 + returns).prod() - 1

# Example:
# returns = [+0.01, +0.02, -0.005]
# (1.01) * (1.02) * (0.995) = 1.02499
# cumulative = 1.02499 - 1 = 0.02499 = +2.5%
