"""
This module performs audio analysis on a raw audio stream.
"""
import numpy as np
from scipy.fftpack import fft  # type: ignore
from scipy.signal.windows import blackmanharris  # type: ignore
from typing import Any, List, Dict

class AudioAnalysis:
    def __init__(self, sample_rate: int, chunk_size: int, num_bands: int = 64) -> None:
        self.sample_rate = sample_rate
        self.chunk_size = chunk_size
        self.num_bands = num_bands
        self.window = blackmanharris(chunk_size)

    def analyze(self, data: bytes) -> Dict[str, Any]:
        """
        Analyzes a chunk of audio data.
        """
        # Waveform
        waveform = np.frombuffer(data, dtype=np.int16)

        # RMS
        rms = np.sqrt(np.mean(waveform.astype(np.float64)**2))

        # Spectrum
        fft_data = fft(waveform * self.window)
        spectrum = np.abs(fft_data)[:self.chunk_size // 2]
        
        # Beat detection (simple energy-based)
        beat = rms > 1000  # This is a very simple and probably not very effective beat detection

        return {
            "spectrum": self.group_into_bands(spectrum, self.num_bands),
            "waveform": waveform.tolist(),
            "rms": float(rms),
            "beat": bool(beat),
        }

    def group_into_bands(self, data: Any, num_bands: int) -> List[float]:
        """
        Groups FFT data into a smaller number of bands.
        """
        band_size = len(data) // num_bands
        bands = []
        for i in range(num_bands):
            start = i * band_size
            end = start + band_size
            band_data = data[start:end]
            bands.append(float(np.mean(band_data)))
        return bands
