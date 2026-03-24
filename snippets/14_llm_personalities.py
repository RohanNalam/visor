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
