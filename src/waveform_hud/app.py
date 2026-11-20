from __future__ import annotations

import argparse
import sys
import time

from rich.align import Align
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from waveform_hud.engine import HudTelemetry, WaveformEngine

BG_DARK = "#0D0D0D"
SURFACE = "#141414"
GRID_DIM = "#222222"
ACCENT_ORANGE = "#FF4500"
FG_WHITE = "#F5F5F5"
FG_MUTED = "#9A9A9A"


def render_hud(data: HudTelemetry, height: int = 13) -> Panel:
    # Build vertical bar matrix inside a brutalist grid
    grid = Table.grid(padding=(0, 0), expand=False)
    for _ in range(data.num_bars if hasattr(data, "num_bars") else len(data.bars)):
        grid.add_column(width=2, justify="center")

    bar_heights = [max(1, min(height, int(round(v * height)))) for v in data.bars]
    center_row = height // 2

    for row_idx in range(height):
        # Symmetric waveform around center_row
        dist_from_center = abs(row_idx - center_row)
        row_cells: list[Text] = []

        for col_idx, b_len in enumerate(bar_heights):
            half_span = max(1, b_len // 2)
            active = dist_from_center < half_span
            is_orange = data.accent_mask[col_idx]

            if active:
                color = ACCENT_ORANGE if is_orange else FG_WHITE
                glyph = "█"
            else:
                # Subtle grid crosshair on inactive cells
                is_grid_line = (row_idx % 3 == 0) or (col_idx % 4 == 0)
                color = GRID_DIM if is_grid_line else BG_DARK
                glyph = "·" if is_grid_line else " "

            row_cells.append(Text(glyph, style=f"bold {color}" if active else color))

        grid.add_row(*row_cells)

    # Top-left HUD badge block matching SLOT 01 / 0799 · 0184
    header = Text()
    header.append(f" {data.slot_id} ", style=f"bold {FG_WHITE} on {SURFACE}")
    header.append("  ")
    header.append(f" {data.freq_tag} ", style=f"bold {FG_WHITE} on {SURFACE}")
    header.append(f"    PEAK {data.peak_db:+.1f}dB  ·  {data.bpm_est} BPM", style=f"bold {FG_MUTED}")

    # Bottom bar with REPO LIST badge and AUDIO: PLAYING indicator
    footer = Text()
    footer.append(" REPO LIST ", style=f"bold {FG_WHITE} on {ACCENT_ORANGE}")
    footer.append("        ")
    footer.append(f"{data.status}", style=f"bold {ACCENT_ORANGE}")

    body = Table.grid(padding=(0, 0))
    body.add_row(header)
    body.add_row(Text(""))
    body.add_row(Align.center(grid))
    body.add_row(Text(""))
    body.add_row(Align.right(footer))

    return Panel(
        body,
        border_style=ACCENT_ORANGE,
        style=f"on {BG_DARK}",
        padding=(1, 2),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="waveform-hud",
        description="Brutalist terminal waveform & HUD telemetry monitor.",
    )
    parser.add_argument(
        "--slot",
        default="SLOT 01",
        help="HUD slot label (default: SLOT 01)",
    )
    parser.add_argument(
        "--tag",
        default="0799 · 0184",
        help="Secondary HUD code tag (default: '0799 · 0184')",
    )
    parser.add_argument(
        "--bars",
        type=int,
        default=43,
        help="Number of waveform columns (default: 43)",
    )
    parser.add_argument(
        "--fps",
        type=int,
        default=24,
        help="Refresh rate in frames per second (default: 24)",
    )
    parser.add_argument(
        "--live-audio",
        action="store_true",
        help="Attempt live microphone/input spectrum capture (requires optional 'audio' extra)",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    console = Console(style=f"on {BG_DARK}")
    engine = WaveformEngine(num_bars=max(11, args.bars), live_audio=args.live_audio)
    delay = 1.0 / max(1, min(60, args.fps))

    try:
        with Live(
            render_hud(engine.step()),
            console=console,
            refresh_per_second=max(1, min(60, args.fps)),
            screen=True,
        ) as live:
            while True:
                telemetry = engine.step()
                telemetry.slot_id = args.slot
                telemetry.freq_tag = args.tag
                live.update(render_hud(telemetry))
                time.sleep(delay)
    except KeyboardInterrupt:
        return 0
    finally:
        engine.close()


if __name__ == "__main__":
    sys.exit(main())
