"""Test the WebViewUI behavior and integration with PlayerService."""

import json
from unittest.mock import MagicMock, patch, call

import pytest

from playt_player.application.player_service import PlayerService
from playt_player.domain.entities.album import Album
from playt_player.domain.entities.song import Song
from playt_player.interface.gui.webview_ui import WebViewUI, PlaytJSApi


@pytest.fixture
def mock_player_service():
    return MagicMock(spec=PlayerService)


@pytest.fixture
def mock_logger():
    return MagicMock()


@pytest.fixture
def js_api(mock_player_service, mock_logger):
    return PlaytJSApi(mock_player_service, mock_logger)


class TestPlaytJSApi:
    """Test the JS API bridge."""

    def test_controls_call_service(self, js_api, mock_player_service):
        """Verify JS commands trigger service methods."""
        js_api.play()
        mock_player_service.play.assert_called_once()

        js_api.pause()
        mock_player_service.pause.assert_called_once()

        js_api.next()
        mock_player_service.next.assert_called_once()

        js_api.previous()
        mock_player_service.previous.assert_called_once()

        js_api.seek(30.5)
        mock_player_service.seek.assert_called_once_with(30.5)

        js_api.setVolume(0.8)
        mock_player_service.set_volume.assert_called_once_with(0.8)

    def test_toggle_play(self, js_api, mock_player_service):
        """Verify togglePlay logic."""
        # If playing -> pause
        mock_player_service.get_state.return_value = "playing"
        js_api.togglePlay()
        mock_player_service.pause.assert_called_once()
        mock_player_service.play.assert_not_called()

        mock_player_service.reset_mock()

        # If paused -> play
        mock_player_service.get_state.return_value = "paused"
        js_api.togglePlay()
        mock_player_service.play.assert_called_once()
        mock_player_service.pause.assert_not_called()


class TestWebViewUI:
    """Test UI event handling."""

    @patch("playt_player.interface.gui.webview_ui.webview")
    def test_update_track_started(self, mock_webview, mock_player_service):
        """Verify track_started event updates UI."""
        ui = WebViewUI(mock_player_service, "dummy.html")
        # Mock the window object
        ui._window = MagicMock()

        song = Song(
            title="Test Song",
            artist="Test Artist",
            album="Test Album",
            duration_secs=120.0,
            file_path="/tmp/test.mp3",
        )

        ui.update("track_started", song)

        # Check that JS was evaluated to update track info
        # We expect two calls: one for track info, one for playback state
        assert ui._window.evaluate_js.call_count >= 2
        
        # Verify track info update
        args, _ = ui._window.evaluate_js.call_args_list[0]
        js_code = args[0]
        assert "window.playt._emitTrackChange" in js_code
        assert "Test Song" in js_code
        assert "Test Artist" in js_code

        # Verify playback state update
        args, _ = ui._window.evaluate_js.call_args_list[1]
        js_code = args[0]
        assert "window.playt._emitPlaybackState('playing')" in js_code

    @patch("playt_player.interface.gui.webview_ui.webview")
    def test_update_playback_states(self, mock_webview, mock_player_service):
        """Verify paused/stopped events update UI."""
        ui = WebViewUI(mock_player_service, "dummy.html")
        ui._window = MagicMock()

        ui.update("track_paused", None)
        ui._window.evaluate_js.assert_called_with("window.playt._emitPlaybackState('paused')")

        ui.update("track_stopped", None)
        ui._window.evaluate_js.assert_called_with("window.playt._emitPlaybackState('stopped')")

    @patch("playt_player.interface.gui.webview_ui.webview")
    def test_initial_state_sync(self, mock_webview, mock_player_service):
        """Verify UI syncs state on ready."""
        ui = WebViewUI(mock_player_service, "dummy.html")
        ui._window = MagicMock()
        
        song = Song(
            title="Current Song",
            artist="Current Artist",
            album="Current Album",
            duration_secs=180.0,
            file_path="/tmp/current.mp3",
        )
        mock_player_service.get_current_song.return_value = song
        mock_player_service.get_state.return_value = "playing"

        # Simulate on_ready callback
        ui._on_ready()

        # Verify initial track info sent
        track_calls = [
            c for c in ui._window.evaluate_js.call_args_list 
            if "window.playt._emitTrackChange" in c[0][0]
        ]
        assert len(track_calls) > 0
        assert "Current Song" in track_calls[0][0][0]

        # Verify initial state sent
        state_calls = [
            c for c in ui._window.evaluate_js.call_args_list 
            if "window.playt._emitPlaybackState" in c[0][0]
        ]
        assert len(state_calls) > 0
        assert "'playing'" in state_calls[0][0][0]
