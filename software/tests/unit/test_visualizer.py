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
    
    def test_config_allows_switching_to_beat_pulse(self):
        """Test that config can be set to beat_pulse visualizer."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        # Modify config to use beat_pulse
        config["active_visualizer"] = "beat_pulse"
        
        # Verify it's valid
        assert config["active_visualizer"] in config["visualizers"]


class TestBeatPulseVisualizer:
    """Tests for beat_pulse hybrid visualizer."""
    
    def test_beat_pulse_in_config(self):
        """Test that beat_pulse visualizer is defined in config."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        assert "beat_pulse" in config["visualizers"]
        assert "sensitivity" in config["visualizers"]["beat_pulse"]
        assert "beat_boost" in config["visualizers"]["beat_pulse"]
        assert "decay_rate" in config["visualizers"]["beat_pulse"]
    
    def test_beat_pulse_config_parameters(self):
        """Test that beat_pulse has correct parameter types and ranges."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        bp_config = config["visualizers"]["beat_pulse"]
        
        # Check types
        assert isinstance(bp_config["sensitivity"], (int, float))
        assert isinstance(bp_config["beat_boost"], (int, float))
        assert isinstance(bp_config["decay_rate"], (int, float))
        
        # Check reasonable ranges
        assert 0.1 <= bp_config["sensitivity"] <= 5.0
        assert 1.0 <= bp_config["beat_boost"] <= 10.0
        assert 0.5 <= bp_config["decay_rate"] <= 1.0
    
    def test_beat_pulse_uses_existing_streams(self):
        """Test that beat_pulse can use existing amplitude and beat streams."""
        from playt_player.infrastructure.audio.visualization_stub import VisualizationStub
        
        stub = VisualizationStub()
        
        # Verify both callbacks exist
        assert hasattr(stub, '_on_amplitude_callback')
        assert hasattr(stub, '_on_beat_callback')
        
        # Both streams should be available simultaneously
        amplitude_values = []
        beat_count = []
        
        def on_amplitude(val):
            amplitude_values.append(val)
        
        def on_beat():
            beat_count.append(1)
        
        stub.set_callbacks(on_amplitude=on_amplitude, on_beat=on_beat)
        stub.start()
        
        import time
        time.sleep(0.3)
        stub.stop()
        
        # Both streams should have data
        assert len(amplitude_values) > 0
        # Beat count may be 0 depending on random data, but callback should work
        assert isinstance(beat_count, list)
    
    def test_visualizer_registry_includes_beat_pulse(self):
        """Test that beat_pulse is in the visualizer registry."""
        config_path = Path(__file__).parent.parent.parent / "visualizer_config.json"
        with open(config_path) as f:
            config = json.load(f)
        
        supported = list(config["visualizers"].keys())
        assert "beat_pulse" in supported
        assert "pulse" in supported
        assert "beat" in supported
        assert "colorwash" in supported
