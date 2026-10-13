#!/usr/bin/env python3
"""Static readiness probe for the Supabase AEON_NXT_CORE replication target.

Purpose: decide, without trusting anything, whether the binary evolution
ledger (ledger/msaf_ledger.jsonl) can be replicated to cloud storage. The
probe performs layered static checks from the outside in and stops at the
first failing layer with a loud, attributable verdict. Exit codes:

    0  READY: endpoint reachable, authenticated, ledger_blocks table present
    1  NOT READY: a concrete layer failed (reason printed, remediation given)
    2  MISCONFIGURED: credentials absent or malformed; nothing was attempted

No credentials are stored anywhere. SUPABASE_URL and SUPABASE_SERVICE_KEY are
read from the environment at runtime only. Without them the probe refuses to
run rather than simulating a connection.

Replication contract (executed only when READY): each ledger line becomes one
row keyed by (ledger, index); every ball serialises as its existing decimal
STRING (radii included); no float conversion at any stage. Provision with:

    create table ledger_blocks (
      ledger text not null,
      index integer not null,
      generation integer not null,
      genome_id text not null,
      decision text not null,
      fitness_total text not null,
      certificate_bits text not null,
      spectral_agreement_bits text not null,
      previous_hash text not null,
      record_hash text not null,
      primary key (ledger, index)
    );
"""

from __future__ import annotations

import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request

TIMEOUT_SECONDS = 10


def fail(reason: str, remediation: str, code: int = 1) -> int:
    print(f"NOT READY: {reason}")
    print(f"REMEDIATION: {remediation}")
    return code


def check_configuration() -> tuple[str, str] | int:
    """Layer 0: credentials present and URL well-formed. No network touched."""
    url = os.environ.get("SUPABASE_URL", "")
    key = os.environ.get("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        print("MISCONFIGURED: SUPABASE_URL and SUPABASE_SERVICE_KEY are required "
              "in the environment; refusing to simulate a connection")
        return 2
    parts = urllib.parse.urlparse(url)
    if parts.scheme != "https" or not parts.hostname:
        return fail(f"malformed SUPABASE_URL: {url!r}",
                    "set SUPABASE_URL to https://<project>.supabase.co")
    return url, key


def check_dns(hostname: str) -> int | None:
    """Layer 1: the host must resolve. Returns None on success."""
    try:
        socket.getaddrinfo(hostname, 443, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return fail(f"DNS resolution failed for {hostname}: {exc}",
                    "check the project reference and network egress")
    return None


def check_tcp(hostname: str) -> int | None:
    """Layer 2: TCP/443 must accept. Returns None on success."""
    try:
        with socket.create_connection((hostname, 443), timeout=TIMEOUT_SECONDS):
            pass
    except OSError as exc:
        return fail(f"TCP connect to {hostname}:443 failed: {exc}",
                    "check firewall egress and Supabase project status")
    return None


def check_rest(url: str, key: str) -> int | None:
    """Layer 3: PostgREST answers with valid authentication. Returns None."""
    request = urllib.request.Request(
        url.rstrip("/") + "/rest/v1/",
        headers={"apikey": key, "Authorization": f"Bearer {key}"},
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            response.read(0)
    except urllib.error.HTTPError as exc:
        if exc.code in (401, 403):
            return fail(f"PostgREST rejected credentials (HTTP {exc.code})",
                        "rotate SUPABASE_SERVICE_KEY; verify project pairing")
        return fail(f"PostgREST unexpected HTTP {exc.code}",
                    "inspect Supabase project logs")
    except OSError as exc:
        return fail(f"TLS/HTTP layer failed: {exc}",
                    "check TLS interception and proxy settings")
    return None


def check_ledger_table(url: str, key: str) -> int | None:
    """Layer 4: the ledger_blocks table must exist and be readable."""
    endpoint = url.rstrip("/") + "/rest/v1/ledger_blocks?select=index&limit=1"
    request = urllib.request.Request(
        endpoint, headers={"apikey": key, "Authorization": f"Bearer {key}"}
    )
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        return fail(f"ledger_blocks query failed (HTTP {exc.code})",
                    "provision the table with the DDL printed in this module docstring")
    except (OSError, ValueError) as exc:
        return fail(f"ledger_blocks unreadable: {exc}",
                    "verify RLS policies grant service_role select")
    if not isinstance(payload, list):
        return fail(f"ledger_blocks returned non-array payload: {payload!r}",
                    "verify the table was not replaced by a view")
    print(f"READY: AEON_NXT_CORE reachable, authenticated, ledger_blocks readable "
          f"({len(payload)} sample row(s))")
    return None


def main() -> int:
    configured = check_configuration()
    if isinstance(configured, int):
        return configured
    url, key = configured
    hostname = urllib.parse.urlparse(url).hostname or ""
    for layer in (lambda: check_dns(hostname),
                  lambda: check_tcp(hostname),
                  lambda: check_rest(url, key),
                  lambda: check_ledger_table(url, key)):
        verdict = layer()
        if verdict is not None:
            return verdict
    _ = ssl.PROTOCOL_TLS_CLIENT  # hard dependency marker: TLS-only transport
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
