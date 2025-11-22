document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const elTrackTitle = document.getElementById('track-title');
    const elTrackArtist = document.getElementById('track-artist');
    const elCurrentTime = document.getElementById('current-time');
    const elTotalTime = document.getElementById('total-time');
    const elProgressBar = document.getElementById('progress-bar');
    const btnPlay = document.getElementById('btn-play');
    const iconPlay = document.getElementById('icon-play');
    const iconPause = document.getElementById('icon-pause');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');
    const btnLoad = document.getElementById('btn-load');
    const elVolume = document.getElementById('volume-slider');
    const elAlbumArt = document.getElementById('album-art');
    const elArtworkPlaceholder = document.getElementById('artwork-placeholder');

    // State
    let isDragging = false;
    let duration = 0;
    let isPlaying = false;

    // Wait for Python bridge
    function waitForBridge() {
        if (window.playt) {
            init();
        } else {
            setTimeout(waitForBridge, 50);
        }
    }
    waitForBridge();

    function init() {
        console.log("Bridge connected");
        
        // Subscribe to events
        window.playt.onTrackChange(handleTrackChange);
        window.playt.onPlaybackState(handlePlaybackState);
        window.playt.onProgress(handleProgress);
        
        // Tell Python we are ready
        if (window.playt.onReady) {
            window.playt.onReady(() => console.log("UI Ready"));
        }
    }

    // --- Event Handlers ---

    function handleTrackChange(track) {
        elTrackTitle.textContent = track.title || "Unknown Title";
        elTrackArtist.textContent = track.artist || "Unknown Artist";
        duration = track.duration || 0;
        elTotalTime.textContent = formatTime(duration);
        elProgressBar.max = duration;
        elProgressBar.disabled = false;
        
        // Update cover art
        if (track.coverArt) {
            elAlbumArt.src = track.coverArt;
            elAlbumArt.style.display = 'block';
            elArtworkPlaceholder.style.display = 'none';
        } else {
            elAlbumArt.style.display = 'none';
            elArtworkPlaceholder.style.display = 'flex';
        }

        if (!isDragging) {
            elProgressBar.value = 0;
            elCurrentTime.textContent = "0:00";
        }
    }

    function handlePlaybackState(state) {
        isPlaying = (state === 'playing');
        updatePlayButton();
    }

    function handleProgress(time) {
        if (!isDragging) {
            elProgressBar.value = time;
            elCurrentTime.textContent = formatTime(time);
        }
    }

    // --- UI Actions ---

    btnPlay.addEventListener('click', () => {
        console.log("Play clicked");
        window.playt.togglePlay();
    });

    btnNext.addEventListener('click', () => {
        console.log("Next clicked");
        window.playt.next();
    });

    btnPrev.addEventListener('click', () => {
        console.log("Prev clicked");
        window.playt.previous();
    });

    btnLoad.addEventListener('click', () => {
        if (window.playt.loadCartridge) {
            window.playt.loadCartridge();
        } else {
            console.error("loadCartridge not supported by bridge");
        }
    });

    // Progress Bar Interaction
    elProgressBar.addEventListener('input', () => {
        isDragging = true;
        elCurrentTime.textContent = formatTime(elProgressBar.value);
    });

    elProgressBar.addEventListener('change', () => {
        isDragging = false;
        window.playt.seek(elProgressBar.value);
    });

    // Volume Interaction
    elVolume.addEventListener('change', () => {
        window.playt.setVolume(parseFloat(elVolume.value));
    });

    // Keyboard Shortcuts
    document.addEventListener('keydown', (e) => {
        // Ignore if typing in an input (though we don't have inputs here really)
        if (e.target.tagName === 'INPUT' && e.target.type === 'text') return;

        switch(e.code) {
            case 'Space':
                e.preventDefault();
                window.playt.togglePlay();
                break;
            case 'ArrowLeft':
                window.playt.previous();
                break;
            case 'ArrowRight':
                window.playt.next();
                break;
            case 'ArrowUp':
                e.preventDefault();
                elVolume.value = Math.min(1, parseFloat(elVolume.value) + 0.05);
                window.playt.setVolume(parseFloat(elVolume.value));
                break;
            case 'ArrowDown':
                e.preventDefault();
                elVolume.value = Math.max(0, parseFloat(elVolume.value) - 0.05);
                window.playt.setVolume(parseFloat(elVolume.value));
                break;
        }
    });

    // --- Helpers ---

    function updatePlayButton() {
        if (isPlaying) {
            iconPlay.style.display = 'none';
            iconPause.style.display = 'block';
        } else {
            iconPlay.style.display = 'block';
            iconPause.style.display = 'none';
        }
    }

    function formatTime(seconds) {
        if (!seconds || isNaN(seconds)) return "0:00";
        const m = Math.floor(seconds / 60);
        const s = Math.floor(seconds % 60);
        return `${m}:${s.toString().padStart(2, '0')}`;
    }
});
