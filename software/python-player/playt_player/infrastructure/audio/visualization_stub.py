"""
Visualization stub for generating mock audio analysis data.
"""

import random
import threading
import time
from typing import Callable, List, Optional

from .beat_detector import BeatDetector


class VisualizationStub:
    """
    Generates mock visualization data (spectrum, RMS, amplitude, and beats) for testing UI.
    """

    def __init__(self) -> None:
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._on_spectrum_callback: Optional[Callable[[List[float]], None]] = None
        self._on_rms_callback: Optional[Callable[[float], None]] = None
        self._on_amplitude_callback: Optional[Callable[[float], None]] = None
        self._on_beat_callback: Optional[Callable[[], None]] = None
        
        # Beat detector with default settings
        self._beat_detector = BeatDetector(threshold=1.6, cooldown_ms=250)

    def set_callbacks(
        self,
        on_spectrum: Optional[Callable[[List[float]], None]] = None,
        on_rms: Optional[Callable[[float], None]] = None,
        on_amplitude: Optional[Callable[[float], None]] = None,
        on_beat: Optional[Callable[[], None]] = None,
    ) -> None:
        """Set callbacks for receiving visualization data."""
        self._on_spectrum_callback = on_spectrum
        self._on_rms_callback = on_rms
        self._on_amplitude_callback = on_amplitude
        self._on_beat_callback = on_beat

    def start(self) -> None:
        """Start generating mock data."""
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        """Stop generating mock data."""
        self._running = False
        if self._thread:
            self._thread.join(timeout=1.0)
            self._thread = None

    def _loop(self) -> None:
        """Main loop for generating data."""
        while self._running:
            # Emit data approximately every 50ms (~20fps)
            start_time = time.time()

            if self._on_spectrum_callback:
                # 64 random values between 0 and 1
                spectrum = [random.random() for _ in range(64)]
                self._on_spectrum_callback(spectrum)

            if self._on_rms_callback:
                # Random float between 0 and 1
                rms = random.random()
                self._on_rms_callback(rms)
            
            # Generate amplitude and detect beats
            amplitude = random.random()
            
            if self._on_amplitude_callback:
                self._on_amplitude_callback(amplitude)
            
            # Detect beat
            if self._on_beat_callback:
                beat_detected = self._beat_detector.detect(amplitude)
                if beat_detected:
                    self._on_beat_callback()

            # Sleep for remaining time to hit ~20fps
            elapsed = time.time() - start_time
            sleep_time = max(0.0, 0.05 - elapsed)
            time.sleep(sleep_time)
