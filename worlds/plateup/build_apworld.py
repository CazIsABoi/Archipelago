"""
Build plateup.apworld with compatible_version injected, matching the official Archipelago build process.
Run from the Archipelago repo root: python worlds/plateup/build_apworld.py
"""
import json
import os
import pathlib
import zipfile

WORLD_DIR = pathlib.Path(__file__).parent
WORLD_NAME = WORLD_DIR.name  # "plateup"
OUTPUT_PATH = WORLD_DIR.parent.parent / "build" / "apworlds" / f"{WORLD_NAME}.apworld"

MANIFEST_INJECT = {
    "compatible_version": 7,
}

SKIP_DIRS = {"__pycache__", ".venv", ".vscode", "test", ".git"}


def build():
    os.makedirs(OUTPUT_PATH.parent, exist_ok=True)

    # Load source manifest
    source_manifest_path = WORLD_DIR / "archipelago.json"
    with source_manifest_path.open("r", encoding="utf-8") as f:
        manifest = json.load(f)

    # Inject fields that the official build tool adds
    manifest.update(MANIFEST_INJECT)

    manifest_zip_path = f"{WORLD_NAME}/archipelago.json"

    with zipfile.ZipFile(OUTPUT_PATH, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for path in WORLD_DIR.rglob("*.*"):
            # Skip unwanted directories
            if any(part in SKIP_DIRS for part in path.parts):
                continue
            if path.suffix in {".pyc"}:
                continue
            if path.name == "archipelago.json":
                continue  # we write the injected version below
            relative_path = f"{WORLD_NAME}/{path.relative_to(WORLD_DIR)}"
            zf.write(path, relative_path)

        # Write injected manifest
        zf.writestr(manifest_zip_path, json.dumps(manifest, indent=4))

    print(f"Built: {OUTPUT_PATH}")


if __name__ == "__main__":
    build()
