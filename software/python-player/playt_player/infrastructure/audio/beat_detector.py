"""
Simple beat detector based on amplitude spikes.
"""
import time
from typing import Optional
from collections import deque


class BeatDetector:
    """Detects beats using amplitude spike detection with rolling average."""
    
    def __init__(self, threshold: float = 1.6, cooldown_ms: int = 250, window_size: int = 10):
        """
        Initialize the beat detector.
        
        Args:
            threshold: Multiplier for beat detection (amplitude must exceed threshold × average)
            cooldown_ms: Minimum milliseconds between beats to prevent double-triggering
            window_size: Number of recent amplitude values to average
        """
        self.threshold = threshold
        self.cooldown_ms = cooldown_ms
        self.window_size = window_size
        
        self._amplitude_history = deque(maxlen=window_size)
        self._last_beat_time: Optional[float] = None
    
    def detect(self, amplitude: float) -> bool:
        """
        Detect if current amplitude represents a beat.
        
        Args:
            amplitude: Current amplitude value (0.0 to 1.0)
            
        Returns:
            True if beat detected, False otherwise
        """
        current_time = time.time()
        
        # Add to history
        self._amplitude_history.append(amplitude)
        
        # Need enough history to calculate average
        if len(self._amplitude_history) < self.window_size:
            return False
        
        # Check cooldown
        if self._last_beat_time is not None:
            time_since_last_beat = (current_time - self._last_beat_time) * 1000  # Convert to ms
            if time_since_last_beat < self.cooldown_ms:
                return False
        
        # Calculate rolling average
        avg_amplitude = sum(self._amplitude_history) / len(self._amplitude_history)
        
        # Detect beat: current amplitude significantly exceeds average
        if amplitude > (avg_amplitude * self.threshold):
            self._last_beat_time = current_time
            return True
        
        return False
    
    def reset(self) -> None:
        """Reset the beat detector state."""
        self._amplitude_history.clear()
        self._last_beat_time = None
