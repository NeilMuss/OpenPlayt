/**
 * Audio Loader - Handles loading .playt cartridge files
 * Supports loading zip archives containing audio files
 */

/**
 * Load a .playt file (zip archive) and extract audio files
 * @param {File} file - The .playt file to load
 * @returns {Promise<Album>} Album object with songs
 */
export async function loadPlaytFile(file) {
    if (!file.name.endsWith('.playt')) {
        throw new Error('File must have .playt extension');
    }

    // Use JSZip to extract the zip file
    const JSZip = (await import('https://cdn.jsdelivr.net/npm/jszip@3.10.1/+esm')).default;
    const zip = await JSZip.loadAsync(file);

    // Find all audio files and album art
    const audioExtensions = ['.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.opus'];
    const imageExtensions = ['.jpg', '.jpeg', '.png'];
    const audioFiles = [];
    let albumArtEntry = null;
    
    zip.forEach((relativePath, zipEntry) => {
        if (zipEntry.dir) return;
        if (relativePath.startsWith('__MACOSX/')) return;

        const originalFileName = relativePath.split('/').pop();
        if (!originalFileName) return;
        
        const lowerFileName = originalFileName.toLowerCase();
        const extIndex = lowerFileName.lastIndexOf('.');
        const ext = extIndex !== -1 ? lowerFileName.substring(extIndex) : '';

        if (audioExtensions.includes(ext)) {
            audioFiles.push({
                path: relativePath,
                name: originalFileName, // Preserve original case
                entry: zipEntry,
                extension: ext
            });
        } else if (imageExtensions.includes(ext) && (lowerFileName.includes('cover') || lowerFileName.includes('folder'))) {
            if (!albumArtEntry) { // Take the first one found
                albumArtEntry = zipEntry;
            }
        }
    });

    if (audioFiles.length === 0) {
        throw new Error('No audio files found in .playt archive');
    }

    // Sort audio files by original name
    audioFiles.sort((a, b) => a.name.localeCompare(b.name));

    // Extract album art if found
    let albumArtUrl = null;
    if (albumArtEntry) {
        const artBlob = await albumArtEntry.async('blob');
        albumArtUrl = URL.createObjectURL(artBlob);
    }

    // Create songs from audio files
    const songs = [];
    
    for (let i = 0; i < audioFiles.length; i++) {
        const audioFile = audioFiles[i];
        const blob = await audioFile.entry.async('blob');
        const blobUrl = URL.createObjectURL(blob);
        
        // Extract title from filename (remove extension)
        const extIndex = audioFile.name.lastIndexOf('.');
        const title = extIndex !== -1 ? audioFile.name.substring(0, extIndex) : audioFile.name;

        // Create song object
        const song = {
            title: title,
            artist: 'Unknown Artist',
            album: file.name.replace('.playt', ''),
            duration_secs: null, // Will be determined when audio loads
            file_path: blobUrl,
            track_number: i + 1,
            metadata: {}
        };

        songs.push(song);
    }

    // Create album
    const album = {
        title: file.name.replace('.playt', ''),
        artist: 'Unknown Artist',
        year: null,
        genre: null,
        songs: songs,
        album_art_url: albumArtUrl
    };

    return album;
}

/**
 * Get audio duration from a blob URL
 * @param {string} blobUrl - URL to the audio blob
 * @returns {Promise<number>} Duration in seconds
 */
export async function getAudioDuration(blobUrl) {
    return new Promise((resolve, reject) => {
        const audio = new Audio();
        audio.addEventListener('loadedmetadata', () => {
            resolve(audio.duration);
        });
        audio.addEventListener('error', (e) => {
            reject(new Error('Failed to load audio metadata: ' + e.message));
        });
        audio.src = blobUrl;
    });
}

