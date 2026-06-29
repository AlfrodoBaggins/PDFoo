# PDFoo

Desktop PDF toolkit — merge, split, compress, rotate, PDF↔JPG. Built with Tauri v2 + Python FastAPI sidecar.

## Prerequisites

| Tool | Version | Notes |
|------|---------|-------|
| Rust | 1.80+ | `rustup` recommended |
| Node.js | 20+ | |
| Python | 3.11+ | |
| Ghostscript | 10.x | Required for compression (`gs` in PATH) |

### Platform system deps

**Linux (Debian/Ubuntu)**
```sh
sudo apt-get install -y \
  libwebkit2gtk-4.1-dev \
  build-essential \
  file \
  libssl-dev \
  libayatana-appindicator3-dev \
  librsvg2-dev \
  libjavascriptcoregtk-4.1-dev \
  libsoup-3.0-dev
```

**macOS** — Xcode Command Line Tools:
```sh
xcode-select --install
```

**Windows** — Microsoft Visual Studio C++ Build Tools ([download](https://visualstudio.microsoft.com/visual-cpp-build-tools/)) with "Desktop development with C++" workload.

## Quick start (development)

```sh
git clone https://github.com/AlfrodoBaggins/PDFoo.git
cd PDFoo

# Python backend
python3 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt

# Frontend
npm install

# Run both (Vite dev server + FastAPI)
npm run dev:all
```

Backend: http://127.0.0.1:8456 · Frontend: http://localhost:1420

## Build for production

### 1. Build the Python sidecar

```sh
source venv/bin/activate
python build_sidecar.py
```

This produces `src-tauri/binaries/pdfoo-server-{target-triple}`.

### 2. Build the Tauri app

```sh
npm run tauri:build
```

Platform-specific output:

| Platform | Bundle |
|----------|--------|
| Linux    | `src-tauri/target/release/bundle/deb/PDFoo_*_amd64.deb` |
| macOS    | `src-tauri/target/release/bundle/dmg/PDFoo_*.dmg` |
| Windows  | `src-tauri/target/release/bundle/nsis/PDFoo_*_x64-setup.exe` |

## CI builds

Pushing to `main` or tagging `v*` triggers GitHub Actions to build all platforms. Download artifacts from the Actions tab.
