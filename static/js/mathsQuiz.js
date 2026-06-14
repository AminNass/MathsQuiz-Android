// Force the active page state into the history loop
history.pushState(null, null, location.href);

// Intercept any popstate actions (back button clicks)
window.onpopstate = function () {
    // Push the state forward instantly, nullifying the backward movement
    history.go(1);
};

window.addEventListener('keydown', function (e) {
    // Block Backspace if the user isn't actively typing inside an input text area
    if (e.key === 'Backspace' && e.target.tagName !== 'INPUT' && e.target.tagName !== 'TEXTAREA') {
        e.preventDefault();
    }

    // Block Alt + Left Arrow (Windows/Linux standard browser back hotkey)
    if (e.altKey && e.key === 'ArrowLeft') {
        e.preventDefault();
    }

    // Block Cmd + Left Arrow / Cmd + [ (Mac standard browser back hotkeys)
    if ((e.metaKey && e.key === 'ArrowLeft') || (e.metaKey && e.key === '[')) {
        e.preventDefault();
    }
});

// Audio handlers:

async function playThenNavigate(sound, targetUrl, element) {
    if (document.body.classList.contains('page-is-loading')) return;

    document.body.classList.add('page-is-loading');

    if (element) {
        element.classList.add('page-exit');
    }

    try {
        await playSfx(sound);
    } catch (e) {}

    window.location.href = targetUrl;
}

// Question Page Functions

function submitAnswer(questionType, level) {
    // Optimization, to stop duplicate requests.
    if (document.body.classList.contains('page-is-loading')) {
        return
    }

    document.body.classList.add('page-is-loading');
    const inputAnswerElement = document.getElementById("answer");

    const data = {
        answer: inputAnswerElement.value
    };

    // Send data to flask by using fetch.
    fetch('/api/submit-answer', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
        .then(response => {
            return response.json();
        })
        .then(data => {
            if (data.status === "success") {
                document.body.classList.remove('page-is-loading');
                playThenNavigate("click",`/question?question-type=${questionType}&level=${level}&state=current`)
            } else {
               document.body.classList.remove('page-is-loading');
            }
        })

}

function answerPressEnter(event, element, questionType, level) {
    // Check the user pressed enter
    if (event.key === 'Enter') {
        event.preventDefault();

        submitAnswer(questionType, level);
    }
}

// Sound Engine:

function playSfx(key) {
    if (!key) return Promise.resolve();

    return fetch(`/api/sfx/${key}`)
        .catch(err => console.error(err));
}

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