#!/usr/bin/env python3
"""Generate UI imagery via gpt-image-1 per Omar's image-gen priority (memory: feedback-image-gen-models).

Usage:
  export OPENAI_API_KEY=$(grep OPENAI_API_KEY ~/.zshrc | cut -d= -f2)
  python tools/genimg.py "prompt text" --out services/mesh_api/static/assets/foo.png --size 1536x1024

Sizes: 1024x1024 (square) | 1536x1024 (wide) | 1024x1536 (tall)
"""
from __future__ import annotations

import argparse
import base64
import os
import sys
from pathlib import Path

try:
    from openai import OpenAI
except ImportError:
    print("pip install openai", file=sys.stderr)
    sys.exit(1)


def generate(prompt: str, out_path: Path, size: str = "1536x1024", quality: str = "high") -> None:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    client = OpenAI(api_key=api_key)
    print(f"generating {size} @ quality={quality}...", file=sys.stderr)
    resp = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size=size,
        quality=quality,
        n=1,
    )
    b64 = resp.data[0].b64_json
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(base64.b64decode(b64))
    print(f"wrote {out_path} ({out_path.stat().st_size:,} bytes)", file=sys.stderr)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="image prompt")
    parser.add_argument("--out", required=True, help="output path (png)")
    parser.add_argument("--size", default="1536x1024", choices=["1024x1024", "1536x1024", "1024x1536"])
    parser.add_argument("--quality", default="high", choices=["low", "medium", "high"])
    args = parser.parse_args()
    generate(args.prompt, Path(args.out), args.size, args.quality)


if __name__ == "__main__":
    main()
