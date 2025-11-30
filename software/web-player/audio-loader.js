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

    // Find all audio files (ignore __MACOSX and other system files)
    const audioExtensions = ['.mp3', '.flac', '.wav', '.m4a', '.aac', '.ogg', '.opus'];
    const audioFiles = [];
    
    zip.forEach((relativePath, zipEntry) => {
        if (zipEntry.dir) return;
        if (relativePath.includes('__MACOSX')) return;
        
        const fileName = relativePath.split('/').pop();
        const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase();
        
        if (audioExtensions.includes(ext)) {
            audioFiles.push({
                path: relativePath,
                name: fileName,
                entry: zipEntry,
                extension: ext
            });
        }
    });

    if (audioFiles.length === 0) {
        throw new Error('No audio files found in .playt archive');
    }

    // Sort audio files by name
    audioFiles.sort((a, b) => a.name.localeCompare(b.name));

    // Create songs from audio files
    const songs = [];
    const baseUrl = URL.createObjectURL(file);
    
    for (let i = 0; i < audioFiles.length; i++) {
        const audioFile = audioFiles[i];
        const blob = await audioFile.entry.async('blob');
        const blobUrl = URL.createObjectURL(blob);
        
        // Extract title from filename (remove extension)
        const title = audioFile.name.substring(0, audioFile.name.lastIndexOf('.'));

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
        songs: songs
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

