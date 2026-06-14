function playSound(filename) {
    if (!filename) return;

    // Isolate just the filename.
    const cleanName = filename.split('/').pop();

    // Call the background Flask server to trigger Android's native MediaPlayer.
    fetch(`/api/play/${cleanName}`)
        .catch(err => console.error("Native sound playback request failed:", err));
}

// Automatically check for and trigger page-load sound requirements once the DOM mounts.
document.addEventListener('DOMContentLoaded', function() {
    const audioMarker = document.getElementById('page-audio-track');

    if (audioMarker) {
        const soundUrl = audioMarker.getAttribute('data-url');
        playSound(soundUrl);
    }
});