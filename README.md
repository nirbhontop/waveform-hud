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

MIT License

Copyright (c) 2026 Nirbhaya Shiwakoti

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
