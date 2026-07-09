from __future__ import annotations

import importlib.metadata
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"


def parse_pins(path: Path) -> list[tuple[str, str]]:
    pins: list[tuple[str, str]] = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "==" not in line:
            raise SystemExit(f"requirements must be pinned with ==: {line}")
        name, version = line.split("==", 1)
        pins.append((name.strip(), version.strip()))
    return pins


def main() -> int:
    failures: list[str] = []
    for name, expected in parse_pins(REQUIREMENTS):
        try:
            installed = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            failures.append(f"{name}: not installed (expected {expected})")
            continue
        if installed != expected:
            failures.append(f"{name}: expected {expected}, found {installed}")
    if failures:
        print("runtime dependency pin check failed:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print(f"runtime dependency pins satisfied ({len(parse_pins(REQUIREMENTS))} package(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
