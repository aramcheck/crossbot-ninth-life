"""Minimal dependency-free PEP 517/660 backend for this pure-Python package.

Editable installs expose src/ through a .pth; release wheels contain the modules.
There are no build-time dependencies beyond Python's standard library.
"""

import base64
import hashlib
import io
import zipfile
from pathlib import Path

NAME = "crossbot-0.1.0"
INFO = f"{NAME}.dist-info"
ROOT = Path(__file__).parent.resolve()


def _build(directory: str, editable: bool) -> str:
    filename = f"{NAME}-py3-none-any.whl"
    metadata = "Metadata-Version: 2.3\nName: crossbot\nVersion: 0.1.0\nRequires-Python: >=3.14\n"
    for requirement in (
        "pydantic>=2.13.4",
        "pydantic-settings>=2.15.0",
        "pyyaml>=6.0.3",
        "rich>=15.0.0",
    ):
        metadata += f"Requires-Dist: {requirement}\n"
    entries = {
        f"{INFO}/METADATA": metadata.encode(),
        f"{INFO}/WHEEL": b"Wheel-Version: 1.0\nGenerator: crossbot-stdlib\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        f"{INFO}/entry_points.txt": b"[console_scripts]\ncrossbot = crossbot.cli:main\nbenchmark = crossbot.benchmark:main\n",
    }
    if editable:
        entries["crossbot.pth"] = f"{ROOT / 'src'}\n".encode()
    else:
        entries.update(
            {
                str(p.relative_to(ROOT / "src")): p.read_bytes()
                for p in (ROOT / "src").rglob("*.py")
            }
        )
    record = io.StringIO()
    for name, content in entries.items():
        digest = (
            base64.urlsafe_b64encode(hashlib.sha256(content).digest())
            .rstrip(b"=")
            .decode()
        )
        record.write(f"{name},sha256={digest},{len(content)}\n")
    record.write(f"{INFO}/RECORD,,\n")
    entries[f"{INFO}/RECORD"] = record.getvalue().encode()
    with zipfile.ZipFile(
        Path(directory) / filename, "w", zipfile.ZIP_DEFLATED
    ) as wheel:
        for name, content in entries.items():
            wheel.writestr(name, content)
    return filename


def build_wheel(
    wheel_directory: str,
    config_settings: object = None,
    metadata_directory: str | None = None,
) -> str:
    return _build(wheel_directory, False)


def build_editable(
    wheel_directory: str,
    config_settings: object = None,
    metadata_directory: str | None = None,
) -> str:
    return _build(wheel_directory, True)
