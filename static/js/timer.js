document.addEventListener("DOMContentLoaded", () => {
    // Get parameter in url containing the level.
    const urlParams = new URLSearchParams(window.location.search);
    const level = urlParams.get('level');

    let timeRemaining = 0;

    // Set the duration from the level parameter.
    if (level === '0' || level === null) {
        // If level zero then the time is infinite.
        document.getElementById('timer').innerText = "∞";
        return;
    } else if (level === '1') {
        timeRemaining = 21;
    } else if (level === '2') {
        timeRemaining = 11;
    }

    document.body.classList.remove('page-is-loading');

    // Get the timer element that shows the time.
    const timerElement = document.getElementById('timer');

    // Display the current time left.
    timerElement.innerText = `${timeRemaining}s`;

    // Run a loop function that executes exactly every 1000 milliseconds (1 second)
    const countdownInterval = setInterval(() => {
        timeRemaining--;
        // Take away one second

        // Update the screen text
        timerElement.innerText = `${timeRemaining}s`;

        // Trigger event when time runs out
        if (timeRemaining <= 0) {
            clearInterval(countdownInterval);
            handleTimeOut();
            // Turn off the timer when it has reached zero.
        }
    }, 1000);
});

// Function that runs when the user runs out of time.
function handleTimeOut() {
    const timerElement = document.getElementById('timer');
    timerElement.innerText = "Time's Up!";
    document.getElementById("userAnswer").disabled = true;
}