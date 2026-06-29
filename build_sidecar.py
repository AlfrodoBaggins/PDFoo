#!/usr/bin/env python3
"""Build the Python sidecar binary using PyInstaller.

Usage:
    python build_sidecar.py

This produces a binary at src-tauri/binaries/pdfoo-server-{target-triple}
"""

import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC_TAURI = HERE / "src-tauri"
BINARIES = SRC_TAURI / "binaries"
BINARIES.mkdir(exist_ok=True)


def get_target_triple() -> str:
    try:
        return (
            subprocess.run(
                ["rustc", "--print", "host-tuple"],
                capture_output=True, text=True, check=True,
            )
            .stdout.strip()
        )
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Warning: rustc not found, using platform default.")
        import platform
        machine = platform.machine()
        if sys.platform == "linux":
            return f"{machine}-unknown-linux-gnu"
        elif sys.platform == "darwin":
            return f"{machine}-apple-darwin"
        elif sys.platform == "win32":
            return f"{machine}-pc-windows-msvc"
        return f"{machine}-unknown-linux-gnu"


def main():
    target = get_target_triple()
    print(f"Building sidecar for target: {target}")

    build_dir = HERE / "build_sidecar_temp"
    spec_path = build_dir / "pdfoo-server.spec"
    binary_name = "pdfoo-server"
    if sys.platform == "win32":
        binary_name += ".exe"

    # Clean previous build
    if build_dir.exists():
        shutil.rmtree(build_dir)
    build_dir.mkdir(parents=True)

    subprocess.run(
        [
            sys.executable, "-m", "PyInstaller",
            "--name", "pdfoo-server",
            "--onefile",
            "--distpath", str(build_dir / "dist"),
            "--workpath", str(build_dir / "build"),
            "--specpath", str(build_dir),
            "--hidden-import", "uvicorn.logging",
            "--hidden-import", "uvicorn.loops.auto",
            "--hidden-import", "uvicorn.protocols.http.auto",
            "app/main.py",
        ],
        cwd=str(HERE),
        check=True,
    )

    src = build_dir / "dist" / binary_name
    dest = BINARIES / f"pdfoo-server-{target}"

    shutil.copy2(str(src), str(dest))
    dest.chmod(0o755)
    print(f"Sidecar binary placed at: {dest}")

    # Cleanup
    shutil.rmtree(build_dir)
    print("Build temp files cleaned up.")


if __name__ == "__main__":
    main()
