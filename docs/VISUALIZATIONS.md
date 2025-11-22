# Music Visualizations in PLAYT Advanced Themes

PLAYT now supports rich, animated music visualizations within Advanced Themes using a new Visualization API exposed to the WebView JavaScript environment. Artists can leverage Canvas, WebGL, SVG, or p5.js to create dynamic visual experiences that react to the music.

## 1. Audio Analysis Layer

The backend now includes an audio analysis layer that processes the live audio stream and computes several metrics:

*   **Spectrum (FFT):** Provides frequency distribution data (default 64 bands).
*   **Waveform:** Time-domain amplitude samples, representing the raw audio signal.
*   **RMS (Root Mean Square):** An overall loudness measurement of the audio.
*   **Beat Detection:** A simple energy-based model to detect prominent beats.

These analysis results are continuously emitted as events at approximately 20-30 frames per second via the existing observer system.

## 2. Exposing the Visualization API to Advanced Themes

Within the WebView's JavaScript environment, a global `window.playt` object is now available, providing access to visualization data and utilities:

### Audio Analysis Callbacks

You can register callback functions to receive real-time audio analysis data:

*   `window.playt.onSpectrum(cb)`: Registers a callback `cb(bands: number[])` which is invoked with an array of numbers representing the spectrum bands.
*   `window.playt.onWaveform(cb)`: Registers a callback `cb(samples: number[])` which is invoked with an array of numbers representing the raw audio waveform samples.
*   `window.playt.onRMS(cb)`: Registers a callback `cb(value: number)` which is invoked with a single number representing the overall RMS (loudness).
*   `window.playt.onBeat(cb)`: Registers a callback `cb(beat: boolean)` which is invoked with a boolean indicating if a beat was detected.

### Album Art Colors

You can also retrieve a color palette extracted from the current album art:

*   `window.playt.getAlbumArtColors()`: This function, when called, returns an object `{primary, secondary, background}` where each property is an RGB tuple `[R, G, B]` representing dominant colors from the album cover (`cover.jpg`). This is useful for theming your visualizations to match the current track.

**Example Usage in JavaScript:**

```javascript
// Connect to the WebSocket server
const ws = new WebSocket("ws://localhost:8765"); // Adjust host/port if needed

ws.onopen = () => {
    console.log("Connected to PLAYT WebSocket.");
    // Request album art colors
    ws.send(JSON.stringify({ type: "getAlbumArtColors" }));
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data);
    if (msg.event_type === "audio_analysis") {
        // Update your visualization based on msg.data:
        // spectrumData = msg.data.spectrum;
        // waveformData = msg.data.waveform;
        // rmsValue = msg.data.rms;
        // isBeat = msg.data.beat;

        // Example: log RMS
        // console.log("RMS:", msg.data.rms);
    } else if (msg.event_type === "album_art_colors") {
        if (msg.data) {
            const { primary, secondary, background } = msg.data;
            console.log("Album Art Colors:", primary, secondary, background);
            // Use these colors to theme your visualization
        }
    }
};

ws.onclose = () => {
    console.log("Disconnected from PLAYT WebSocket.");
    // Implement reconnection logic if desired
};

ws.onerror = (error) => {
    console.error("WebSocket Error:", error);
};

// In your application logic, you might have functions like these
// to simulate the window.playt API calls, using the WebSocket:

function onSpectrum(callback) {
    // Internally, listen to 'audio_analysis' events from WebSocket
    // and extract spectrum data to call the callback.
}

function onWaveform(callback) {
    // ...
}

function onRMS(callback) {
    // ...
}

function onBeat(callback) {
    // ...
}

function getAlbumArtColors() {
    // Send a message over WebSocket to request colors
    // and handle the response asynchronously.
}
```

## 3. How to Draw with Canvas or WebGL

For animated visuals, `Canvas` and `WebGL` are the recommended technologies due to their performance.

*   **Canvas 2D:** Ideal for simpler visualizations like bar graphs (spectrum), line graphs (waveform), and basic shapes.
    *   Get a reference to your canvas element and its 2D rendering context:
        ```javascript
        const canvas = document.getElementById('myCanvas');
        const ctx = canvas.getContext('2d');
        ```
    *   In your animation loop (e.g., using `requestAnimationFrame`), clear the canvas and redraw based on the latest `onSpectrum`, `onWaveform`, etc., data.
*   **WebGL:** For complex 3D or highly performant 2D graphics. This requires more advanced JavaScript and shader programming.
    *   Initialize a WebGL context:
        ```javascript
        const canvas = document.getElementById('myWebGLCanvas');
        const gl = canvas.getContext('webgl');
        if (!gl) { /* handle error */ }
        ```
    *   Update vertex buffers and uniforms with visualization data in your render loop.

## 4. Simple Amplitude-Based Animations

You can create dynamic animations by mapping audio analysis values directly to visual properties:

*   **Spectrum to Bar Height:** For a classic equalizer look, map each spectrum band's value to the height of a corresponding rectangle.
*   **RMS to Size/Brightness:** Make elements pulse or glow brighter based on the `rms` value.
*   **Beat to Flashes/Jumps:** Trigger a brief visual effect (e.g., screen flash, element jump) when `onBeat` is true.

## 5. Adding p5.js

p5.js is a JavaScript library for creative coding, making it easier to draw with Canvas.

1.  **Include p5.js:** Add the p5.js library to your `index.html`:
    ```html
    <script src="https://cdnjs.cloudflare.com/ajax/libs/p5.js/1.4.0/p5.js"></script>
    ```
2.  **Integrate:** Write your p5.js sketch in `app.js` (or a separate file) and use the `window.playt` API within `setup()` or `draw()` functions.
    ```javascript
    let spectrumData = [];
    let rmsValue = 0;

    function setup() {
        createCanvas(windowWidth, windowHeight);
        // Register callbacks
        window.playt.onSpectrum(bands => { spectrumData = bands; });
        window.playt.onRMS(rms => { rmsValue = rms; });
    }

    function draw() {
        background(0); // Black background
        fill(255, 0, 0); // Red color
        // Draw spectrum bars
        for (let i = 0; i < spectrumData.length; i++) {
            let x = map(i, 0, spectrumData.length, 0, width);
            let h = map(spectrumData[i], 0, 255, 0, height); // Adjust mapping as needed
            rect(x, height - h, width / spectrumData.length, h);
        }
        // Draw a pulsing circle based on RMS
        ellipse(width / 2, height / 2, rmsValue * 0.1, rmsValue * 0.1);
    }
    ```

## 6. Performance Tips

*   **Optimize Drawing:** Minimize redraws. Only update elements that have changed.
*   **Batch Operations:** Group multiple drawing commands together.
*   **Offscreen Canvas:** For complex intermediate calculations or effects, use an offscreen canvas.
*   **`requestAnimationFrame`:** Always use `requestAnimationFrame` for animation loops for smoother visuals and battery efficiency.
*   **Limit Data Processing:** Avoid heavy computations directly in your `onSpectrum` or `onWaveform` callbacks. Instead, store the data and process it efficiently in your animation loop.
*   **Reduce WebSocket Traffic:** If you only need certain data (e.g., just RMS), consider filtering or requesting only that data from the backend (future enhancement).

This documentation provides a guide to developing dynamic music visualizations for PLAYT's Advanced Themes, enabling artists to create engaging and reactive visual experiences.
