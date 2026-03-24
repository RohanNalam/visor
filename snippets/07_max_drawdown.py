# ============================================================
# SNIPPET 7: Maximum Drawdown Formula
# ============================================================
# Formula: Max Drawdown = min of (Value(t) / Peak(t) - 1)
#
# Tracks the WORST drop from any peak to any bottom.
# Shows how bad the worst crash was for each strategy.
#
# If the portfolio hit $1.50 then fell to $1.20:
#   Drawdown = (1.20 / 1.50) - 1 = -20%
# ============================================================

def max_drawdown(series):
    peak = series.cummax()          # Highest value ever seen so far
    drawdown = (series / peak) - 1  # How far below the peak right now
    return float(drawdown.min())    # The worst (most negative) drop

# Example:
# Portfolio values: [$1.00, $1.20, $1.50, $1.10, $1.30, $1.60]
# Peaks:           [$1.00, $1.20, $1.50, $1.50, $1.50, $1.60]
# Drawdowns:       [  0%,    0%,    0%,  -26.7%, -13.3%,  0% ]
# Max drawdown = -26.7% (the drop from $1.50 to $1.10)
