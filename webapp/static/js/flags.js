let completedExercises = new Set(); // Stores completed exercises

function submitFlag() {
    let flagInput = document.getElementById("flagInput").value.trim();
    let flagMessage = document.getElementById("flagMessage");

    console.log("Submitting flag:", flagInput);

    fetch("https://api-dvwa.onrender.com/api/check_flag", {  
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ flag: flagInput })  // ✅ Send only the flag
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            flagMessage.innerHTML = `<span class='text-success'>${data.message} (Exercise ${data.exercise} completed!)</span>`;
            markExerciseCompleted(data.exercise);  // ✅ Now correctly marks it
        } else {
            flagMessage.innerHTML = `<span class='text-danger'>${data.message}</span>`;
        }
    })
    .catch(error => {
        console.error("Fetch Error:", error);
        flagMessage.innerHTML = "<span class='text-danger'>Error submitting flag. Check console.</span>";
    });
}


function markExerciseCompleted(exercise) {
    let button = document.getElementById(exercise);
    if (button) {
        completedExercises.add(exercise);
        button.classList.add("completed-exercise");
        button.innerHTML += " - Complete!"; 
        updateProgress();
    } else {
        console.error(`Exercise button not found: ${exercise}`);
    }
}

function updateProgress() {
    let progressBar = document.getElementById("progressBar");
    let totalExercises = 5; 
    let completedCount = completedExercises.size;
    let progressPercentage = (completedCount / totalExercises) * 100;
    progressBar.style.width = `${progressPercentage}%`;
}

function showExercise(exerciseNumber) {
    let modalId = `exercise${exerciseNumber}Modal`;
    let modal = new bootstrap.Modal(document.getElementById(modalId));
    modal.show();
}
