from __future__ import annotations

import math
import random
import time
from dataclasses import dataclass, field


@dataclass
class HudTelemetry:
    slot_id: str = "SLOT 01"
    freq_tag: str = "0799 · 0184"
    status: str = "AUDIO: PLAYING"
    bars: list[float] = field(default_factory=list)
    accent_mask: list[bool] = field(default_factory=list)
    peak_db: float = -3.4
    bpm_est: int = 128
    tick: int = 0


class WaveformEngine:
    """Generates reactive waveform bars with optional live PortAudio/sounddevice input."""

    def __init__(self, num_bars: int = 43, live_audio: bool = False) -> None:
        self.num_bars = num_bars
        self.live_audio = live_audio
        self._phase = 0.0
        self._last_time = time.monotonic()
        self._smooth_bars = [0.15] * num_bars
        self._live_levels: list[float] | None = None
        self._stream = None

        # Signature brutalist envelope + orange accent bar indices
        self._envelope = self._build_envelope(num_bars)
        self._accent_indices = {
            i for i in range(num_bars)
            if (i in {2, 5, 9, 13, 18, 22, 27, 32, 36, 40})
        }

        if self.live_audio:
            self._init_live_audio()

    @staticmethod
    def _build_envelope(n: int) -> list[float]:
        env = []
        for i in range(n):
            norm = (i / max(n - 1, 1)) * 2.0 - 1.0  # -1.0 to +1.0
            # Multi-peaked brutalist waveform silhouette
            arch = math.exp(-(norm ** 2) * 2.1)
            rib = 0.72 + 0.28 * math.cos(i * 1.15)
            notch = 0.45 if abs(i - n // 2) <= 1 else 1.0
            env.append(max(0.12, min(1.0, arch * rib * notch)))
        return env

    def _init_live_audio(self) -> None:
        try:
            import numpy as np  # type: ignore
            import sounddevice as sd  # type: ignore

            def callback(indata, frames, time_info, status):  # noqa: ARG001
                if indata.size == 0:
                    return
                mono = indata[:, 0].astype(np.float32)
                window = np.hanning(len(mono))
                spectrum = np.abs(np.fft.rfft(mono * window))
                if spectrum.size == 0:
                    return
                bins = np.array_split(spectrum, self.num_bars)
                vals = [float(np.clip(np.mean(b) * 18.0, 0.05, 1.0)) for b in bins]
                self._live_levels = vals

            self._stream = sd.InputStream(channels=1, callback=callback, blocksize=1024)
            self._stream.start()
        except Exception:
            # Seamless fallback to deterministic synthesizer if audio backend is unavailable
            self._stream = None
            self._live_levels = None

    def step(self) -> HudTelemetry:
        now = time.monotonic()
        dt = max(0.008, min(0.1, now - self._last_time))
        self._last_time = now
        self._phase += dt * 7.5

        raw_bars: list[float] = []
        for i in range(self.num_bars):
            base = self._envelope[i]
            wave_a = 0.5 + 0.5 * math.sin(self._phase * 1.45 - i * 0.42)
            wave_b = 0.5 + 0.5 * math.cos(self._phase * 0.85 + i * 0.27)
            jitter = random.uniform(-0.08, 0.08)

            synth_val = base * (0.35 + 0.45 * wave_a + 0.25 * wave_b) + jitter
            if self._live_levels is not None and i < len(self._live_levels):
                val = 0.35 * synth_val + 0.65 * self._live_levels[i]
            else:
                val = synth_val

            clamped = max(0.06, min(1.0, val))
            self._smooth_bars[i] = self._smooth_bars[i] * 0.45 + clamped * 0.55
            raw_bars.append(self._smooth_bars[i])

        avg_energy = sum(raw_bars) / max(len(raw_bars), 1)
        peak_db = round(-18.0 + avg_energy * 17.5, 1)
        bpm_est = int(124 + round(math.sin(self._phase * 0.25) * 6))

        status = "AUDIO: PLAYING" if self._stream is None else "AUDIO: LIVE MIC"
        telemetry = HudTelemetry(
            slot_id="SLOT 01",
            freq_tag="0799 · 0184",
            status=status,
            bars=raw_bars,
            accent_mask=[i in self._accent_indices for i in range(self.num_bars)],
            peak_db=peak_db,
            bpm_est=bpm_est,
            tick=self._smooth_bars.__len__(),
        )
        return telemetry

    def close(self) -> None:
        if self._stream is not None:
            try:
                self._stream.stop()
                self._stream.close()
            except Exception:
                pass
