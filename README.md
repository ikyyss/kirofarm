# Kiro Farm (AWS Builder ID) — 9Router Injector

Automated farmer for [Kiro](https://kiro.dev) accounts via the AWS Builder ID OAuth flow. Injects active connections directly into [9Router](https://github.com/9router/9router) (`kiro` provider).

Uses **Camoufox** (anti-fingerprint headless Firefox engine) to bypass AWS bot detection (`ERR-837`).

---

## 📋 Step-by-Step Installation Guide

Ikuti langkah-langkah di bawah ini secara berurutan:

### Langkah 1: Persiapan Akun Gmail & App Password

Script ini membaca kode verifikasi OTP langsung dari inbox Gmail secara otomatis melalui IMAP.

1. **Aktifkan 2-Step Verification (2FA)** di akun Google Anda:
   - Buka [Google Account Security](https://myaccount.google.com/security).
   - Pastikan **2-Step Verification** sudah aktif.
2. **Buat App Password (Password Aplikasi)**:
   - Buka [Google App Passwords](https://myaccount.google.com/apppasswords).
   - Beri nama aplikasi sembarang (misal: `Himalaya CLI`).
   - Salin 16 karakter kode yang dihasilkan (format: `xxxx xxxx xxxx xxxx`). Simpan kode ini.
3. **Aktifkan Akses IMAP**:
   - Buka [Gmail](https://mail.google.com/) -> Ikon Gerigi (Settings) -> **See all settings**.
   - Masuk ke tab **Forwarding and POP/IMAP**.
   - Pada bagian **IMAP access**, pilih **Enable IMAP**.
   - Klik **Save Changes** di bagian bawah.

---

### Langkah 2: Install & Setup Himalaya CLI

Himalaya adalah CLI ringan untuk membaca email via IMAP tanpa browser.

#### 1. Install Himalaya CLI
- **Windows** (via WinGet / PowerShell):
  ```powershell
  winget install pimalaya.himalaya
  ```
  *Atau download binary `.exe` dari [Himalaya Releases](https://github.com/pimalaya/himalaya/releases) lalu masukkan ke PATH sistem Anda.*
- **Linux / macOS**:
  ```bash
  # via brew
  brew install himalaya
  # atau via cargo
  cargo install himalaya
  ```

#### 2. Buat File Konfigurasi Himalaya
Buat file `config.toml` pada direktori:
- **Windows**: `C:\Users\<UsernameAnda>\.config\himalaya\config.toml`
- **Linux/macOS**: `~/.config/himalaya/config.toml`

Isi file `config.toml` dengan template berikut:
```toml
[accounts.gmail]
email = "emailanda@gmail.com"
display-name = "emailanda@gmail.com"
default = true

imap.server = "imaps://imap.gmail.com:993"
imap.sasl.plain.username = "emailanda@gmail.com"
imap.sasl.plain.password.raw = "xxxx xxxx xxxx xxxx" # Ganti dengan 16 digit App Password Anda

smtp.server = "smtp://smtp.gmail.com:587"
smtp.starttls = true
smtp.sasl.plain.username = "emailanda@gmail.com"
smtp.sasl.plain.password.raw = "xxxx xxxx xxxx xxxx"

mailbox.alias.inbox = "INBOX"
```

#### 3. Tes Koneksi Email
Jalankan di terminal:
```bash
himalaya envelope list --account gmail --page-size 5
```
Jika muncul daftar 5 email terakhir di inbox Anda, integrasi email berhasil!

---

### Langkah 3: Setup 9Router

1. Pastikan **9Router** sudah terpasang dan sedang berjalan di background:
   - URL default: `http://localhost:20128`
2. Pastikan provider `kiro` aktif di dashboard 9Router (`http://localhost:20128/dashboard/providers/kiro`).

---

### Langkah 4: Setup Environment & Dependencies

1. **Clone Repository**:
   ```bash
   git clone <URL_REPO_GITHUB_ANDA>
   cd kirofarm
   ```
2. **Install Python 3.13** (atau 3.11+).
3. **Install Camoufox**:
   ```bash
   pip install camoufox
   ```
4. **Download Browser Engine Camoufox**:
   ```bash
   camoufox fetch
   ```

---

### Langkah 5: Menjalankan Bot

Semua kredensial (nama akun, email, password) dapat disesuaikan lewat command line argumen tanpa perlu edit script.

#### Opsi A: Farming 1 Akun Tunggal (`kiro_farm.py`)

Format:
```bash
python kiro_farm.py <email> <nama> <password>
```
Contoh:
```bash
python kiro_farm.py "emailanda+tes1@gmail.com" "BudiSantoso" "PasswordKuat123@"
```

#### Opsi B: Farming Batch Otomatis (`kiro_batch.py`)

Menggunakan fitur **Gmail Plus-Addressing** (`namaemail+tag@gmail.com`) agar semua email verifikasi masuk ke satu inbox yang sama.

Format:
```bash
python kiro_batch.py <base_email> <angka_mulai> <jumlah_akun> <prefix_nama> <password>
```
*Parameter:*
- `base_email`: Username Gmail Anda sebelum `@gmail.com`.
- `angka_mulai`: Nomor awal akun (misal: 1).
- `jumlah_akun`: Jumlah akun yang ingin dibuat (misal: 5).
- `prefix_nama`: Awalan display name AWS (misal: `User`).
- `password`: Password yang diinginkan untuk semua akun.

Contoh:
```bash
python kiro_batch.py "emailanda" 1 5 "Kibo" "PasswordKuat123@"
```
*Perintah di atas akan otomatis membuat:*
- `emailanda+1@gmail.com` dengan nama `Kibo1`
- `emailanda+2@gmail.com` dengan nama `Kibo2`
- ... dan seterusnya sampai 5 akun selesai dibuat.

---

## 📁 Hasil Output

Setiap akun yang sukses terdaftar dan lolos verifikasi consent akan otomatis tercatat di:
`akun_full.txt`

Format:
```text
email:password:
```

File `akun_full.txt` sudah dimasukkan ke `.gitignore` agar kredensial tidak pernah bocor ke repository git.

---

## ⚙️ Environment Variables (Opsional)

| Variabel | Default | Keterangan |
|---|---|---|
| `KIRO_9ROUTER` | `http://localhost:20128` | URL API 9Router jika di-host di port/mesin lain |
| `KIRO_PASSWORD` | — | Fallback password jika tidak ditulis di argumen CLI |
| `KIRO_OUT` | `./akun_full.txt` | Lokasi file output penyimpanan akun |

---

## ⚠️ Troubleshooting & Catatan Penting

- **Error `FATAL no otp`**:
  - Pastikan perintah `himalaya envelope list --account gmail` bisa menampilkan inbox.
  - Jika AWS tidak mengirim email verifikasi, kemungkinan base email terkena temporary rate-limit oleh AWS. Coba ganti base email Gmail baru.
- **Halaman AWS Lambat Render**:
  - Script sudah dilengkapi auto-retry reload hingga 3x jika input field email lambat muncul.
- **Deteksi Sukses 9Router**:
  - 9Router memberi nama koneksi secara increment (`Account 1`, `Account 2`, dst), bukan memakai alamat email. Script mendeteksi keberhasilan berdasarkan kenaikan total koneksi Kiro di 9Router.
