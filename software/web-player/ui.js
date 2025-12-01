/**
 * UI Controller - Manages user interface and updates
 */

/**
 * Format time in seconds to MM:SS format
 */
function formatTime(seconds) {
    if (seconds === null || isNaN(seconds)) return '0:00';
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * UI Controller class
 */
export class UIController {
    constructor(playerService) {
        this.playerService = playerService;
        this.elements = {};
        
        // Attach UI as observer
        this.playerService.attach(this);
        
        this._initializeElements();
        this._attachEventListeners();
    }

    _initializeElements() {
        // Find all UI elements
        this.elements = {
            fileInput: document.getElementById('file-input'),
            loadButton: document.getElementById('load-button'),
            playButton: document.getElementById('play-button'),
            pauseButton: document.getElementById('pause-button'),
            nextButton: document.getElementById('next-button'),
            prevButton: document.getElementById('prev-button'),
            volumeSlider: document.getElementById('volume-slider'),
            progressBar: document.getElementById('progress-bar'),
            progressContainer: document.getElementById('progress-bar-container'),
            currentTime: document.getElementById('current-time'),
            duration: document.getElementById('total-time'),
            songTitle: document.getElementById('track-title'),
            songArtist: document.getElementById('track-artist'),
            albumArt: document.getElementById('album-art'),
            artworkPlaceholder: document.getElementById('artwork-placeholder'),
            statusMessage: document.getElementById('status-message')
        };
    }

    _attachEventListeners() {
        // File loading
        if (this.elements.loadButton) {
            this.elements.loadButton.addEventListener('click', () => {
                this.elements.fileInput?.click();
            });
        }

        if (this.elements.fileInput) {
            this.elements.fileInput.addEventListener('change', async (e) => {
                const file = e.target.files[0];
                if (file) {
                    await this._handleFileLoad(file);
                }
            });
        }

        // Playback controls
        if (this.elements.playButton) {
            this.elements.playButton.addEventListener('click', () => {
                console.log('Play button clicked');
                this.playerService.play();
                // Update UI immediately, then again after audio starts
                this._updatePlaybackControls();
                setTimeout(() => {
                    this._updatePlaybackControls();
                }, 300);
            });
        }

        if (this.elements.pauseButton) {
            this.elements.pauseButton.addEventListener('click', () => {
                this.playerService.pause();
            });
        }

        if (this.elements.nextButton) {
            this.elements.nextButton.addEventListener('click', () => {
                this.playerService.next();
            });
        }

        if (this.elements.prevButton) {
            this.elements.prevButton.addEventListener('click', () => {
                this.playerService.previous();
            });
        }

        // Volume control (0-1 range)
        if (this.elements.volumeSlider) {
            this.elements.volumeSlider.addEventListener('input', (e) => {
                const volume = parseFloat(e.target.value);
                this.playerService.setVolume(volume);
            });
        }

        // Progress bar seeking
        if (this.elements.progressContainer) {
            this.elements.progressContainer.addEventListener('click', (e) => {
                const rect = this.elements.progressContainer.getBoundingClientRect();
                const percent = (e.clientX - rect.left) / rect.width;
                const duration = this.playerService.getDuration();
                if (duration) {
                    const position = percent * duration;
                    this.playerService.seek(position);
                }
            });
        }

        // Update UI periodically
        setInterval(() => this._updateProgress(), 100);
    }

    async _handleFileLoad(file) {
        try {
            this._showStatus('Loading ' + file.name + '...');
            console.log('Loading .playt file:', file.name);
            
            const { loadPlaytFile } = await import('./audio-loader.js');
            const album = await loadPlaytFile(file);
            
            console.log('Loaded album:', album.title, 'with', album.songs.length, 'songs');
            album.songs.forEach((song, idx) => {
                console.log(`  ${idx + 1}. ${song.title} - ${song.file_path.substring(0, 50)}...`);
            });
            
            this.playerService.loadAlbum(album);
            this._showStatus(`Loaded ${album.songs.length} songs from ${album.title}`);
            
            // Auto-play first song (may be blocked by browser autoplay policy)
            console.log('Attempting to start playback...');
            this.playerService.play();
            
            // Update UI immediately to show track info
            const currentSong = this.playerService.getCurrentSong();
            if (currentSong) {
                this._updateSongInfo(currentSong);
            }
            
            // Check if play was successful after a delay to allow audio to start
            setTimeout(() => {
                this._updatePlaybackControls();
                const state = this.playerService.getState();
                console.log('Playback state after start:', state);
                if (state !== 'playing') {
                    this._showStatus('Click play to start playback (autoplay may be blocked)', 'info');
                }
            }, 1000);
        } catch (error) {
            console.error('Failed to load file:', error);
            console.error('Error stack:', error.stack);
            this._showStatus('Error loading file: ' + error.message, 'error');
        }
    }

    _updateProgress() {
        const position = this.playerService.getPosition();
        const duration = this.playerService.getDuration();
        
        if (this.elements.currentTime) {
            this.elements.currentTime.textContent = formatTime(position);
        }
        
        if (this.elements.duration) {
            this.elements.duration.textContent = formatTime(duration);
        }
        
        if (this.elements.progressBar && duration > 0) {
            const percent = position ? (position / duration) * 100 : 0;
            this.elements.progressBar.style.width = `${percent}%`;
        }
    }


    _updatePlaybackControls() {
        const state = this.playerService.getState();
        console.log('Updating playback controls, state:', state);
        
        if (this.elements.playButton && this.elements.pauseButton) {
            if (state === 'playing') {
                this.elements.playButton.style.display = 'none';
                this.elements.pauseButton.style.display = 'flex'; // Use flex to match CSS
            } else {
                this.elements.playButton.style.display = 'flex';
                this.elements.pauseButton.style.display = 'none';
            }
        }
    }

    _showStatus(message, type = 'info') {
        if (this.elements.statusMessage) {
            this.elements.statusMessage.textContent = message;
            this.elements.statusMessage.className = `status-${type}`;
            
            if (type === 'info') {
                setTimeout(() => {
                    if (this.elements.statusMessage) {
                        this.elements.statusMessage.textContent = '';
                    }
                }, 3000);
            }
        }
    }

    // Observer pattern - called by PlayerService
    update(eventType, data) {
        switch (eventType) {
            case 'album_loaded':
                break;
                
            case 'track_started':
                console.log('UI: track_started event received', data);
                this._updateSongInfo(data);
                // Try to update controls immediately, then again when playback starts
                this._updatePlaybackControls();
                // Also check again after a delay in case audio takes time to start
                setTimeout(() => {
                    this._updatePlaybackControls();
                }, 500);
                break;
                
            case 'playback_started':
                console.log('UI: playback_started event received');
                // Audio actually started playing - update controls now
                this._updatePlaybackControls();
                break;
                
            case 'track_paused':
                this._updatePlaybackControls();
                break;
                
            case 'track_stopped':
                this._updatePlaybackControls();
                break;
                
            case 'volume_changed':
                if (this.elements.volumeSlider) {
                    this.elements.volumeSlider.value = data; // Already 0-1 range
                }
                break;
        }
    }

    _updateSongInfo(song) {
        if (!song) return;
        
        if (this.elements.songTitle) {
            this.elements.songTitle.textContent = song.title || 'Unknown Title';
        }
        
        if (this.elements.songArtist) {
            this.elements.songArtist.textContent = song.artist || 'Unknown Artist';
        }
        
        // Show placeholder artwork
        if (this.elements.artworkPlaceholder) {
            this.elements.artworkPlaceholder.style.display = 'flex';
        }
        if (this.elements.albumArt) {
            this.elements.albumArt.style.display = 'none';
        }
    }
}

