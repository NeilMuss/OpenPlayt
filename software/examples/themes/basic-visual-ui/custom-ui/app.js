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

        switch (e.code) {
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

    // --- Visualizer ---
    const btnVisualizer = document.getElementById('btn-visualizer');
    const btnCloseVisualizer = document.getElementById('btn-close-visualizer');
    const visualizerScreen = document.getElementById('visualizer-screen');
    const canvas = document.getElementById('visualizer-canvas');
    const ctx = canvas.getContext('2d');

    let visualizerActive = false;
    let animationId = null;
    let currentVisualizer = 'beat';  // Default to beat
    let config = {
        enabled: true,
        active_visualizer: 'beat',
        visualizers: {
            colorwash: { speed: 0.5 },
            pulse: { sensitivity: 1.0 },
            beat: { threshold: 1.6, cooldown_ms: 250, flash_intensity: 1.0 }
        }
    };

    // Visualizer state
    let hue = 0;
    let amplitude = 0.0;
    let beatIntensity = 0.0;  // For beat visualizer
    let rings = [];  // Active beat rings

    // Load config
    async function loadConfig() {
        try {
            // Config file in same directory as HTML
            const response = await fetch('visualizer_config.json');
            if (response.ok) {
                config = await response.json();
                currentVisualizer = config.active_visualizer || 'pulse';
                console.log('Loaded visualizer config:', currentVisualizer);
            } else {
                console.log('Config file not found, using pulse as default');
                currentVisualizer = 'pulse';
            }
        } catch (e) {
            console.log('Error loading config, using pulse as default:', e);
            currentVisualizer = 'pulse';
        }
    }

    // Set up amplitude listener when window.playt is ready
    function setupAmplitudeListener() {
        if (window.playt && window.playt.onAmplitude) {
            window.playt.onAmplitude(val => {
                amplitude = val;
            });
        } else {
            // Retry after a short delay if not ready yet
            setTimeout(setupAmplitudeListener, 100);
        }
    }

    // Set up beat listener when window.playt is ready
    function setupBeatListener() {
        if (window.playt && window.playt.onBeat) {
            window.playt.onBeat(() => {
                // Trigger beat visual
                beatIntensity = 1.0;
                // Add expanding ring
                rings.push({
                    radius: 0,
                    maxRadius: Math.min(canvas.width, canvas.height) * 0.6,
                    alpha: 1.0
                });
            });
        } else {
            // Retry after a short delay if not ready yet
            setTimeout(setupBeatListener, 100);
        }
    }

    // Start listening for amplitude and beats
    setupAmplitudeListener();
    setupBeatListener();

    // Resize canvas to fill screen
    function resizeCanvas() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }

    // Open visualizer
    function openVisualizer() {
        visualizerActive = true;
        visualizerScreen.style.display = 'block';
        resizeCanvas();
        loadConfig().then(() => {
            startAnimation();
        });
    }

    // Close visualizer
    function closeVisualizer() {
        visualizerActive = false;
        visualizerScreen.style.display = 'none';
        stopAnimation();
    }

    // Colorwash visualizer
    function animateColorwash() {
        const speed = config.visualizers.colorwash?.speed || 0.5;
        hue = (hue + (0.2 * speed)) % 360;

        const gradient = ctx.createLinearGradient(0, 0, canvas.width, canvas.height);
        gradient.addColorStop(0, `hsl(${hue}, 60%, 20%)`);
        gradient.addColorStop(0.5, `hsl(${(hue + 60) % 360}, 50%, 15%)`);
        gradient.addColorStop(1, `hsl(${(hue + 120) % 360}, 55%, 18%)`);

        ctx.fillStyle = gradient;
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    }

    // Pulse visualizer
    function animatePulse() {
        const sensitivity = config.visualizers.pulse?.sensitivity || 1.0;

        // Clear with dark background
        ctx.fillStyle = '#0a0a0a';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Calculate pulse size based on amplitude
        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;
        const baseRadius = Math.min(canvas.width, canvas.height) * 0.15;
        const pulseRadius = baseRadius + (amplitude * sensitivity * 200);

        // Draw pulsing circle with glow
        const gradient = ctx.createRadialGradient(
            centerX, centerY, 0,
            centerX, centerY, pulseRadius
        );

        // Color shifts slightly with amplitude
        const pulseHue = 200 + (amplitude * 60);
        gradient.addColorStop(0, `hsla(${pulseHue}, 70%, 60%, 0.8)`);
        gradient.addColorStop(0.5, `hsla(${pulseHue}, 60%, 50%, 0.4)`);
        gradient.addColorStop(1, `hsla(${pulseHue}, 50%, 40%, 0)`);

        ctx.fillStyle = gradient;
        ctx.beginPath();
        ctx.arc(centerX, centerY, pulseRadius, 0, Math.PI * 2);
        ctx.fill();
    }

    // Beat visualizer
    function animateBeat() {
        const flashIntensity = config.visualizers.beat?.flash_intensity || 1.0;

        // Background with flash effect
        const bgBrightness = 10 + (beatIntensity * 40 * flashIntensity);
        ctx.fillStyle = `rgb(${bgBrightness}, ${bgBrightness}, ${bgBrightness})`;
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        const centerX = canvas.width / 2;
        const centerY = canvas.height / 2;

        // Draw expanding rings
        for (let i = rings.length - 1; i >= 0; i--) {
            const ring = rings[i];

            // Update ring
            ring.radius += 8;
            ring.alpha -= 0.02;

            // Remove if faded out
            if (ring.alpha <= 0 || ring.radius > ring.maxRadius) {
                rings.splice(i, 1);
                continue;
            }

            // Draw ring
            ctx.strokeStyle = `rgba(100, 200, 255, ${ring.alpha})`;
            ctx.lineWidth = 4;
            ctx.beginPath();
            ctx.arc(centerX, centerY, ring.radius, 0, Math.PI * 2);
            ctx.stroke();
        }

        // Decay beat intensity
        beatIntensity *= 0.92;
    }

    // Main animation loop
    function animate() {
        if (!visualizerActive) return;

        animationId = requestAnimationFrame(animate);

        // Switch based on active visualizer
        if (currentVisualizer === 'pulse') {
            animatePulse();
        } else if (currentVisualizer === 'beat') {
            animateBeat();
        } else {
            animateColorwash();
        }
    }

    function startAnimation() {
        if (!animationId) {
            animate();
        }
    }

    function stopAnimation() {
        if (animationId) {
            cancelAnimationFrame(animationId);
            animationId = null;
        }
    }

    // On-screen feedback system
    let feedbackTimeout = null;

    function showFeedback(message) {
        // Create or get feedback element
        let feedback = document.getElementById('visualizer-feedback');
        if (!feedback) {
            feedback = document.createElement('div');
            feedback.id = 'visualizer-feedback';
            feedback.style.cssText = `
                position: fixed;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                background: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 20px 40px;
                border-radius: 10px;
                font-size: 24px;
                font-weight: bold;
                z-index: 2000;
                pointer-events: none;
                opacity: 0;
                transition: opacity 0.3s;
            `;
            document.body.appendChild(feedback);
        }

        feedback.textContent = message;
        feedback.style.opacity = '1';

        // Clear existing timeout
        if (feedbackTimeout) {
            clearTimeout(feedbackTimeout);
        }

        // Hide after 1.5 seconds
        feedbackTimeout = setTimeout(() => {
            feedback.style.opacity = '0';
        }, 1500);
    }

    // Event listeners
    if (btnVisualizer) {
        btnVisualizer.addEventListener('click', openVisualizer);
    }

    if (btnCloseVisualizer) {
        btnCloseVisualizer.addEventListener('click', closeVisualizer);
    }

    window.addEventListener('resize', () => {
        if (visualizerActive) {
            resizeCanvas();
        }
    });

    // Keyboard controls
    document.addEventListener('keydown', (e) => {
        if (!visualizerActive) return;

        // ESC to close
        if (e.key === 'Escape') {
            closeVisualizer();
            return;
        }

        // Tab or Space to cycle visualizers
        if (e.key === 'Tab' || e.key === ' ') {
            e.preventDefault();
            const visualizers = Object.keys(config.visualizers);
            const currentIndex = visualizers.indexOf(currentVisualizer);
            const nextIndex = (currentIndex + 1) % visualizers.length;
            currentVisualizer = visualizers[nextIndex];

            // Reset visualizer-specific state
            rings = [];
            beatIntensity = 0;

            showFeedback(`Visualizer: ${currentVisualizer}`);
            return;
        }

        // Arrow keys to adjust settings
        if (e.key.startsWith('Arrow')) {
            e.preventDefault();

            if (currentVisualizer === 'colorwash') {
                if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
                    config.visualizers.colorwash.speed = Math.min(2.0, config.visualizers.colorwash.speed + 0.1);
                    showFeedback(`Speed: ${config.visualizers.colorwash.speed.toFixed(1)}`);
                } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
                    config.visualizers.colorwash.speed = Math.max(0.1, config.visualizers.colorwash.speed - 0.1);
                    showFeedback(`Speed: ${config.visualizers.colorwash.speed.toFixed(1)}`);
                }
            } else if (currentVisualizer === 'pulse') {
                if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
                    config.visualizers.pulse.sensitivity = Math.min(3.0, config.visualizers.pulse.sensitivity + 0.1);
                    showFeedback(`Sensitivity: ${config.visualizers.pulse.sensitivity.toFixed(1)}`);
                } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
                    config.visualizers.pulse.sensitivity = Math.max(0.1, config.visualizers.pulse.sensitivity - 0.1);
                    showFeedback(`Sensitivity: ${config.visualizers.pulse.sensitivity.toFixed(1)}`);
                }
            } else if (currentVisualizer === 'beat') {
                if (e.key === 'ArrowUp' || e.key === 'ArrowRight') {
                    config.visualizers.beat.flash_intensity = Math.min(2.0, config.visualizers.beat.flash_intensity + 0.1);
                    showFeedback(`Flash Intensity: ${config.visualizers.beat.flash_intensity.toFixed(1)}`);
                } else if (e.key === 'ArrowDown' || e.key === 'ArrowLeft') {
                    config.visualizers.beat.flash_intensity = Math.max(0.1, config.visualizers.beat.flash_intensity - 0.1);
                    showFeedback(`Flash Intensity: ${config.visualizers.beat.flash_intensity.toFixed(1)}`);
                }
            }
        }
    });
});
