#!/usr/bin/env python3
"""Validate all skin YAML files against the Hermes skin schema."""

import re
import sys
from pathlib import Path

import yaml

SKINS_DIR = Path(__file__).parent / "skins"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"

REQUIRED_COLORS = [
    "banner_border", "banner_title", "banner_accent", "banner_dim", "banner_text",
    "ui_accent", "ui_label", "ui_ok", "ui_error", "ui_warn",
    "prompt", "input_rule", "response_border", "session_label", "session_border",
]
REQUIRED_SPINNER = ["waiting_faces", "thinking_faces", "thinking_verbs", "wings"]
REQUIRED_BRANDING = ["agent_name", "welcome", "goodbye", "response_label", "prompt_symbol", "help_header"]
HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")

errors = []


def err(skin, msg):
    errors.append(f"  [{skin}] {msg}")


for skin_file in sorted(SKINS_DIR.glob("*.yaml")):
    skin_name = skin_file.stem

    try:
        data = yaml.safe_load(skin_file.read_text())
    except yaml.YAMLError as e:
        err(skin_name, f"YAML parse error: {e}")
        continue

    # name matches filename
    if data.get("name") != skin_name:
        err(skin_name, f"name: '{data.get('name')}' does not match filename '{skin_name}'")

    # colors
    colors = data.get("colors", {})
    for key in REQUIRED_COLORS:
        if key not in colors:
            err(skin_name, f"missing color key: {key}")
        elif not HEX_RE.match(str(colors[key])):
            err(skin_name, f"color '{key}' is not a valid #RRGGBB hex: {colors[key]}")

    # spinner
    spinner = data.get("spinner", {})
    for key in REQUIRED_SPINNER:
        if key not in spinner:
            err(skin_name, f"missing spinner key: {key}")
        elif not isinstance(spinner[key], list) or len(spinner[key]) == 0:
            err(skin_name, f"spinner.{key} must be a non-empty list")

    # branding
    branding = data.get("branding", {})
    for key in REQUIRED_BRANDING:
        if key not in branding:
            err(skin_name, f"missing branding key: {key}")

    # banner_logo and banner_hero
    for field in ("banner_logo", "banner_hero"):
        if field not in data:
            err(skin_name, f"missing field: {field}")

    # screenshot exists
    if not (SCREENSHOTS_DIR / f"{skin_name}.png").exists():
        err(skin_name, f"missing screenshot: screenshots/{skin_name}.png")


if errors:
    print(f"FAILED — {len(errors)} error(s):\n")
    for e in errors:
        print(e)
    sys.exit(1)

skin_count = len(list(SKINS_DIR.glob("*.yaml")))
print(f"OK — {skin_count} skin(s) valid")
