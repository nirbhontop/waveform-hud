# waveform-hud

Brutalist dark-and-orange (`#0D0D0D` / `#FF4500`) terminal waveform & HUD telemetry monitor built with Python and `rich`.

## Quick Start

```bash
git clone https://github.com/nirbhontop/waveform-hud.git
cd waveform-hud
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e .
waveform-hud
```

### Optional Live Audio Input

```bash
pip install -e ".[audio]"
waveform-hud --live-audio
```

## CLI Options

* `--slot`: HUD slot label (default: `SLOT 01`)
* `--tag`: Secondary HUD identifier (default: `0799 · 0184`)
* `--bars`: Waveform bar count (default: `43`)
* `--fps`: Frame rate cap (default: `24`)
* `--live-audio`: Blend real-time audio input spectrum when available

## License

MIT
