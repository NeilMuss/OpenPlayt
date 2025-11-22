// Assuming a global `window.playt` object will be exposed by the WebView
// For now, we'll connect directly to the WebSocket server

const WS_URL = "ws://localhost:8765"; // Needs to be configurable or passed by the WebView

let ws;
let spectrumData = [];
let waveformData = [];
let rmsValue = 0;
let isBeat = false;
let albumArtColors = { primary: [0, 0, 0], secondary: [0, 0, 0], background: [0, 0, 0] };

// Canvas setup
const spectrumCanvas = document.getElementById('spectrumCanvas');
const spectrumCtx = spectrumCanvas.getContext('2d');
const waveformCanvas = document.getElementById('waveformCanvas');
const waveformCtx = waveformCanvas.getContext('2d');

let animationFrameId;

function resizeCanvases() {
    spectrumCanvas.width = window.innerWidth;
    spectrumCanvas.height = window.innerHeight;
    waveformCanvas.width = window.innerWidth;
    waveformCanvas.height = window.innerHeight;
}

window.addEventListener('resize', resizeCanvases);
resizeCanvases();


function drawSpectrum() {
    spectrumCtx.clearRect(0, 0, spectrumCanvas.width, spectrumCanvas.height);
    const barWidth = spectrumCanvas.width / spectrumData.length;
    spectrumData.forEach((value, i) => {
        const barHeight = (value / 255) * spectrumCanvas.height; // Assuming max value is 255
        spectrumCtx.fillStyle = `rgb(${albumArtColors.primary[0]}, ${albumArtColors.primary[1]}, ${albumArtColors.primary[2]})`;
        spectrumCtx.fillRect(i * barWidth, spectrumCanvas.height - barHeight, barWidth, barHeight);
    });
}

function drawWaveform() {
    waveformCtx.clearRect(0, 0, waveformCanvas.width, waveformCanvas.height);
    waveformCtx.beginPath();
    waveformCtx.moveTo(0, waveformCanvas.height / 2);

    const sliceWidth = waveformCanvas.width * 1.0 / waveformData.length;
    let x = 0;
    for (let i = 0; i < waveformData.length; i++) {
        const v = waveformData[i] / 32768; // Assuming 16-bit audio
        const y = (v * waveformCanvas.height / 2) + waveformCanvas.height / 2;
        waveformCtx.lineTo(x, y);
        x += sliceWidth;
    }
    waveformCtx.lineTo(waveformCanvas.width, waveformCanvas.height / 2);
    waveformCtx.strokeStyle = `rgb(${albumArtColors.secondary[0]}, ${albumArtColors.secondary[1]}, ${albumArtColors.secondary[2]})`;
    waveformCtx.stroke();
}

function updateRMSRing() {
    const rmsRing = document.getElementById('rms-ring');
    const size = rmsValue * 0.1; // Scale RMS value for visual effect
    rmsRing.style.width = `${size}px`;
    rmsRing.style.height = `${size}px`;
    rmsRing.style.opacity = Math.min(rmsValue / 5000, 1); // Max opacity at RMS 5000
    rmsRing.style.borderColor = `rgb(${albumArtColors.background[0]}, ${albumArtColors.background[1]}, ${albumArtColors.background[2]})`;
    rmsRing.style.left = `calc(50% - ${size / 2}px)`;
    rmsRing.style.top = `calc(50% - ${size / 2}px)`;
}

function updateBeatFlash() {
    const beatFlash = document.getElementById('beat-flash');
    if (isBeat) {
        beatFlash.style.opacity = 0.8;
    } else {
        beatFlash.style.opacity = 0;
    }
}

function animate() {
    drawSpectrum();
    drawWaveform();
    updateRMSRing();
    updateBeatFlash();
    animationFrameId = requestAnimationFrame(animate);
}

function connectWebSocket() {
    ws = new WebSocket(WS_URL);

    ws.onopen = () => {
        console.log("WebSocket connected!");
        // Request album art colors on connect
        ws.send(JSON.stringify({ type: "getAlbumArtColors" }));
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        if (msg.event_type === "audio_analysis") {
            spectrumData = msg.data.spectrum;
            waveformData = msg.data.waveform;
            rmsValue = msg.data.rms;
            isBeat = msg.data.beat;
        } else if (msg.event_type === "album_art_colors") {
            if (msg.data) {
                albumArtColors = msg.data;
                console.log("Album Art Colors:", albumArtColors);
            }
        }
    };

    ws.onclose = () => {
        console.log("WebSocket disconnected. Reconnecting in 5 seconds...");
        setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (err) => {
        console.error("WebSocket error:", err);
        ws.close();
    };
}

// Start visualization
animate();
connectWebSocket();
