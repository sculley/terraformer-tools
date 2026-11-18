"""Packs both folders into dist/Terraformer_Tools.mcaddon.

Run from anywhere:  python3 tools/build.py
"""
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "dist" / "Terraformer_Tools.mcaddon"
PACKS = ["Terraformer_Tools_BP", "Terraformer_Tools_RP"]


def main():
    OUT.parent.mkdir(exist_ok=True)
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        for pack in PACKS:
            for f in sorted((ROOT / pack).rglob("*")):
                if f.is_file() and f.name != ".DS_Store":
                    z.write(f, f.relative_to(ROOT).as_posix())
    print(f"Built {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
