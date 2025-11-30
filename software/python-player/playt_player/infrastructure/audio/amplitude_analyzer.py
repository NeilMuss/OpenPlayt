"""
Simple amplitude analyzer for audio visualization.
Extracts RMS (Root Mean Square) amplitude from audio chunks.
"""
import numpy as np
from typing import Optional


class AmplitudeAnalyzer:
    """Analyzes audio amplitude for visualization purposes."""
    
    def __init__(self, smoothing: float = 0.3):
        """
        Initialize the amplitude analyzer.
        
        Args:
            smoothing: Smoothing factor (0.0 = no smoothing, 1.0 = maximum smoothing)
        """
        self.smoothing = max(0.0, min(1.0, smoothing))
        self._last_amplitude: Optional[float] = None
    
    def analyze(self, audio_data: bytes) -> float:
        """
        Extract normalized amplitude from audio data.
        
        Args:
            audio_data: Raw audio bytes (int16 format)
            
        Returns:
            Normalized amplitude value (0.0 to 1.0)
        """
        # Convert bytes to numpy array
        samples = np.frombuffer(audio_data, dtype=np.int16)
        
        if len(samples) == 0:
            return 0.0
        
        # Calculate RMS (Root Mean Square)
        rms = np.sqrt(np.mean(samples.astype(np.float64) ** 2))
        
        # Normalize to 0.0-1.0 range (int16 max is 32768)
        normalized = min(1.0, rms / 32768.0)
        
        # Apply smoothing
        if self._last_amplitude is not None:
            normalized = (self.smoothing * self._last_amplitude + 
                         (1.0 - self.smoothing) * normalized)
        
        self._last_amplitude = normalized
        
        return normalized
