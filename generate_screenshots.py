#!/usr/bin/env python3
"""Generate screenshot PNGs for each skin in the hermes-skins repo.

Renders each skin's banner as ANSI → HTML → PNG via Chromium for authentic
terminal-quality screenshots.
"""

import sys
import os
import io

HERMES_AGENT_DIR = os.path.expanduser("~/projects/hermes-agent")
sys.path.insert(0, HERMES_AGENT_DIR)

from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
from ansi2html import Ansi2HTMLConverter
from html2image import Html2Image
from PIL import Image
import yaml

SKINS_DIR = Path(__file__).parent / "skins"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

from hermes_cli.skin_engine import _build_skin_config, load_skin


def get_skin_colors(skin):
    return {
        "accent": skin.get_color("banner_accent", "#FFBF00"),
        "dim": skin.get_color("banner_dim", "#B8860B"),
        "text": skin.get_color("banner_text", "#FFF8DC"),
        "label": skin.get_color("ui_label", "#4dd0e1"),
        "warn": skin.get_color("ui_warn", "#ffa726"),
        "error": skin.get_color("ui_error", "#ef5350"),
        "session_color": skin.get_color("session_border", "#8B8682"),
        "title_color": skin.get_color("banner_title", "#FFD700"),
        "border_color": skin.get_color("banner_border", "#CD7F32"),
    }


def render_banner_ansi(skin_name, skin_path=None):
    """Render a skin's banner and return raw ANSI string."""
    if skin_path:
        with open(skin_path) as f:
            skin_data = yaml.safe_load(f)
        skin = _build_skin_config(skin_data)
    else:
        skin = load_skin(skin_name)

    c = get_skin_colors(skin)
    agent_name = skin.get_branding("agent_name", "Hermes Agent")

    hero = ""
    if hasattr(skin, 'banner_hero') and skin.banner_hero:
        hero = skin.banner_hero
    else:
        from hermes_cli.banner import HERMES_CADUCEUS
        hero = HERMES_CADUCEUS

    logo = ""
    if hasattr(skin, 'banner_logo') and skin.banner_logo:
        logo = skin.banner_logo
    else:
        from hermes_cli.banner import HERMES_AGENT_LOGO
        logo = HERMES_AGENT_LOGO

    # Use a string buffer to capture ANSI output
    buf = io.StringIO()
    console = Console(file=buf, width=120, force_terminal=True, color_system="truecolor")

    console.print()
    console.print(Align.center(logo))
    console.print()

    layout_table = Table.grid(padding=(0, 2))
    layout_table.add_column("left", justify="center")
    layout_table.add_column("right", justify="left")

    left_lines = ["", hero, ""]
    left_lines.append(
        f"[{c['accent']}]claude-opus-4-6[/] [{c['dim']}]·[/] "
        f"[{c['dim']}]200K context[/] [{c['dim']}]·[/] [{c['dim']}]Nous Research[/]"
    )
    left_lines.append(f"[dim {c['dim']}]~/projects[/]")
    left_lines.append(f"[dim {c['session_color']}]Session: a1b2c3d4[/]")
    left_content = "\n".join(left_lines)

    accent, dim, text, label = c['accent'], c['dim'], c['text'], c['label']

    right_lines = [f"[bold {accent}]Available Tools[/]"]
    mock_toolsets = {
        "browser": ["browser_click", "browser_navigate", "browser_snapshot"],
        "file": ["patch", "read_file", "search_files", "write_file"],
        "hermes-cli": ["memory", "session_search", "skill_manage", "todo"],
        "terminal": ["execute_code", "process", "terminal"],
    }
    for toolset, tools in sorted(mock_toolsets.items()):
        colored = [f"[{text}]{t}[/]" for t in tools]
        tools_str = f"[{dim}], [/]".join(colored)
        right_lines.append(f"[dim {dim}]{toolset}:[/] {tools_str}")

    right_lines.append("")
    right_lines.append(f"[bold {accent}]Available Skills[/]")
    right_lines.append(f"[dim {dim}]devops:[/] [{text}]webhook-subscriptions, wsl-ssh-remote-access[/]")
    right_lines.append(f"[dim {dim}]mlops:[/] [{text}]huggingface-hub, llama-cpp, vllm, unsloth[/]")
    right_lines.append(f"[dim {dim}]research:[/] [{text}]arxiv, duckduckgo-search, last30days[/]")
    right_lines.append("")
    right_lines.append(f"[dim {dim}]14 tools · 42 skills · /help for commands[/]")

    right_content = "\n".join(right_lines)
    layout_table.add_row(Align.center(left_content), right_content)

    outer_panel = Panel(
        layout_table,
        title=f"[bold {c['title_color']}]{agent_name} v0.7.0 (2026.4.3)[/]",
        border_style=c['border_color'],
        padding=(0, 2),
    )
    console.print(outer_panel)

    welcome = skin.get_branding("welcome", "")
    if welcome:
        console.print()
        console.print(f"[{c['text']}]{welcome}[/]")

    console.print()

    return buf.getvalue()


def ansi_to_png(ansi_text, output_path, bg_color="#0d1117"):
    """Convert ANSI text to PNG via ansi2html + Chromium."""
    conv = Ansi2HTMLConverter(inline=True, dark_bg=True, font_size="14px")
    body = conv.convert(ansi_text, full=False)

    html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8">
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');
</style>
</head><body style="margin:0;background:{bg_color}">
<pre style="font-family:'JetBrains Mono','Fira Code','Cascadia Code',monospace;
font-size:13px;line-height:1.35;padding:24px 32px;color:#c0c0c0;
background:{bg_color};white-space:pre;overflow:hidden">{body}</pre>
</body></html>"""

    html_path = f"/tmp/skin_{Path(output_path).stem}.html"
    with open(html_path, "w") as f:
        f.write(html)

    hti = Html2Image(
        output_path=str(Path(output_path).parent),
        size=(1400, 1600),
        custom_flags=[
            "--no-sandbox",
            "--disable-gpu",
            "--force-device-scale-factor=2",
            "--hide-scrollbars",
        ]
    )
    png_name = Path(output_path).name
    hti.screenshot(html_file=html_path, save_as=png_name)

    # Auto-crop
    img = Image.open(output_path)
    bg = img.getpixel((0, 0))

    # Find content bounds
    last_row = 0
    last_col = 0
    first_row = img.height
    first_col = img.width

    threshold = 15

    # Scan for content boundaries
    for y in range(img.height):
        for x in range(0, img.width, 2):
            r, g, b = img.getpixel((x, y))[:3]
            if abs(r - bg[0]) > threshold or abs(g - bg[1]) > threshold or abs(b - bg[2]) > threshold:
                if y < first_row:
                    first_row = y
                if y > last_row:
                    last_row = y
                if x < first_col:
                    first_col = x
                if x > last_col:
                    last_col = x

    if last_row > 0:
        pad = 40
        crop_box = (
            max(0, first_col - pad),
            max(0, first_row - pad),
            min(img.width, last_col + pad),
            min(img.height, last_row + pad),
        )
        cropped = img.crop(crop_box)
        cropped.save(output_path)
        print(f"    Cropped: {cropped.size[0]}x{cropped.size[1]}")


def main():
    skin_files = sorted(SKINS_DIR.glob("*.yaml"))

    for skin_file in skin_files:
        skin_name = skin_file.stem
        print(f"Generating: {skin_name}")

        try:
            ansi = render_banner_ansi(skin_name, skin_path=str(skin_file))
            png_path = SCREENSHOTS_DIR / f"{skin_name}.png"
            ansi_to_png(ansi, str(png_path))
            print(f"  -> {png_path}")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()

    print(f"\nDone! Screenshots in {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    main()
