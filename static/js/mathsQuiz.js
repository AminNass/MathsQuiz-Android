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

// Question Page Functions

function submitAnswer(questionType, level) {

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
                window.location.href=`question?question-type=${questionType}&level=${level}&state=current`;
            } else {
                console.log("Nothing was entered");
            }
        })

}

function answerPressEnter(event, element, questionType, level) {
    // Check the user pressed enter
    if (event.key === 'Enter') {
        event.preventDefault();

        let inputValue = element.value; // Get the typed text
        console.log("User entered: " + inputValue);

        submitAnswer(questionType, level);
    }
}