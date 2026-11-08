# Kiro Farm (AWS Builder ID) — 9Router Injector

Automated farmer for [Kiro](https://kiro.dev) accounts via the AWS Builder ID OAuth flow. Injects active connections directly into [9Router](https://github.com/9router/9router) (`kiro` provider).

Uses **Camoufox** (anti-fingerprint headless Firefox engine) to bypass AWS bot detection (`ERR-837`).

---

## 📋 Step-by-Step Installation Guide

Follow the steps below in order.

### Step 1: Prepare a Gmail Account & App Password

The script reads OTP verification codes directly from the Gmail inbox automatically over IMAP.

1. **Enable 2-Step Verification (2FA)** on your Google account:
   - Open [Google Account Security](https://myaccount.google.com/security).
   - Make sure **2-Step Verification** is enabled.
2. **Create an App Password (Application Password)**:
   - Open [Google App Passwords](https://myaccount.google.com/apppasswords).
   - Give the app any name (e.g. `Himalaya CLI`).
   - Copy the generated 16-character code (format: `xxxx xxxx xxxx xxxx`). Save it.
3. **Enable IMAP Access**:
   - Open [Gmail](https://mail.google.com/) -> Gear icon (Settings) -> **See all settings**.
   - Go to the **Forwarding and POP/IMAP** tab.
   - Under **IMAP access**, select **Enable IMAP**.
   - Click **Save Changes** at the bottom.

---

### Step 2: Install & Set Up Himalaya CLI

Himalaya is a lightweight CLI for reading email via IMAP without a browser.

#### 1. Install Himalaya CLI
- **Windows** (via WinGet / PowerShell):
  ```powershell
  winget install pimalaya.himalaya
  ```
  *Or download the `.exe` binary from [Himalaya Releases](https://github.com/pimalaya/himalaya/releases) and add it to your system PATH.*
- **Linux / macOS**:
  ```bash
  # via brew
  brew install himalaya
  # or via cargo
  cargo install himalaya
  ```

#### 2. Create the Himalaya Config File
Create `config.toml` in:
- **Windows**: `C:\Users\<YourUsername>\.config\himalaya\config.toml`
- **Linux/macOS**: `~/.config/himalaya/config.toml`

Fill `config.toml` with the following template:
```toml
[accounts.gmail]
email = "youremail@gmail.com"
display-name = "youremail@gmail.com"
default = true

imap.server = "imaps://imap.gmail.com:993"
imap.sasl.plain.username = "youremail@gmail.com"
imap.sasl.plain.password.raw = "xxxx xxxx xxxx xxxx" # Replace with your 16-digit App Password

smtp.server = "smtp://smtp.gmail.com:587"
smtp.starttls = true
smtp.sasl.plain.username = "youremail@gmail.com"
smtp.sasl.plain.password.raw = "xxxx xxxx xxxx xxxx"

mailbox.alias.inbox = "INBOX"
```

#### 3. Test the Email Connection
Run in the terminal:
```bash
himalaya envelope list --account gmail --page-size 5
```
If your last 5 emails appear, the email integration works.

---

### Step 3: Set Up 9Router

1. Make sure **9Router** is installed and running in the background:
   - Default URL: `http://localhost:20128`
2. Make sure the `kiro` provider is active in the 9Router dashboard (`http://localhost:20128/dashboard/providers/kiro`).

---

### Step 4: Environment & Dependencies

1. **Clone the repository**:
   ```bash
   git clone https://github.com/ikyyss/kirofarm.git
   cd kirofarm
   ```
2. **Install Python 3.13** (or 3.11+).
3. **Install Camoufox**:
   ```bash
   pip install camoufox
   ```
4. **Download the Camoufox browser engine**:
   ```bash
   camoufox fetch
   ```

---

### Step 5: Run the Bot

All credentials (account name, email, password) can be set via command-line arguments without editing the script.

#### Option A: Farm a Single Account (`kiro_farm.py`)

Format:
```bash
python kiro_farm.py <email> <name> <password>
```
Example:
```bash
python kiro_farm.py "youremail+test1@gmail.com" "BudiSantoso" "PasswordKuat123@"
```

#### Option B: Automatic Batch Farming (`kiro_batch.py`)

Uses **Gmail Plus-Addressing** (`nameemail+tag@gmail.com`) so all verification emails land in a single shared inbox.

Format:
```bash
python kiro_batch.py <base_email> <start_number> <account_count> <name_prefix> <password>
```
*Parameters:*
- `base_email`: Your Gmail username before `@gmail.com`.
- `start_number`: The starting account number (e.g. 1).
- `account_count`: The number of accounts to create (e.g. 5).
- `name_prefix`: The AWS display-name prefix (e.g. `User`).
- `password`: The password to use for all accounts.

Example:
```bash
python kiro_batch.py "youremail" 1 5 "Kibo" "PasswordKuat123@"
```
*The command above automatically creates:*
- `youremail+1@gmail.com` with name `Kibo1`
- `youremail+2@gmail.com` with name `Kibo2`
- ... and so on until 5 accounts are created.

---

## 📁 Output

Every account that is successfully registered and passes consent verification is automatically written to:
`akun_full.txt`

Format:
```text
email:password:
```

`akun_full.txt` is already in `.gitignore` so credentials never leak into the git repository.

---

## ⚙️ Environment Variables (Optional)

| Variable | Default | Description |
|---|---|---|
| `KIRO_9ROUTER` | `http://localhost:20128` | 9Router API URL if hosted on another port/machine |
| `KIRO_PASSWORD` | — | Fallback password if not passed as a CLI argument |
| `KIRO_OUT` | `./akun_full.txt` | Output file location for saved accounts |

---

## ⚠️ Troubleshooting & Important Notes

- **Error `FATAL no otp`**:
  - Make sure `himalaya envelope list --account gmail` can show the inbox.
  - If AWS doesn't send a verification email, the base email may be temporarily rate-limited by AWS. Try a different base Gmail address.
- **AWS page renders slowly**:
  - The script auto-retries reloading up to 3 times if the email field appears slowly.
- **Detecting 9Router success**:
  - 9Router names connections incrementally (`Account 1`, `Account 2`, etc.), not by email address. The script detects success by the increase in total Kiro connections in 9Router.
