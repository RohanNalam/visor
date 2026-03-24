# ============================================================
# COMBINED SNIPPETS (01-25)
# ============================================================
# This file concatenates all snippet files in order.
# The original files remain unchanged in `snippets/`.
# ============================================================

# ------------------------------------------------------------
# Source: snippets/01_daily_return.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 1: Daily Return Formula
# ============================================================
# Formula: rt = (Pt - Pt-1) / Pt-1
#
# This converts raw stock prices into percent changes.
# If the S&P 500 was $4000 yesterday and $4040 today,
# the return is (4040 - 4000) / 4000 = +1%.
# ============================================================

def to_period_returns(prices, frequency):
    period_prices = prices.resample(frequency).last()
    returns = period_prices.pct_change().dropna(how="all")
    return returns

# Example:
# Input prices:  [4000, 4040, 3990, 4100]
# Output returns: [+1.0%, -1.2%, +2.8%]


# ------------------------------------------------------------
# Source: snippets/02_cumulative_return.py
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Source: snippets/03_growth_of_one_dollar.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 3: Growth of $1 (The Line on the Graph)
# ============================================================
# Formula: Growth(t) = Product of (1 + ri) for i=1 to t
#
# This is what gets plotted on the chart. Each point shows
# what $1 invested at the start would be worth on that day.
#
# If signal = 1 (BUY), you earn the market return that day.
# If signal = 0 (SELL), you earn 0 (sitting in cash).
# ============================================================

def compute_strategy_series(returns, signal):
    if signal is None:
        strat_returns = returns           # Buy and hold
    else:
        strat_returns = returns * signal  # Only earn when invested
    return (1 + strat_returns).cumprod()  # Running growth of $1

# Example (3 days, signal = [1, 0, 1]):
# Day 1: market +2%, signal=1 (BUY)  -> earn +2%  -> $1.00 * 1.02 = $1.02
# Day 2: market +3%, signal=0 (SELL) -> earn  0%  -> $1.02 * 1.00 = $1.02
# Day 3: market -1%, signal=1 (BUY)  -> earn -1%  -> $1.02 * 0.99 = $1.01


# ------------------------------------------------------------
# Source: snippets/04_annualized_return.py
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Source: snippets/05_volatility.py
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Source: snippets/06_sharpe_ratio.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 6: Sharpe Ratio Formula
# ============================================================
# Formula: S = (Rannual - Rf) / sigma_annual
#
# Measures return PER UNIT OF RISK. Higher = better.
# Rf = risk-free rate (2%, what a savings account earns)
# Only returns ABOVE the risk-free rate count.
#
# Sharpe of 1.0 = you got 1% extra for every 1% of risk
# Sharpe of 0.5 = you only got 0.5% extra per 1% of risk
# ============================================================

# Convert annual risk-free rate to per-period rate
rf_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1

# Subtract the risk-free rate from each return
excess = returns - rf_period

# Sharpe = average excess return / volatility
sharpe = excess.mean() / returns.std() * np.sqrt(periods_per_year)

# Example:
# Annual return = 14%, Risk-free = 2%, Volatility = 17%
# Sharpe = (14% - 2%) / 17% = 0.71


# ------------------------------------------------------------
# Source: snippets/07_max_drawdown.py
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Source: snippets/08_look_ahead_bias_prevention.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 8: Preventing Look-Ahead Bias
# ============================================================
# Formula: rt_portfolio = Signal(t-1) * rt
#
# The decision from YESTERDAY is applied to TODAY's return.
# This prevents the model from "cheating" by seeing the future.
#
# shift(1) moves every signal forward by one period.
# Monday's decision -> applied to Tuesday's return.
# ============================================================

# Quant model: shift signals by 1 period
def quant_model_signals(returns, model):
    signals = QUANT_MODELS[model](returns)
    return signals.shift(1).fillna(0.0)  # Yesterday's signal for today

# LLM models: same shift applied
for model, signal in llm_signals.items():
    raw_signal = signal.reindex(spy_returns.index).ffill().fillna(0.0)
    aligned_signal = raw_signal.shift(1).fillna(0.0)  # Yesterday's signal
    llm_series[model] = compute_strategy_series(spy_returns, aligned_signal)

# Example:
# Day  | Signal computed | Signal USED | Market return | You earn
# Mon  | BUY (1)        | --          | +1%           | 0% (no signal yet)
# Tue  | SELL (0)       | BUY (1)     | -2%           | -2% (Mon's BUY)
# Wed  | BUY (1)        | SELL (0)    | +3%           | 0% (Tue's SELL)
# Thu  | BUY (1)        | BUY (1)     | +1%           | +1% (Wed's BUY)


# ------------------------------------------------------------
# Source: snippets/09_quant_model_rsi.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 9: RSI (Relative Strength Index)
# ============================================================
# Formula: RS = Average Gain / Average Loss (over 14 periods)
#          RSI = 100 - (100 / (1 + RS))
#
# RSI ranges from 0 to 100.
# Above 70 = "overbought" (market went up too fast, might crash)
# Below 30 = "oversold" (market dropped too hard, might bounce)
# Below 70 = safe to invest
# ============================================================

def _rsi(prices, window=14):
    delta = prices.diff()                               # Price changes
    gain = delta.clip(lower=0).rolling(window).mean()   # Average gains
    loss = (-delta.clip(upper=0)).rolling(window).mean() # Average losses
    rs = gain / loss.replace(0, pd.NA)                  # Relative strength
    return 100 - (100 / (1 + rs))                       # RSI formula

rsi = _rsi(prices, window=14)
rsi_ok = rsi < 70  # True = safe to buy, False = overbought

# Example:
# Average gain over 14 days = $20, Average loss = $10
# RS = 20/10 = 2
# RSI = 100 - (100 / (1+2)) = 100 - 33.3 = 66.7
# 66.7 < 70, so rsi_ok = True (safe to buy)


# ------------------------------------------------------------
# Source: snippets/10_quant_model_trend.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 10: Trend / Moving Average Crossover
# ============================================================
# Formula: Trend = SMA(6) / SMA(12) - 1
#
# SMA(6)  = Simple Moving Average over 6 periods (short-term)
# SMA(12) = Simple Moving Average over 12 periods (long-term)
#
# If the short-term average is ABOVE the long-term average,
# the market is trending upward = BUY signal.
# This is one of the most classic trading indicators.
# ============================================================

prices = (1 + returns).cumprod()  # Convert returns back to prices

# Calculate the two moving averages
short_average = prices.rolling(6).mean()   # 6-period average
long_average = prices.rolling(12).mean()   # 12-period average

# Trend = how much the short average is above/below the long average
trend = short_average / long_average - 1
trend_up = trend > 0  # True if short average > long average

# Example:
# 6-month average price  = $4200
# 12-month average price = $4100
# Trend = (4200/4100) - 1 = +2.4% -> trend_up = True (BUY)
#
# If 6-month avg = $3900, 12-month avg = $4100:
# Trend = (3900/4100) - 1 = -4.9% -> trend_up = False (SELL)


# ------------------------------------------------------------
# Source: snippets/11_quant_model_momentum.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 11: Momentum Indicator
# ============================================================
# Formula: Momentum = Pt / Pt-3 - 1
#
# Compares today's price to the price 3 periods ago.
# If today's price is higher, the market has upward momentum.
# Momentum traders believe things going up keep going up.
# ============================================================

prices = (1 + returns).cumprod()  # Convert returns to prices

# How much has the price changed over the last 3 periods?
momentum = prices / prices.shift(3) - 1
momentum_up = momentum > 0  # True if price went up

# Example:
# Price today = $4200, Price 3 months ago = $4000
# Momentum = (4200/4000) - 1 = +5% -> momentum_up = True (BUY)
#
# Price today = $3800, Price 3 months ago = $4000
# Momentum = (3800/4000) - 1 = -5% -> momentum_up = False (SELL)


# ------------------------------------------------------------
# Source: snippets/12_quant_model_volatility_filter.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 12: Volatility Filter
# ============================================================
# Formula: Vol = std(returns) over 6 periods
#
# If current volatility is BELOW the 12-period median,
# the market is calmer than usual = safer to invest.
# If volatility is spiking, the model stays in cash.
# ============================================================

# Current volatility over last 6 periods
volatility = returns.rolling(6).std()

# Historical median volatility over last 12 periods
median_vol = volatility.rolling(12).median()

# Is the market calmer than usual?
vol_ok = volatility < median_vol

# Example:
# Current 6-month volatility = 12%
# 12-month median volatility = 15%
# 12% < 15%, so vol_ok = True (market is calm, safe to buy)
#
# Current 6-month volatility = 25%
# 12-month median volatility = 15%
# 25% > 15%, so vol_ok = False (market is shaky, stay in cash)


# ------------------------------------------------------------
# Source: snippets/13_quant_decision_rule.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 13: The Quant Model Decision Rule (2 out of 4)
# ============================================================
# The quant model checks 4 conditions every period:
#   1. Trend up?      (Moving Average Crossover)
#   2. Momentum up?   (Price higher than 3 periods ago)
#   3. RSI < 70?      (Market not overbought)
#   4. Volatility OK? (Market calmer than usual)
#
# If at least 2 out of 4 are True -> BUY (invest in S&P 500)
# If fewer than 2 are True        -> SELL (stay in cash)
# ============================================================

def _trend_momentum_rsi_vol(returns):
    prices = (1 + returns).cumprod()

    # The 4 indicators
    momentum = prices / prices.shift(3) - 1
    trend = prices.rolling(6).mean() / prices.rolling(12).mean() - 1
    volatility = returns.rolling(6).std()
    rsi = _rsi(prices, window=14)

    # Check each condition
    trend_up = trend > 0               # Condition 1
    momentum_up = momentum > 0         # Condition 2
    vol_ok = volatility < volatility.rolling(12).median()  # Condition 3
    rsi_ok = rsi < 70                  # Condition 4

    # Count how many conditions are True
    conditions_met = (trend_up.astype(int) + momentum_up.astype(int)
                      + vol_ok.astype(int) + rsi_ok.astype(int))

    # BUY if at least 2 out of 4 conditions are met
    signal = conditions_met >= 2
    return signal.astype(float).fillna(0.0)

# Example:
# trend_up=True(1), momentum_up=True(1), vol_ok=False(0), rsi_ok=True(1)
# conditions_met = 1 + 1 + 0 + 1 = 3
# 3 >= 2, so signal = 1.0 (BUY)
#
# trend_up=False(0), momentum_up=False(0), vol_ok=True(1), rsi_ok=False(0)
# conditions_met = 0 + 0 + 1 + 0 = 1
# 1 < 2, so signal = 0.0 (SELL, stay in cash)


# ------------------------------------------------------------
# Source: snippets/14_llm_personalities.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 14: LLM Model Personalities
# ============================================================
# Each LLM has two traits that control its investing behavior:
#
# skill      = how good it is at dodging crashes (0 to 1)
#              Higher = better at reading danger signals
#
# aggression = how eager it is to stay invested (0 to 1)
#              Higher = more time in the market, less in cash
# ============================================================

model_profiles = {
    "gpt":            {"skill": 0.55, "aggression": 0.85},
    "claude_sonnet":  {"skill": 0.60, "aggression": 0.80},
    "gemini":         {"skill": 0.45, "aggression": 0.90},
    "deepseek":       {"skill": 0.65, "aggression": 0.75},
    "grok":           {"skill": 0.50, "aggression": 0.82},
}

# GPT:           Aggressive (0.85), decent crash detection (0.55)
#                -> Stays invested a lot, sometimes gets caught in drops
#
# Claude Sonnet: Balanced (0.80), good crash detection (0.60)
#                -> More careful, avoids some bad months
#
# Gemini:        Very aggressive (0.90), weak crash detection (0.45)
#                -> Almost always invested, barely dodges anything
#
# DeepSeek:      Most cautious (0.75), best crash detection (0.65)
#                -> Sits in cash more, but dodges the worst crashes
#
# Grok:          Middle of the road (0.82, 0.50)
#                -> Average on both fronts


# ------------------------------------------------------------
# Source: snippets/15_llm_decision_process.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 15: How Each LLM Makes a BUY/SELL Decision
# ============================================================
# Each day, the LLM looks at recent market data and computes
# a "buy score" (0 to 1). Higher score = more likely to BUY.
#
# The LLM checks:
#   - Last 5 days of returns (is the market dropping?)
#   - 20-day trend (is the market in a downtrend?)
#   - Recent volatility (is the market shaking?)
# Then adds randomness so each run gives different results.
# ============================================================

for idx in range(len(returns)):
    # Start with the model's base aggression (bias toward investing)
    buy_score = aggression

    # Look at the last 5 days of market returns
    recent_5 = returns.iloc[max(0, idx - 5):idx]
    recent_mean = recent_5.mean()
    recent_vol = recent_5.std()

    # Check the 20-day price trend
    lookback = min(idx, 20)
    trend = prices.iloc[idx] / prices.iloc[idx - lookback] - 1

    # RULE 1: If recent returns are negative, reduce buy score
    if recent_mean < -0.005:       # Losing > 0.5% per day
        buy_score -= skill * 0.4
    if recent_mean < -0.015:       # Losing > 1.5% per day (bad)
        buy_score -= skill * 0.3

    # RULE 2: If the trend is negative, reduce buy score
    if trend < -0.02:              # Market down > 2% over 20 days
        buy_score -= skill * 0.3
    elif trend > 0.03:             # Market up > 3% over 20 days
        buy_score += 0.1

    # RULE 3: If volatility is spiking, reduce buy score
    if recent_vol > 0.02:          # Daily swings > 2%
        buy_score -= skill * 0.2

    # RULE 4: Add randomness (simulates LLM "temperature")
    noise = rng.normal(0, 0.15)
    buy_score += noise

    # Clamp between 0 and 1, then flip a weighted coin
    buy_score = max(0.0, min(1.0, buy_score))
    signal = 1.0 if rng.random() < buy_score else 0.0  # BUY or SELL


# ------------------------------------------------------------
# Source: snippets/16_llm_crash_dodge_example.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 16: Worked Example - DeepSeek Dodging a Crash
# ============================================================
# DeepSeek: skill=0.65 (best at spotting crashes), aggression=0.75
#
# Scenario: March 2020 COVID crash. The market has been
# dropping for 5 days straight, trend is very negative.
# ============================================================

# DeepSeek starts with its aggression as the base buy score
buy_score = 0.75

# Step 1: Last 5 days averaged -2% per day (market is crashing)
recent_mean = -0.02
# recent_mean < -0.005, so:
buy_score -= 0.65 * 0.4   # buy_score = 0.75 - 0.26 = 0.49
# recent_mean < -0.015, so ALSO:
buy_score -= 0.65 * 0.3   # buy_score = 0.49 - 0.195 = 0.295

# Step 2: 20-day trend is -15% (massive downtrend)
trend = -0.15
# trend < -0.02, so:
buy_score -= 0.65 * 0.3   # buy_score = 0.295 - 0.195 = 0.10

# Step 3: Volatility is 4% per day (extremely shaky)
recent_vol = 0.04
# recent_vol > 0.02, so:
buy_score -= 0.65 * 0.2   # buy_score = 0.10 - 0.13 = -0.03

# Step 4: Add random noise of +0.05
buy_score += 0.05          # buy_score = 0.02

# Clamp to [0, 1]
buy_score = max(0.0, min(1.0, 0.02))  # buy_score = 0.02

# RESULT: Only 2% chance of buying.
# DeepSeek almost certainly stays in cash and DODGES the crash.
# While the S&P 500 drops -12% that month, DeepSeek loses 0%.


# ------------------------------------------------------------
# Source: snippets/17_llm_fresh_results.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 17: Why Results Are Different Every Run
# ============================================================
# The random seed is based on the current time in milliseconds.
# Since time is always different, the random numbers change,
# so each LLM makes different decisions each run.
#
# The model name also affects the seed, so GPT and Claude
# get different random numbers even in the same run.
# ============================================================

import time
import numpy as np

# Seed = current time in milliseconds + model name hash
seed_base = int(time.time() * 1000) % (2**31)
model_hash = sum(ord(c) for c in model_name)
rng = np.random.default_rng(seed_base + model_hash)

# Example:
# Run 1 at 2:15:30 PM -> seed = 1739742930000 + 321 = unique seed A
# Run 2 at 2:15:45 PM -> seed = 1739742945000 + 321 = unique seed B
# Different seeds -> different random numbers -> different BUY/SELL decisions
#
# Same run, different models:
# GPT seed    = 1739742930000 + 340 = seed C
# Claude seed = 1739742930000 + 1271 = seed D
# Different seeds -> GPT and Claude make independent decisions


# ------------------------------------------------------------
# Source: snippets/18_llm_prompt_template.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 18: The LLM Prompt Template (for Live API Mode)
# ============================================================
# When using real LLM APIs (GPT, Claude, etc.), each model
# receives this exact prompt for every trading day.
#
# The prompt ONLY gives data up to today. It never reveals
# tomorrow's prices. This prevents look-ahead bias.
# ============================================================

def _build_llm_prompt(current_date, recent_returns, trend_20d, volatility_20d):
    returns_list = [f"{value:.2%}" for value in recent_returns.tolist()]
    return (
        "You are a financial decision assistant.\n\n"
        f"Date: {current_date.date().isoformat()}\n"
        f"Last {len(returns_list)} days returns: {returns_list}\n"
        f"20-day trend (price vs 20D MA): {trend_20d:.2%}\n"
        f"20-day volatility: {volatility_20d:.2%}\n\n"
        "Based only on the information available up to today, "
        "should an investor be invested in the S&P 500 tomorrow?\n"
        "Respond with exactly one word: BUY, HOLD, or SELL."
    )

# Example prompt sent to GPT for June 15, 2024:
# --------------------------------------------------
# You are a financial decision assistant.
#
# Date: 2024-06-15
# Last 5 days returns: ['0.50%', '-0.20%', '0.80%', '0.10%', '-0.30%']
# 20-day trend (price vs 20D MA): 3.20%
# 20-day volatility: 1.10%
#
# Based only on the information available up to today,
# should an investor be invested in the S&P 500 tomorrow?
# Respond with exactly one word: BUY, HOLD, or SELL.
# --------------------------------------------------
# GPT responds: "BUY" -> converted to signal = 1.0


# ------------------------------------------------------------
# Source: snippets/19_advisor_model.py
# ------------------------------------------------------------
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


# ------------------------------------------------------------
# Source: snippets/20_hybrid_model.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 20: The Hybrid Model (Advisor + Best AI Signals)
# ============================================================
# From the methodology: "If the LLM or quant model beats the
# advisor, combine them to see if advisors stay relevant."
#
# The Hybrid takes the BEST model's BUY/SELL signals and
# applies them to the ADVISOR's returns. This answers:
# "If an advisor used AI to tell them when to buy and sell,
#  would they perform better than either one alone?"
# ============================================================

# Step 1: Find which non-advisor strategy performed best
non_advisor_excess = excess_over_sp.drop("Advisor", errors="ignore")
best_signal_strategy = non_advisor_excess.idxmax()

# Step 2: Get that strategy's BUY/SELL signals
if best_signal_strategy in llm_series:
    hybrid_signal = align_signals_to_returns(
        llm_signals[best_signal_strategy], advisor_returns.index
    )
    hybrid_label = f"Hybrid (Advisor + {best_signal_strategy})"

# Step 3: Apply the AI's signals to the advisor's returns
hybrid_series = compute_strategy_series(advisor_returns, hybrid_signal)

# What this means:
# - When GPT says BUY, the advisor invests (earns advisor returns)
# - When GPT says SELL, the advisor goes to cash (earns 0%)
# - The advisor still has their 1.5% underperformance and 1% fee
# - But now they dodge crashes using AI timing
#
# If Hybrid beats both Advisor and the AI alone:
#   -> Advisors have a future WITH AI assistance
# If Hybrid still loses to AI alone:
#   -> Advisors add no value, AI replaces them


# ------------------------------------------------------------
# Source: snippets/21_find_winner.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 21: Finding the Winner
# ============================================================
# After all strategies run over the same time period,
# compare final values to determine who beat the S&P 500.
#
# Excess = strategy's final value - S&P 500's final value
# Positive excess = BEAT the market
# Negative excess = LOST to the market
# Highest excess = WINNER
# ============================================================

# Get the final value of each strategy (what $1 became)
sp500_final = series_df["S&P 500"].iloc[-1]   # e.g., $2.14
final_values = series_df.iloc[-1]              # All strategies

# Subtract S&P 500 from each to get excess return
excess_over_sp = (final_values - sp500_final).drop("S&P 500")

# The strategy with the highest excess wins
best_strategy = excess_over_sp.idxmax()
best_excess = excess_over_sp.loc[best_strategy]

# Example output:
# S&P 500:       $2.14 (the benchmark - always at 0 excess)
# Advisor:       $1.96  -> excess = 1.96 - 2.14 = -0.18 (lost $0.18)
# GPT:           $2.21  -> excess = 2.21 - 2.14 = +0.07 (beat by $0.07)
# Claude Sonnet: $1.94  -> excess = 1.94 - 2.14 = -0.20 (lost $0.20)
# Quant Model:   $1.88  -> excess = 1.88 - 2.14 = -0.26 (lost $0.26)
#
# Winner: GPT with +0.07 excess over S&P 500


# ------------------------------------------------------------
# Source: snippets/22_excess_chart.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 22: The Final Chart (Excess Return vs S&P 500)
# ============================================================
# This is the main output of the entire project.
# The S&P 500 is shown as a flat dashed line at zero.
# Every other strategy shows how much it is above or below.
#
# Lines ABOVE zero = BEAT the S&P 500
# Lines BELOW zero = LOST to the S&P 500
# ============================================================

def plot_excess_over_sp500(series, output_dir, show=False):
    # Subtract S&P 500 from every strategy
    excess = series.subtract(series["S&P 500"], axis=0)
    excess = excess.drop(columns=["S&P 500"])

    fig, ax = plt.subplots(figsize=(10, 5.5))

    # Plot each strategy's excess return over time
    for i, col in enumerate(excess.columns):
        color = PUBLICATION_COLORS[i % len(PUBLICATION_COLORS)]
        ax.plot(excess.index, excess[col], label=col, color=color)

    # S&P 500 = flat line at zero (the benchmark)
    ax.axhline(y=0, color="black", linewidth=1, linestyle="--",
               label="S&P 500 Baseline")

    ax.legend()
    ax.set_title("Excess Return vs S&P 500")
    ax.set_xlabel("Date")
    ax.set_ylabel("Excess over S&P 500")

    if show:
        plt.show()  # Opens a popup window on your screen

# How to read this chart:
# - Dashed line at 0 = S&P 500 (buy and hold)
# - Advisor line at -0.18 = lost 18 cents per dollar vs S&P
# - GPT line at +0.07 = made 7 cents more per dollar vs S&P
# - If lines cross above zero, that model is currently winning
# - If lines cross below zero, that model is currently losing


# ------------------------------------------------------------
# Source: snippets/23_all_metrics.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 23: Computing All 5 Performance Metrics
# ============================================================
# For every strategy, compute these 5 numbers:
#   1. Cumulative return  = total growth (higher is better)
#   2. Annualized return  = average yearly growth (higher is better)
#   3. Volatility         = risk level (lower is safer)
#   4. Sharpe ratio       = return per unit of risk (higher is better)
#   5. Max drawdown       = worst crash (closer to 0 is safer)
# ============================================================

def performance_metrics(returns, risk_free_annual, frequency):
    periods_per_year = {"D": 252, "W": 52, "M": 12}.get(frequency, 52)
    rf_period = (1 + risk_free_annual) ** (1 / periods_per_year) - 1
    excess = returns - rf_period

    # 1. Total growth
    cumulative = (1 + returns).prod() - 1

    # 2. Average yearly growth
    annualized = (1 + cumulative) ** (periods_per_year / len(returns)) - 1

    # 3. How much returns bounce around
    volatility = returns.std() * np.sqrt(periods_per_year)

    # 4. Return per unit of risk
    sharpe = excess.mean() / returns.std() * np.sqrt(periods_per_year)

    # 5. Worst peak-to-bottom drop
    max_dd = max_drawdown((1 + returns).cumprod())

    return {
        "cumulative_return": cumulative,
        "annualized_return": annualized,
        "volatility": volatility,
        "sharpe": sharpe,
        "max_drawdown": max_dd,
    }

# Example output for one strategy:
# {
#     "cumulative_return": 1.14,    -> grew 114% total
#     "annualized_return": 0.136,   -> 13.6% per year
#     "volatility": 0.171,          -> 17.1% annual risk
#     "sharpe": 0.715,              -> decent risk-adjusted return
#     "max_drawdown": -0.248,       -> worst crash was -24.8%
# }


# ------------------------------------------------------------
# Source: snippets/24_data_loading.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 24: Loading S&P 500 Price Data from CSV
# ============================================================
# The CSV file (data/prices.csv) has columns:
#   date, SPX (S&P 500 prices), AOR (advisor proxy ETF)
#
# This function reads the file, filters to the chosen dates,
# and returns a clean table of prices.
# ============================================================

def load_prices_csv(path, date_column, tickers, start, end):
    # Step 1: Read the CSV file
    df = pd.read_csv(path)

    # Step 2: Convert date strings to actual dates
    df[date_column] = pd.to_datetime(df[date_column])

    # Step 3: Set date as the index and sort chronologically
    df = df.set_index(date_column).sort_index()

    # Step 4: Filter to only the date range we want
    df = df[(df.index >= pd.to_datetime(start))
            & (df.index <= pd.to_datetime(end))]

    # Step 5: Return only the columns we need
    return df[tickers].dropna(how="all")

# Example:
# load_prices_csv("data/prices.csv", "date", ["SPX","AOR"],
#                 "2025-01-01", "2025-01-31")
#
# Returns:
# date        | SPX      | AOR
# 2025-01-02  | 5881.63  | 52.71
# 2025-01-03  | 5942.47  | 52.89
# 2025-01-06  | 5975.38  | 52.95
# ...


# ------------------------------------------------------------
# Source: snippets/25_pipeline_overview.py
# ------------------------------------------------------------
# ============================================================
# SNIPPET 25: The Full Pipeline (How Everything Connects)
# ============================================================
# This is main.py - the brain that runs the entire competition.
# It loads data, runs all models, finds the winner, and shows
# the chart.
# ============================================================

def main():
    config = parse_args()  # Read settings (dates, frequency, etc.)

    # STEP 1: Run the backtest competition
    series_df, metrics_df, best_strategy, best_excess, output_dir = (
        run_backtest(config)
    )
    # series_df = table with growth-of-$1 for ALL strategies
    # metrics_df = table with 5 metrics for ALL strategies
    # best_strategy = name of the winner
    # best_excess = how much the winner beat S&P 500 by

    # STEP 2: Save charts as PNG files (for the research paper)
    plot_series(series_df, output_dir, show=False)
    plot_excess_over_sp500(series_df, output_dir, show=False)
    plot_metrics_bars(metrics_df, output_dir)

    # STEP 3: Print the winner
    print(f"Winner vs S&P 500: {best_strategy} (excess {best_excess:.4f})")

    # STEP 4: Show the popup chart (Excess Return vs S&P 500)
    plot_excess_over_sp500(series_df, output_dir=None, show=True)

# Inside run_backtest(), the steps are:
#   1. Load S&P 500 prices from CSV          (data.py)
#   2. Convert prices to returns              (data.py)
#   3. Create advisor curve (S&P - 1.5% - 1% fee)
#   4. Generate 5 LLM BUY/SELL signals       (llm.py)
#   5. Generate quant model BUY/SELL signals  (quant.py)
#   6. Apply all signals with shift(1) to prevent look-ahead bias
#   7. Build growth-of-$1 curves for all strategies
#   8. Find winner (highest excess over S&P 500)
#   9. Create Hybrid if AI beats advisor      (main.py)
#  10. Compute all 5 metrics                  (metrics.py)
