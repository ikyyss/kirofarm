#!/usr/bin/env python3
"""Batch farm Kiro via Gmail plus/dot-addressing (portable, publishable).

Usage:
    py -3.13 kiro_batch.py <base_email> <start> <count> <prefix> [password]

Args:
    base_email  Email prefix WITHOUT the +tag and @gmail.com domain.
                Each account = f"{base_email}+{n}@gmail.com"
                (all plus-tags land in the same base inbox).
    start       First account number.
    count       How many accounts to farm.
    prefix      Account name prefix; name = f"{prefix}{n}".
    password    Password for all accounts. Falls back to env KIRO_PASSWORD.

Env:
    KIRO_PASSWORD  default password
"""
import subprocess, sys, time, os

HERE = os.path.dirname(os.path.abspath(__file__))

if len(sys.argv) < 5:
    print("usage: kiro_batch.py <base_email> <start> <count> <prefix> [password]")
    sys.exit(1)

BASE = sys.argv[1]
START = int(sys.argv[2])
COUNT = int(sys.argv[3])
PREFIX = sys.argv[4]
PASS = sys.argv[5] if len(sys.argv) > 5 else os.environ.get("KIRO_PASSWORD", "")
PK = os.path.join(HERE, "kiro_farm.py")

for i in range(START, START + COUNT):
    email = f"{BASE}+{i}@gmail.com"
    name = f"{PREFIX}{i}"
    print(f"\n=== {email} / {name} ===", flush=True)
    cmd = [sys.executable, PK, email, name]
    if PASS:
        cmd.append(PASS)
    try:
        p = subprocess.run(cmd, cwd=HERE, capture_output=True, text=True, timeout=360)
        print(p.stdout[-1500:], flush=True)
        if p.stderr:
            print(p.stderr[-300:], flush=True)
    except subprocess.TimeoutExpired:
        print("TIMEOUT", flush=True)
    time.sleep(2)

print("\n=== BATCH SELESAI ===", flush=True)
