
function submitAnswer(questionType) {

    const inputAnswerElement = document.getElementById("answer");

    const data = {
        answer: inputAnswerElement.value
    }

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
                window.location.href=`question?question-type=${questionType}&level=0&state=current`
            } else {
                console.log("Nothing was entered")
            }
        })

}