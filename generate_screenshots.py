#!/usr/bin/env python3
"""Generate screenshot PNGs for each skin in the hermes-skins repo.

Renders the banner for each skin using Rich's SVG export + CairoSVG conversion.
Outputs PNG files to screenshots/ directory.
"""

import sys
import os

# Add hermes-agent to path so we can import skin_engine, banner, etc.
HERMES_AGENT_DIR = os.path.expanduser("~/projects/hermes-agent")
sys.path.insert(0, HERMES_AGENT_DIR)

import shutil
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.align import Align
import cairosvg
import yaml

# Skins directory
SKINS_DIR = Path(__file__).parent / "skins"
SCREENSHOTS_DIR = Path(__file__).parent / "screenshots"
SCREENSHOTS_DIR.mkdir(exist_ok=True)

# Import skin engine
from hermes_cli.skin_engine import (
    load_skin, set_active_skin, get_active_skin,
    _load_skin_from_yaml, _build_skin_config, SkinConfig
)


def get_skin_colors(skin):
    """Extract color values from a SkinConfig."""
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


def render_banner_for_skin(skin_name, skin_path=None):
    """Render a banner for a given skin and return SVG string."""
    
    # Load and activate the skin
    if skin_path:
        with open(skin_path) as f:
            skin_data = yaml.safe_load(f)
        skin = _build_skin_config(skin_data)
    else:
        skin = load_skin(skin_name)
    
    c = get_skin_colors(skin)
    
    # Get branding
    agent_name = skin.get_branding("agent_name", "Hermes Agent")
    
    # Get hero art
    hero = ""
    if hasattr(skin, 'banner_hero') and skin.banner_hero:
        hero = skin.banner_hero
    else:
        # Use default caduceus
        from hermes_cli.banner import HERMES_CADUCEUS
        hero = HERMES_CADUCEUS
    
    # Get logo
    logo = ""
    if hasattr(skin, 'banner_logo') and skin.banner_logo:
        logo = skin.banner_logo
    else:
        from hermes_cli.banner import HERMES_AGENT_LOGO
        logo = HERMES_AGENT_LOGO
    
    # Build a mock banner
    console = Console(record=True, width=120, force_terminal=True)
    
    # Print logo centered
    console.print()
    console.print(Align.center(logo))
    console.print()
    
    # Build layout table
    layout_table = Table.grid(padding=(0, 2))
    layout_table.add_column("left", justify="center")
    layout_table.add_column("right", justify="left")
    
    # Left side: hero art + model info
    left_lines = ["", hero, ""]
    left_lines.append(f"[{c['accent']}]claude-opus-4-6[/] [{c['dim']}]·[/] [{c['dim']}]200K context[/] [{c['dim']}]·[/] [{c['dim']}]Nous Research[/]")
    left_lines.append(f"[dim {c['dim']}]~/projects[/]")
    left_lines.append(f"[dim {c['session_color']}]Session: a1b2c3d4[/]")
    left_content = "\n".join(left_lines)
    
    # Right side: mock tools + skills
    accent = c['accent']
    dim = c['dim']
    text = c['text']
    label = c['label']
    
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
    
    # Also print welcome message if available
    welcome = skin.get_branding("welcome", "")
    if welcome:
        console.print()
        console.print(f"[{c['text']}]{welcome}[/]")
    
    console.print()
    
    return console.export_svg(title=f"{skin_name} skin")


def svg_to_png(svg_string, output_path, scale=1.5):
    """Convert SVG string to PNG file."""
    cairosvg.svg2png(
        bytestring=svg_string.encode('utf-8'),
        write_to=str(output_path),
        scale=scale
    )


def main():
    skin_files = sorted(SKINS_DIR.glob("*.yaml"))
    
    for skin_file in skin_files:
        skin_name = skin_file.stem
        print(f"Generating screenshot for: {skin_name}")
        
        try:
            svg = render_banner_for_skin(skin_name, skin_path=str(skin_file))
            
            # Save SVG (useful for debugging)
            svg_path = SCREENSHOTS_DIR / f"{skin_name}.svg"
            svg_path.write_text(svg)
            
            # Convert to PNG
            png_path = SCREENSHOTS_DIR / f"{skin_name}.png"
            svg_to_png(svg, png_path)
            
            print(f"  -> {png_path}")
        except Exception as e:
            print(f"  ERROR: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"\nDone! Screenshots saved to {SCREENSHOTS_DIR}")


if __name__ == "__main__":
    main()
