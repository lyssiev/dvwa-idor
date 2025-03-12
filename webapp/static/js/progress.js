// Javascript to track progress for each user

document.addEventListener("DOMContentLoaded", function () {
    fetchProgress(); // fetch user's progress on page load
});

// updates UI to show completed exercises
function updateExerciseUI(completedExercises) {
    // for each completed exercise, add styling to the button and update the text
    completedExercises.forEach(exercise => {
        let button = document.getElementById(`exercise${exercise}`);
        if (button) {
            button.classList.add("completed-exercise");
            // if button does not already have text, add it
            if (!button.innerHTML.includes(" - Completed!")) {
                button.innerHTML += " - Completed!";
            }
        }
    });
}

// fetches user's progress from the server
function fetchProgress() {
    fetch("/get_progress/") 
        .then(response => response.json()) // parse the response as JSON
        .then(data => {
            updateExerciseUI(data.completed_exercises); // update the UI
            updateProgressBar(data.progress); // update the progress bar
        })
        .catch(error => console.error("Error fetching progress:", error));
}

// function to show exercise is completed and update progress
function markExerciseCompleted(exerciseNumber) {
    // send a POST request to the server to update the progress
    fetch('/update_progress/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken'),
            'Content-Type': 'application/x-www-form-urlencoded'
        },
        body: `exercise=${exerciseNumber}`
    })
    .then(response => response.json())
    .then(data => {
        updateExerciseUI(data.completed_exercises); // update the UI
        updateProgressBar(data.progress); // update the progress bar
    });
}

// function to update the progress bar
function updateProgressBar(progress) {
    document.getElementById("progressBar").style.width = progress + "%";
    if (progress === 100) {
        window.location.href = window.location.origin + "/solutions/";
    }
}

/* DELETE LATER - testing for resetting progress */

// add event listener to reset progress button
document.getElementById("resetProgressBtn").addEventListener("click", function () {
    if (confirm("Are you sure you want to reset your progress?")) {
        fetch("/reset_progress/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCSRFToken()
            },
            credentials: "same-origin"
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === "success") {
                console.log("Reset Response:", data);
                updateExerciseUI();
                updateProgressBar();
                alert("Progress has been reset! Please refresh your browser.");
            } else {
                alert("No progress found to reset.");
            }
        })
        .catch(error => console.error("Error resetting progress:", error));
    }
});

// function to get CSRF token from cookies
// source: https://docs.djangoproject.com/en/3.2/ref/csrf/#ajax
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        let cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            let cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
    }
    return cookieValue;
}

// function to get the value of a cookie
// source: https://docs.djangoproject.com/en/3.2/ref/csrf/#ajax
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}