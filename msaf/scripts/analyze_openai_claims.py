#!/usr/bin/env python3
"""Minimal analysis script for OpenAI claim Lean files.
Fetches Lean formalizations for local smoothing (079.md) and ETH refutation (378.md),
extracts top-level theorem names, and runs `lake build` to verify.
Assumes `lean` and `lake` are installed and in PATH.
"""
import subprocess, sys, json, urllib.request

LEANS = {
    "local_smoothing": "https://raw.githubusercontent.com/openai/math/main/lean/docs/079.md",
    "eth_false": "https://raw.githubusercontent.com/openai/math/main/lean/docs/378.md",
}

def fetch(url):
    with urllib.request.urlopen(url) as resp:
        return resp.read().decode()

def extract_theorems(content: str):
    # Very naive: lines starting with "theorem" or "lemma"
    names = []
    for line in content.splitlines():
        if line.lstrip().startswith("theorem ") or line.lstrip().startswith("lemma "):
            parts = line.split()
            if len(parts) >= 2:
                names.append(parts[1])
    return names

def main():
    for label, url in LEANS.items():
        print(f"Fetching {label} ...", file=sys.stderr)
        txt = fetch(url)
        theorems = extract_theorems(txt)
        print(f"{label}: {len(theorems)} top-level results")
        for name in theorems:
            print(f"  - {name}")
    # Optional: run lake build in lean directory if present
    try:
        subprocess.run(["lake", "build"], cwd="lean", check=True, capture_output=True)
        print("lake build succeeded", file=sys.stderr)
    except Exception as e:
        print(f"lake build failed: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()


