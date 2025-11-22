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
    const cbSlideshow = document.getElementById('cb-slideshow');

    // State
    let isDragging = false;
    let duration = 0;
    let isPlaying = false;
    let slideshowInterval = null;
    let slideshowImages = [];
    let currentImageIndex = 0;
    let currentCoverArt = null;
    let isSlideshowEnabled = true;

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
        
        // Debug: Check Charset
        console.log("Document Character Set:", document.characterSet);
        if (document.characterSet !== "UTF-8") {
            console.error("CRITICAL: Document is not UTF-8!");
        }
        
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
        // Debug: Inspect data integrity
        if (track.title) {
            console.log("TITLE RAW:", track.title);
            console.log("CHAR CODES:", [...track.title].map(c => c.charCodeAt(0)));
        }

        // Normalize strings
        const title = (track.title || "Unknown Title").normalize('NFC');
        const artist = (track.artist || "Unknown Artist").normalize('NFC');

        elTrackTitle.textContent = title;
        elTrackArtist.textContent = artist;
        duration = track.duration || 0;
        elTotalTime.textContent = formatTime(duration);
        elProgressBar.max = duration;
        elProgressBar.disabled = false;
        
        // Update cover art and slideshow
        currentCoverArt = track.coverArt || null;
        slideshowImages = track.slideshowImages || [];
        
        // Stop any existing slideshow
        stopSlideshow();
        
        if (currentCoverArt) {
            elAlbumArt.src = currentCoverArt;
            elAlbumArt.style.display = 'block';
            elArtworkPlaceholder.style.display = 'none';
        } else {
            elAlbumArt.style.display = 'none';
            elArtworkPlaceholder.style.display = 'flex';
        }
        
        // Start slideshow if playing and we have images
        if (isPlaying && slideshowImages.length > 0 && isSlideshowEnabled) {
            startSlideshow();
        }

        if (!isDragging) {
            elProgressBar.value = 0;
            elCurrentTime.textContent = "0:00";
        }
    }

    function handlePlaybackState(state) {
        isPlaying = (state === 'playing');
        updatePlayButton();
        
        if (isPlaying) {
            if (slideshowImages.length > 0 && isSlideshowEnabled) {
                startSlideshow();
            }
        } else {
            stopSlideshow();
            // Reset to cover art when paused/stopped
            if (currentCoverArt) {
                 elAlbumArt.src = currentCoverArt;
            }
        }
    }

    function startSlideshow() {
        stopSlideshow(); // Ensure no duplicates
        
        // Start with the first image (or continue from where we left off? 
        // Let's start from index 0 or a random one. Let's try sequential for now.)
        // Actually, let's show the cover art first, then cycle?
        // Or just start cycling.
        
        // If we have images, cycle them every 15 seconds
        slideshowInterval = setInterval(() => {
             if (slideshowImages.length === 0) return;
             
             // Next image
             currentImageIndex = (currentImageIndex + 1) % slideshowImages.length;
             const nextImage = slideshowImages[currentImageIndex];
             
             // Create a fade effect maybe? For now just swap source
             elAlbumArt.src = nextImage;
             
        }, 15000); // 15 seconds
    }

    function stopSlideshow() {
        if (slideshowInterval) {
            clearInterval(slideshowInterval);
            slideshowInterval = null;
        }
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

    // Slideshow toggle
    if (cbSlideshow) {
        cbSlideshow.addEventListener('change', () => {
            isSlideshowEnabled = cbSlideshow.checked;
            if (isSlideshowEnabled) {
                if (isPlaying && slideshowImages.length > 0) {
                    startSlideshow();
                }
            } else {
                stopSlideshow();
                if (currentCoverArt) {
                    elAlbumArt.src = currentCoverArt;
                }
            }
        });
    }

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
