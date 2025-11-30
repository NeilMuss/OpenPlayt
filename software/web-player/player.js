/**
 * Player Service - Core playback logic with observer pattern
 * Manages queue, playback state, and notifications
 */

/**
 * Observer pattern implementation
 */
class Subject {
    constructor() {
        this._observers = [];
    }

    attach(observer) {
        if (!this._observers.includes(observer)) {
            this._observers.push(observer);
        }
    }

    detach(observer) {
        const index = this._observers.indexOf(observer);
        if (index > -1) {
            this._observers.splice(index, 1);
        }
    }

    notify(eventType, data) {
        this._observers.forEach(observer => {
            if (observer && typeof observer.update === 'function') {
                observer.update(eventType, data);
            }
        });
    }
}

/**
 * Web Audio Player - Uses HTML5 Audio API
 */
class WebAudioPlayer {
    constructor() {
        this._audio = null;
        this._state = 'idle';
        this._currentUrl = null;
        this._volume = 1.0;
        this._position = 0.0;
        this._duration = 0.0;
        
        // Track position updates
        this._positionInterval = null;
        
        // Callback for track ended
        this._onTrackEnded = null;
    }

    setOnTrackEnded(callback) {
        this._onTrackEnded = callback;
    }

    play(filePath) {
        // If already playing this file, do nothing
        if (this._currentUrl === filePath && this._state === 'playing') {
            return;
        }

        // Stop current playback if any
        this.stop();

        // Create new audio element
        this._audio = new Audio(filePath);
        this._audio.volume = this._volume;
        this._currentUrl = filePath;
        this._state = 'loading';

        // Set up event handlers
        this._audio.addEventListener('loadedmetadata', () => {
            this._duration = this._audio.duration;
        });

        this._audio.addEventListener('canplay', () => {
            // Audio has enough data to start playing
            console.log('Audio canplay event, readyState:', this._audio.readyState);
            if (this._state === 'loading') {
                this._startPlayback();
            }
        });

        this._audio.addEventListener('canplaythrough', () => {
            // Audio is fully ready to play
            console.log('Audio canplaythrough event, readyState:', this._audio.readyState);
            if (this._state === 'loading') {
                this._startPlayback();
            }
        });

        this._audio.addEventListener('ended', () => {
            const previousUrl = this._currentUrl;
            this._state = 'idle';
            this._currentUrl = null;
            this._position = 0.0;
            if (this._positionInterval) {
                clearInterval(this._positionInterval);
                this._positionInterval = null;
            }
            // Notify that track ended (will be handled by PlayerService)
            if (this._onTrackEnded) {
                this._onTrackEnded(previousUrl);
            }
        });

        this._audio.addEventListener('error', (e) => {
            console.error('Audio playback error:', e);
            if (this._audio.error) {
                console.error('Audio error code:', this._audio.error.code);
                console.error('Audio error message:', this._audio.error.message);
            }
            console.error('Audio src:', this._audio.src);
            console.error('Audio readyState:', this._audio.readyState);
            this._state = 'idle';
        });

        // Debug: Log when audio starts loading
        this._audio.addEventListener('loadstart', () => {
            console.log('Audio load started:', filePath);
        });

        // Load the audio (triggers loading)
        this._audio.load();
        
        // Also try playing when loadeddata fires as a fallback
        this._audio.addEventListener('loadeddata', () => {
            console.log('Audio loadeddata event, readyState:', this._audio.readyState);
            if (this._state === 'loading') {
                this._startPlayback();
            }
        }, { once: true });
        
        // Final fallback: try after 2 seconds if still loading
        setTimeout(() => {
            if (this._state === 'loading' && this._audio) {
                console.log('Timeout fallback: attempting to play, readyState:', this._audio.readyState);
                this._startPlayback();
            }
        }, 2000);
    }

    _startPlayback() {
        if (!this._audio) {
            console.warn('_startPlayback called but _audio is null');
            return;
        }
        
        console.log('Starting playback, readyState:', this._audio.readyState);
        console.log('Audio src:', this._audio.src.substring(0, 50) + '...');
        
        // Only attempt to play if we have enough data
        if (this._audio.readyState < 2) {
            console.log('Not enough data loaded yet (readyState:', this._audio.readyState + '), waiting...');
            return;
        }
        
        this._audio.play().then(() => {
            console.log('Playback started successfully');
            this._state = 'playing';
            this._startPositionTracking();
        }).catch(err => {
            console.error('Failed to play audio:', err);
            console.error('Error name:', err.name);
            console.error('Error message:', err.message);
            // If autoplay is blocked, keep audio loaded but set state to paused
            if (err.name === 'NotAllowedError' || err.name === 'NotSupportedError') {
                this._state = 'paused';
                console.log('Autoplay blocked. Audio is ready, user can click play. State set to paused.');
            } else {
                // Other errors - might be format issue or corrupted file
                console.error('Audio playback error - file might not be supported or corrupted');
                this._state = 'idle';
            }
        });
    }

    pause() {
        if (this._audio && this._state === 'playing') {
            this._audio.pause();
            this._state = 'paused';
            this._stopPositionTracking();
        }
    }

    resume() {
        if (this._audio && this._state === 'paused') {
            console.log('Resuming audio playback');
            this._audio.play().then(() => {
                this._state = 'playing';
                this._startPositionTracking();
            }).catch(err => {
                console.error('Failed to resume audio:', err);
                // If resume fails, try starting from beginning
                if (this._currentUrl) {
                    console.log('Resume failed, trying to start fresh');
                    this.play(this._currentUrl);
                }
            });
        } else if (!this._audio && this._currentUrl) {
            // Audio element was lost, recreate it
            console.log('Audio element lost, recreating from URL:', this._currentUrl);
            this.play(this._currentUrl);
        }
    }

    stop() {
        if (this._audio) {
            this._audio.pause();
            this._audio.currentTime = 0;
            this._audio = null;
        }
        this._state = 'idle';
        this._currentUrl = null;
        this._position = 0.0;
        this._duration = 0.0;
        this._stopPositionTracking();
    }

    seek(positionSecs) {
        if (this._audio) {
            this._audio.currentTime = positionSecs;
            this._position = positionSecs;
        }
    }

    setVolume(volume) {
        this._volume = Math.max(0.0, Math.min(1.0, volume));
        if (this._audio) {
            this._audio.volume = this._volume;
        }
    }

    getPosition() {
        if (this._audio && this._state !== 'idle') {
            return this._audio.currentTime;
        }
        return null;
    }

    getDuration() {
        return this._duration;
    }

    getState() {
        return this._state;
    }

    isPlaying() {
        return this._state === 'playing';
    }

    _startPositionTracking() {
        this._stopPositionTracking();
        this._positionInterval = setInterval(() => {
            if (this._audio) {
                this._position = this._audio.currentTime;
            }
        }, 100);
    }

    _stopPositionTracking() {
        if (this._positionInterval) {
            clearInterval(this._positionInterval);
            this._positionInterval = null;
        }
    }
}

/**
 * Player Service - Manages queue and playback coordination
 */
export class PlayerService extends Subject {
    constructor() {
        super();
        this._audioPlayer = new WebAudioPlayer();
        this._currentSong = null;
        this._queue = [];
        this._currentIndex = -1;
        
        // Set up auto-advance callback
        this._audioPlayer.setOnTrackEnded(() => {
            this._handleTrackEnded();
        });
    }

    loadAlbum(album) {
        // Sort songs by track number
        const orderedSongs = [...album.songs].sort((a, b) => {
            const trackA = a.track_number ?? 999;
            const trackB = b.track_number ?? 999;
            if (trackA !== trackB) return trackA - trackB;
            return a.title.localeCompare(b.title);
        });

        this._queue = orderedSongs;
        this._currentIndex = -1;
        this._currentSong = null;
        this.notify('album_loaded', album);
    }

    loadQueue(songs) {
        this._queue = [...songs];
        this._currentIndex = -1;
        this._currentSong = null;
        this.notify('queue_loaded', songs);
    }

    play() {
        console.log('PlayerService.play() called');
        
        if (this._currentSong === null && this._queue.length > 0) {
            console.log('Setting current song to first in queue');
            this._currentIndex = 0;
            this._currentSong = this._queue[0];
            console.log('Current song:', this._currentSong);
        }

        if (this._currentSong) {
            const state = this._audioPlayer.getState();
            console.log('Current audio player state:', state);
            
            if (state === 'paused' && this._audioPlayer._currentUrl === this._currentSong.file_path) {
                console.log('Resuming paused audio');
                this._audioPlayer.resume();
            } else {
                console.log('Starting new playback:', this._currentSong.file_path);
                // Always call play with the file path - let the audio player handle state
                this._audioPlayer.play(this._currentSong.file_path);
            }
            this.notify('track_started', this._currentSong);
        } else {
            console.warn('No current song to play');
        }
    }

    pause() {
        if (this._audioPlayer.isPlaying()) {
            this._audioPlayer.pause();
            if (this._currentSong) {
                this.notify('track_paused', this._currentSong);
            }
        }
    }

    stop() {
        this._audioPlayer.stop();
        if (this._currentSong) {
            this.notify('track_stopped', this._currentSong);
        }
        this._currentSong = null;
        this._currentIndex = -1;
    }

    next() {
        if (this._queue.length === 0) return;

        if (this._currentIndex < this._queue.length - 1) {
            this._currentIndex += 1;
            this._currentSong = this._queue[this._currentIndex];
            this._audioPlayer.play(this._currentSong.file_path);
            this.notify('track_started', this._currentSong);
        } else {
            this.stop();
            this.notify('queue_ended', null);
        }
    }

    previous() {
        if (this._queue.length === 0) return;

        if (this._currentIndex > 0) {
            this._currentIndex -= 1;
            this._currentSong = this._queue[this._currentIndex];
            this._audioPlayer.play(this._currentSong.file_path);
            this.notify('track_started', this._currentSong);
        } else {
            // Restart current track
            if (this._currentSong) {
                this._audioPlayer.play(this._currentSong.file_path);
                this.notify('track_started', this._currentSong);
            }
        }
    }

    seek(positionSecs) {
        this._audioPlayer.seek(positionSecs);
        this.notify('seeked', {
            position: positionSecs,
            song: this._currentSong
        });
    }

    setVolume(volume) {
        this._audioPlayer.setVolume(volume);
        this.notify('volume_changed', volume);
    }

    getCurrentSong() {
        return this._currentSong;
    }

    getQueue() {
        return [...this._queue];
    }

    getState() {
        return this._audioPlayer.getState();
    }

    getPosition() {
        return this._audioPlayer.getPosition();
    }

    getDuration() {
        return this._audioPlayer.getDuration();
    }

    _handleTrackEnded() {
        // Only auto-advance if we still have a current song (wasn't manually stopped)
        if (this._currentSong === null) {
            return; // Was manually stopped, don't auto-advance
        }
        
        // Auto-advance to next track
        if (this._currentIndex < this._queue.length - 1) {
            this.next();
        } else {
            this.stop();
            this.notify('queue_ended', null);
        }
    }
}

