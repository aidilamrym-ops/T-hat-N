#!/usr/bin/env python3
"""V1 frozen tool: flatten the captured claim HTML into readable text.

Deterministic (regex-based; no external deps). The output
captures/claim_anthropic_ecdsa_curve_origins.txt is itself a frozen capture;
this script documents its derivation (Replay Record spec, P8 replayability).
It is NOT used to extract comparison values (build_manifest.py does that).

Usage: tool_claim_text.py <in.html> <out.txt>
"""
import html
import pathlib
import re
import sys


def flatten(src: str) -> str:
    s = src
    s = re.sub(r"(?is)<script[^>]*>.*?</script>", "\n", s)
    s = re.sub(r"(?is)<style[^>]*>.*?</style>", "\n", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)<td[^>]*>", " | ", s)
    s = re.sub(r"(?i)</(p|div|li|tr|h[1-6]|pre|code|section|article|main|header|footer)>", "\n", s)
    s = re.sub(r"(?i)</(td|th)>", " |", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = html.unescape(s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = re.sub(r"[ \t]+\n", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s


def main() -> None:
    inp, outp = sys.argv[1], sys.argv[2]
    src = pathlib.Path(inp).read_text(encoding="utf-8", errors="replace")
    text = flatten(src)
    pathlib.Path(outp).write_text(text, encoding="utf-8", newline="\n")
    print(f"wrote {outp}: {len(text)} chars, {text.count(chr(10)) + 1} lines")


if __name__ == "__main__":
    main()


