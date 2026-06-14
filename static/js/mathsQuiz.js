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

function playThenNavigate(soundUrl, targetUrl, element) {
    // Guard against double-tap requests
    if (document.body.classList.contains('page-is-loading')) {
        return;
    }

    // Lock UI
    document.body.classList.add('page-is-loading');

    if (element) {
        element.classList.add('page-exit');
    }

    const audio = new Audio(soundUrl);
    let hasNavigated = false;

    // Unified navigation trigger to prevent double execution
    function triggerNavigation() {
        if (!hasNavigated) {
            hasNavigated = true;
            window.location.href = targetUrl;
        }
    }

    // Trigger when the audio finishes playing completely
    audio.onended = triggerNavigation;

    // only if the audio hangs or takes too long.
    const fallbackTimeout = setTimeout(triggerNavigation, 1500);

    // C. Fire audio playback
    audio.play().catch(error => {
        clearTimeout(fallbackTimeout);
        triggerNavigation();
    });
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
                playThenNavigate("/static/sounds/click.mp3",`/question?question-type=${questionType}&level=${level}&state=current`)
            }
            document.body.classList.remove('page-is-loading');
        })

}

function answerPressEnter(event, element, questionType, level) {
    // Check the user pressed enter
    if (event.key === 'Enter') {
        event.preventDefault();

        // Get the typed text
        let inputValue = element.value;

        submitAnswer(questionType, level);
    }
}