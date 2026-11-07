#!/usr/bin/env python3
"""Farm Kiro/AWS Builder ID accounts (portable, publishable).

Usage:
    py -3.13 kiro_farm.py <email> <nama> [password]

Args:
    email      AWS Builder ID signup email (e.g. something+tag@gmail.com)
    nama       Display name shown on AWS profile
    password   Account password. If omitted, falls back to env KIRO_PASSWORD.

Env:
    KIRO_9ROUTER   9Router base URL (default http://localhost:20128)
    KIRO_PASSWORD   default password when arg 3 omitted
    KIRO_OUT        funnel output file (default ./akun_full.txt)

Reads the OTP from Gmail via himalaya. Validates by polling the 9Router
API until a kiro connection count increases (success signal).
"""
import sys, time, re, subprocess, urllib.request, json, pathlib, os

EMAIL = sys.argv[1]
NAME = sys.argv[2]
PASSWORD = sys.argv[3] if len(sys.argv) > 3 else os.environ.get("KIRO_PASSWORD", "")
if not PASSWORD:
    print("FATAL no password (argv[3] or KIRO_PASSWORD)"); sys.exit(1)

BASE = os.environ.get("KIRO_9ROUTER", "http://localhost:20128").rstrip("/")
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = pathlib.Path(os.environ.get("KIRO_OUT", os.path.join(HERE, "akun_full.txt")))


def api_connections():
    try:
        with urllib.request.urlopen(BASE + "/api/providers", timeout=10) as r:
            return json.loads(r.read()).get("connections", [])
    except Exception:
        return []


def get_otp():
    for _ in range(20):
        try:
            out = subprocess.run(["himalaya", "envelope", "list", "--account", "gmail",
                                  "--page-size", "5"], capture_output=True, text=True).stdout
            ids = []
            for ln in out.split("\n"):
                if "Verify your AWS Builder ID" in ln:
                    m = re.match(r"^\D*(\d+)", ln)
                    if m:
                        ids.append(m.group(1))
            if ids:
                msg = subprocess.run(["himalaya", "message", "read", "--account", "gmail",
                                      ids[0]], capture_output=True, text=True).stdout
                codes = re.findall(r"\b\d{6}\b", msg)
                if codes:
                    return codes[0]
        except Exception:
            pass
        time.sleep(6)
    return None


from camoufox.sync_api import Camoufox

print(f"FARM {EMAIL} / {NAME}", flush=True)

with Camoufox(headless=True) as fox:
    page = fox.new_page()
    # 1. 9Router: Add -> AWS Builder ID
    page.goto(BASE + "/dashboard/providers/kiro", timeout=30000, wait_until="domcontentloaded")
    time.sleep(4)
    page.locator('button:has-text("Add")').first.click()
    time.sleep(2)
    page.locator('h3:has-text("AWS Builder ID")').locator("xpath=ancestor::button[1]").click()
    code = None
    for _ in range(15):
        time.sleep(1)
        body = page.inner_text("body")
        m = re.search(r'view\.awsapps\.com/start/#/device\?user_code=(\S+)', body)
        if m:
            code = m.group(1); break
    if not code:
        print("FATAL no device code"); sys.exit(1)
    print("CODE", code, flush=True)

    # 2. device login -> email -> name
    p2 = fox.new_page()
    p2.goto(f"https://view.awsapps.com/start/#/device?user_code={code}",
            timeout=60000, wait_until="domcontentloaded")
    time.sleep(5)
    # heavy page render - retry navigation up to 3x if email field lags
    for attempt in range(3):
        try:
            p2.locator('input[type="email"]').wait_for(state="visible", timeout=25000)
            break
        except Exception:
            if attempt == 2:
                raise
            print("email field not shown, reloading...", flush=True)
            p2.goto(f"https://view.awsapps.com/start/#/device?user_code={code}",
                    timeout=60000, wait_until="domcontentloaded")
            time.sleep(8)
    p2.fill('input[type="email"]', EMAIL)
    p2.locator('button:has-text("Continue")').first.click()
    time.sleep(6)
    p2.locator('input[type="text"]').wait_for(state="visible", timeout=20000)
    p2.fill('input[type="text"]', NAME)
    p2.locator('button:has-text("Continue")').first.click()
    time.sleep(6)

    # 3. OTP
    otp = get_otp()
    if not otp:
        print("FATAL no otp"); sys.exit(1)
    print("OTP", otp, flush=True)
    p2.locator('input[placeholder="6-digit"]').wait_for(state="visible", timeout=15000)
    p2.fill('input[placeholder="6-digit"]', otp)
    p2.locator('button:has-text("Continue")').first.click()
    time.sleep(6)

    # 4. cookie banner
    try:
        p2.locator('button:has-text("Accept")').first.click(timeout=5000)
        time.sleep(2)
    except Exception:
        pass

    # 5. password (two fields: password + confirm)
    pws = p2.locator('input[type="password"]')
    pws.nth(0).wait_for(state="visible", timeout=15000)
    pws.nth(0).fill(PASSWORD)
    if pws.count() >= 2:
        pws.nth(1).fill(PASSWORD)
    time.sleep(1)
    p2.locator('button:has-text("Continue")').first.click()
    time.sleep(6)
    try:
        p2.locator('button:has-text("Accept")').first.click(timeout=4000)
        time.sleep(2)
    except Exception:
        pass

    # baseline kiro connection count
    base_count = len([c for c in api_connections() if c.get("provider") == "kiro"])

    # 6. consent loop until connection appears
    def click_consent():
        for label in ["Allow access", "Allow", "Authorize", "Confirm and continue"]:
            try:
                b = p2.locator(f'button:has-text("{label}")')
                if b.count():
                    b.first.click(timeout=3000)
                    time.sleep(3)
                    return True
            except Exception:
                continue
        return False

    t0 = time.time()
    done = False
    while time.time() - t0 < 90:
        n_now = len([c for c in api_connections() if c.get("provider") == "kiro"])
        if n_now > base_count:
            done = True
            break
        click_consent()
        time.sleep(2)

    if done:
        with OUT.open("a") as f:
            f.write(f"{EMAIL}:{PASSWORD}:\n")
        print(f"SUCCESS {EMAIL} (funneled to {OUT})", flush=True)
    else:
        tot = len([c for c in api_connections() if c.get("provider") == "kiro"])
        print(f"FAIL no connection after {int(time.time()-t0)}s; kiro total={tot}", flush=True)
        print("FINAL URL:", p2.url, flush=True)
        print("FINAL TEXT:", p2.evaluate("document.body.innerText.slice(0,300)"), flush=True)
