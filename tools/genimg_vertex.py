#!/usr/bin/env python3
"""Fallback image generator using Vertex AI Imagen 4 (ADC, no API key).

Usage:
  source .venv/bin/activate
  python tools/genimg_vertex.py "prompt" --out path/file.png --aspect 16:9
"""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

try:
    from google import genai
except ImportError:
    print("source .venv/bin/activate && pip install google-genai", file=sys.stderr)
    sys.exit(1)

PROJECT = "pawconscious-mesh-2026"
LOCATION = "us-central1"
MODEL = "imagen-4.0-generate-001"  # also try imagen-4.0-fast-generate-001 for cheaper


def generate(prompt: str, out: Path, aspect: str = "16:9") -> None:
    client = genai.Client(vertexai=True, project=PROJECT, location=LOCATION)
    print(f"imagen-4 · aspect={aspect} · prompt len={len(prompt)}", file=sys.stderr)
    resp = client.models.generate_images(
        model=MODEL,
        prompt=prompt,
        config=dict(number_of_images=1, aspect_ratio=aspect),
    )
    if not resp.generated_images:
        print("no image returned", file=sys.stderr)
        sys.exit(1)
    img = resp.generated_images[0].image
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(img.image_bytes)
    print(f"wrote {out} ({out.stat().st_size:,} bytes)", file=sys.stderr)


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("prompt")
    p.add_argument("--out", required=True)
    p.add_argument("--aspect", default="16:9", choices=["1:1", "16:9", "9:16", "4:3", "3:4"])
    args = p.parse_args()
    generate(args.prompt, Path(args.out), args.aspect)


if __name__ == "__main__":
    main()
