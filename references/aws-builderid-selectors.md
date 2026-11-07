# AWS Builder ID signup — validated flow quirks

Worked via Camoufox headless. All selectors verified by debugging a real run.

## Device-code page
- Device URL: `https://view.awsapps.com/start/#/device?user_code=XXXX-XXXX`.
- The `input[type="email"]` field renders slowly; often missing on first load.
  Retry full navigation reload up to 3x, wait up to 25s each.
- After Continue: `input[type="text"]` for name (placeholder contains "Maria").
  Wait for visible before fill.

## OTP page
- OTP input selector: `input[placeholder="6-digit"]`.
- Cookie banner: `button:has-text("Accept")` appears after OTP — click it before
  password form.

## Password
- TWO password fields: `input[type="password"]` (placeholder "Enter password" and
  "Re-enter password"). Use `.nth(0)` / `.nth(1)` — a bare locator hits strict-mode
  violation.
- Submit via `button:has-text("Continue")`.

## Consent sequence (kiro-oauth-client)
- First screen: `Allow kiro-oauth-client to access your data?` — click `Allow access`
  (NOT generic Continue; Continue on this screen does nothing and the loop exits early).
- Possibly followed by `Confirm and continue`.
- Loop clicking allow/confirm buttons until the kiro connection count increases
  (success signal).

## Success signal
- 9Router verifies out; success = kiro connection count increases. Then append
  `EMAIL:PASSWORD:` to `akun_full.txt`.
