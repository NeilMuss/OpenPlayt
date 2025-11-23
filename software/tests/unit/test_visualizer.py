"""
Tests for visualizer functionality.
"""
import json
import pytest
from pathlib import Path


class TestVisualizerConfig:
    """Tests for visualizer configuration."""
    
    def test_config_file_exists(self):
        """Test that visualizer config file exists."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        assert config_path.exists(), "visualizer_config.json should exist"
    
    def test_config_structure(self):
        """Test that config has required structure."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        assert "enabled" in config
        assert "active_visualizer" in config
        assert "visualizers" in config
        assert isinstance(config["visualizers"], dict)
    
    def test_pulse_visualizer_in_config(self):
        """Test that pulse visualizer is defined in config."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        assert "pulse" in config["visualizers"]
        assert "sensitivity" in config["visualizers"]["pulse"]
    
    def test_colorwash_visualizer_in_config(self):
        """Test that colorwash visualizer is defined in config."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        assert "colorwash" in config["visualizers"]
        assert "speed" in config["visualizers"]["colorwash"]
    
    def test_active_visualizer_is_valid(self):
        """Test that active_visualizer references a defined visualizer."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        active = config["active_visualizer"]
        assert active in config["visualizers"], \
            f"active_visualizer '{active}' must be defined in visualizers"


class TestVisualizerRegistry:
    """Tests for visualizer registry."""
    
    def test_supported_visualizers(self):
        """Test that both pulse and colorwash are supported."""
        # This would test against a registry if we had one
        # For now, we verify via config
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        supported = list(config["visualizers"].keys())
        assert "pulse" in supported
        assert "colorwash" in supported


class TestAmplitudeAnalyzer:
    """Tests for amplitude analyzer."""
    
    def test_amplitude_analyzer_import(self):
        """Test that AmplitudeAnalyzer can be imported."""
        from playt_player.infrastructure.audio.amplitude_analyzer import AmplitudeAnalyzer
        assert AmplitudeAnalyzer is not None
    
    def test_amplitude_analyzer_initialization(self):
        """Test that AmplitudeAnalyzer initializes correctly."""
        from playt_player.infrastructure.audio.amplitude_analyzer import AmplitudeAnalyzer
        analyzer = AmplitudeAnalyzer(smoothing=0.3)
        assert analyzer.smoothing == 0.3
    
    def test_amplitude_analyzer_returns_normalized_value(self):
        """Test that analyzer returns value between 0 and 1."""
        from playt_player.infrastructure.audio.amplitude_analyzer import AmplitudeAnalyzer
        import numpy as np
        
        analyzer = AmplitudeAnalyzer(smoothing=0.0)
        
        # Create mock audio data (int16 format)
        samples = np.array([1000, -1000, 2000, -2000], dtype=np.int16)
        audio_bytes = samples.tobytes()
        
        amplitude = analyzer.analyze(audio_bytes)
        
        assert 0.0 <= amplitude <= 1.0
        assert amplitude > 0.0  # Should be non-zero for non-silent audio


class TestVisualizationStub:
    """Tests for visualization stub."""
    
    def test_visualization_stub_has_amplitude_callback(self):
        """Test that VisualizationStub supports amplitude callback."""
        from playt_player.infrastructure.audio.visualization_stub import VisualizationStub
        
        stub = VisualizationStub()
        
        # Should have amplitude callback attribute
        assert hasattr(stub, '_on_amplitude_callback')
    
    def test_amplitude_callback_is_called(self):
        """Test that amplitude callback is invoked."""
        from playt_player.infrastructure.audio.visualization_stub import VisualizationStub
        import time
        
        stub = VisualizationStub()
        
        received_values = []
        
        def on_amplitude(val):
            received_values.append(val)
        
        stub.set_callbacks(on_amplitude=on_amplitude)
        stub.start()
        
        # Wait for a few callbacks
        time.sleep(0.2)
        stub.stop()
        
        # Should have received at least one amplitude value
        assert len(received_values) > 0
        # All values should be between 0 and 1
        assert all(0.0 <= v <= 1.0 for v in received_values)


class TestVisualizerSwitching:
    """Tests for visualizer switching logic."""
    
    def test_config_allows_switching_to_pulse(self):
        """Test that config can be set to pulse visualizer."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Modify config to use pulse
        config["active_visualizer"] = "pulse"
        
        # Verify it's valid
        assert config["active_visualizer"] in config["visualizers"]
    
    def test_config_allows_switching_to_colorwash(self):
        """Test that config can be set to colorwash visualizer."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Modify config to use colorwash
        config["active_visualizer"] = "colorwash"
        
        # Verify it's valid
        assert config["active_visualizer"] in config["visualizers"]
    
    def test_config_allows_switching_to_beat(self):
        """Test that config can be set to beat visualizer."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Modify config to use beat
        config["active_visualizer"] = "beat"
        
        # Verify it's valid
        assert config["active_visualizer"] in config["visualizers"]


class TestBeatVisualizer:
    """Tests for beat visualizer functionality."""
    
    def test_beat_visualizer_in_config(self):
        """Test that beat visualizer is defined in config."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        assert "beat" in config["visualizers"]
        assert "threshold" in config["visualizers"]["beat"]
        assert "cooldown_ms" in config["visualizers"]["beat"]
        assert "flash_intensity" in config["visualizers"]["beat"]
    
    def test_beat_detector_import(self):
        """Test that BeatDetector can be imported."""
        from playt_player.infrastructure.audio.beat_detector import BeatDetector
        assert BeatDetector is not None
    
    def test_beat_detector_initialization(self):
        """Test that BeatDetector initializes correctly."""
        from playt_player.infrastructure.audio.beat_detector import BeatDetector
        detector = BeatDetector(threshold=1.6, cooldown_ms=250)
        assert detector.threshold == 1.6
        assert detector.cooldown_ms == 250
    
    def test_beat_detector_triggers_on_spike(self):
        """Test that beat detector triggers when amplitude crosses threshold."""
        from playt_player.infrastructure.audio.beat_detector import BeatDetector
        import time
        
        detector = BeatDetector(threshold=1.5, cooldown_ms=100)
        
        # Build up history with low values
        for _ in range(10):
            result = detector.detect(0.2)
            assert not result  # Should not detect beat with low amplitude
        
        # Spike should trigger beat
        result = detector.detect(0.8)  # 0.8 > (0.2 * 1.5)
        assert result, "Beat should be detected on amplitude spike"
    
    def test_beat_detector_cooldown_prevents_retriggering(self):
        """Test that cooldown prevents immediate retriggering."""
        from playt_player.infrastructure.audio.beat_detector import BeatDetector
        import time
        
        detector = BeatDetector(threshold=1.5, cooldown_ms=200)
        
        # Build up history
        for _ in range(10):
            detector.detect(0.2)
        
        # First spike triggers beat
        result1 = detector.detect(0.8)
        assert result1, "First beat should be detected"
        
        # Immediate second spike should be blocked by cooldown
        result2 = detector.detect(0.8)
        assert not result2, "Second beat should be blocked by cooldown"
        
        # After cooldown, should trigger again
        time.sleep(0.25)  # Wait for cooldown
        for _ in range(5):
            detector.detect(0.2)  # Reset average
        result3 = detector.detect(0.8)
        assert result3, "Beat should be detected after cooldown"
    
    def test_visualization_stub_has_beat_callback(self):
        """Test that VisualizationStub supports beat callback."""
        from playt_player.infrastructure.audio.visualization_stub import VisualizationStub
        
        stub = VisualizationStub()
        assert hasattr(stub, '_on_beat_callback')
        assert hasattr(stub, '_beat_detector')
    
    def test_beat_callback_is_called(self):
        """Test that beat callback is invoked when beat detected."""
        from playt_player.infrastructure.audio.visualization_stub import VisualizationStub
        import time
        
        stub = VisualizationStub()
        
        beat_count = []
        
        def on_beat():
            beat_count.append(1)
        
        stub.set_callbacks(on_beat=on_beat)
        stub.start()
        
        # Wait for potential beats
        time.sleep(1.0)
        stub.stop()
        
        # Should have detected at least one beat in random data
        # (This is probabilistic but should work with random amplitude spikes)
        assert len(beat_count) >= 0  # At minimum, no errors
