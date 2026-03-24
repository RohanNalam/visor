#!/usr/bin/env python3
"""Quick check that your API keys are set and working."""
import os
import sys
import requests


def check_openai():
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key:
        print("❌ OPENAI_API_KEY  — not set")
        return False
    try:
        r = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {key}"},
            json={
                "model": "gpt-4o-mini",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Say OK"}],
            },
            timeout=15,
        )
        if r.status_code == 200:
            print("✅ OPENAI_API_KEY  — working")
            return True
        print(f"❌ OPENAI_API_KEY  — HTTP {r.status_code}: {r.json().get('error', {}).get('message', r.text[:100])}")
        return False
    except Exception as e:
        print(f"❌ OPENAI_API_KEY  — error: {e}")
        return False


def check_anthropic():
    key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        print("❌ ANTHROPIC_API_KEY — not set")
        return False
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-5-20250929",
                "max_tokens": 5,
                "messages": [{"role": "user", "content": "Say OK"}],
            },
            timeout=15,
        )
        if r.status_code == 200:
            print("✅ ANTHROPIC_API_KEY — working")
            return True
        print(f"❌ ANTHROPIC_API_KEY — HTTP {r.status_code}: {r.json().get('error', {}).get('message', r.text[:100])}")
        return False
    except Exception as e:
        print(f"❌ ANTHROPIC_API_KEY — error: {e}")
        return False


if __name__ == "__main__":
    print("Checking API keys...\n")
    ok1 = check_openai()
    ok2 = check_anthropic()
    print()
    if ok1 and ok2:
        print("Both keys working. You can run:")
        print('  python3 main.py --prices-csv data/prices.csv --frequency D \\')
        print('    --start 2025-01-01 --end 2025-01-31 \\')
        print('    --llm-mode api --llm-models "gpt-4o-mini,claude-sonnet-4-5-20250929"')
    elif ok1:
        print("Only OpenAI key working. You can run with OpenAI models only:")
        print('  python3 main.py --prices-csv data/prices.csv --frequency D \\')
        print('    --start 2025-01-01 --end 2025-01-31 \\')
        print('    --llm-mode api --llm-models "gpt-4o-mini"')
    elif ok2:
        print("Only Anthropic key working. You can run with Claude models only:")
        print('  python3 main.py --prices-csv data/prices.csv --frequency D \\')
        print('    --start 2025-01-01 --end 2025-01-31 \\')
        print('    --llm-mode api --llm-models "claude-sonnet-4-5-20250929"')
    else:
        print("No keys working. Set them with:")
        print('  export OPENAI_API_KEY="sk-..."')
        print('  export ANTHROPIC_API_KEY="sk-ant-..."')
        sys.exit(1)
