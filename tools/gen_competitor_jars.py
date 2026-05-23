#!/usr/bin/env python3
"""Generate two mock-brand competitor jars for /demo scene 2 via gpt-image-1.

Output:
  services/mesh_api/static/assets/wellpaw-hip-joint.png
  services/mesh_api/static/assets/goldenpaw-hip-joint.png

Both jars match the visual style of the existing Native Pet warm jar so the
LLM-style product compare row in scene 2 reads as a real shopping result with
visual parity. Brands are fictional. Labels are baked into the image.

Run: python tools/gen_competitor_jars.py
Requires: OPENAI_API_KEY in env.
"""
import base64
import os
import sys
from pathlib import Path
from openai import OpenAI

ASSETS = Path(__file__).resolve().parent.parent / "services" / "mesh_api" / "static" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

client = OpenAI()

PROMPTS = {
    "wellpaw-hip-joint.png": (
        "Studio product photograph of a pet supplement jar on a soft cream background. "
        "Amber-brown matte glass jar with rounded shoulders, dark brown lid. "
        "Clean modern minimal label with sage-green and cream color palette, "
        "title 'WELLPAW' in bold sans-serif at the top center, "
        "subtitle 'Hip + Joint Mobility' below, "
        "bottom of label reads 'FOR ALL DOGS / 90 SOFT CHEWS'. "
        "Warm directional natural light, soft shadow under the jar, square format, "
        "centered composition, premium DTC pet wellness brand aesthetic, "
        "no real brand names visible, no logos other than the WELLPAW wordmark."
    ),
    "goldenpaw-hip-joint.png": (
        "Studio product photograph of a pet supplement jar on a soft cream background. "
        "Off-white ceramic-look jar with rounded shoulders, warm terracotta lid. "
        "Clean modern label with terracotta and warm-cream color palette, "
        "title 'GOLDENPAW' in elegant serif at the top center, "
        "subtitle 'Joint Care Complex' below, "
        "bottom of label reads 'SENIOR DOGS / 120 SOFT CHEWS'. "
        "Warm directional natural light, soft shadow under the jar, square format, "
        "centered composition, premium DTC pet wellness brand aesthetic, "
        "no real brand names visible, no logos other than the GOLDENPAW wordmark."
    ),
}


def gen(filename: str, prompt: str) -> None:
    out = ASSETS / filename
    print(f"[gen] {filename} ...")
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        n=1,
    )
    b64 = resp.data[0].b64_json
    out.write_bytes(base64.b64decode(b64))
    print(f"[ok]  {out} ({out.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    for name, prompt in PROMPTS.items():
        gen(name, prompt)
    print("done.")
