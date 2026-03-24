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
