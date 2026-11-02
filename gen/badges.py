"""Build the profile's stack badges as plain SVG files, so the README needs no badge service.

Each badge is shields.io flat-square in the palette, fetched once, with its logo
decoded from base64 into inline SVG so the files stay readable and diffable.
Order follows the `guy --stack` rows: devtools, agents, vision, inference, homelab, core, infra.
A tool with no shields.io logo gets a text-only badge.

Run: uv run --no-project python -I gen/badges.py assets/badges
"""

import base64
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

STEEL, SILVER, GREEN = "2e3642", "d1d7e0", "76b900"

STACK = [
    ("t3-code", "T3 Code", None), ("claude-code", "Claude Code", "claudecode"), ("codex", "Codex", None),
    ("cursor", "Cursor", "cursor"), ("devin", "Devin", None),
    ("pydantic-ai", "Pydantic AI", "pydantic"), ("dspy", "DSPy", None), ("mcp", "MCP", "modelcontextprotocol"),
    ("deepstream", "DeepStream", "nvidia"), ("jetson", "Jetson", "nvidia"),
    ("vllm", "vLLM", "vllm"), ("sglang", "SGLang", None), ("tensorrt-llm", "TensorRT-LLM", "nvidia"),
    ("hermes-agent", "Hermes Agent", None),  # shields' "hermes" logo is the parcel company (myhermes.de)
    ("home-assistant", "Home Assistant", "homeassistant"),
    ("python", "Python", "python"), ("rust", "Rust", "rust"), ("cpp", "C++", "cplusplus"),
    ("cuda", "CUDA", "nvidia"), ("pytorch", "PyTorch", "pytorch"),
    ("docker", "Docker", "docker"), ("terraform", "Terraform", "terraform"),
]


def shields(label: str, logo: str | None) -> str:
    text = urllib.parse.quote(label.replace("-", "--").replace("_", "__").replace(" ", "_"))
    query = {"style": "flat-square"}
    if logo:
        query |= {"logo": logo, "logoColor": GREEN if logo == "nvidia" else SILVER}
    url = f"https://img.shields.io/badge/{text}-{STEEL}?{urllib.parse.urlencode(query)}"
    request = urllib.request.Request(url, headers={"User-Agent": "guydada-profile-badges"})  # default UA gets 403
    with urllib.request.urlopen(request, timeout=20) as response:
        return response.read().decode()


def inline_logo(match: re.Match) -> str:
    x, y, w, h, data = match.groups()
    logo = re.sub(r"<title>.*?</title>", "", base64.b64decode(data).decode())
    return logo.replace("<svg ", f'<svg x="{x}" y="{y}" width="{w}" height="{h}" ', 1)


def main(out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for name, label, logo in STACK:
        svg = re.sub(r'<image x="([\d.]+)" y="([\d.]+)" width="([\d.]+)" height="([\d.]+)" '
                     r'href="data:image/svg\+xml;base64,([^"]+)"/>', inline_logo, shields(label, logo))
        (out / f"{name}.svg").write_text(svg)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
