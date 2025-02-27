// JS for handling flag submission

let completedExercises = new Set(); // storing completed exercises

// Event listener for flag submission
function submitFlag() {
  let flagInput = document.getElementById("flagInput").value.trim();
  let flagMessage = document.getElementById("flagMessage");

  console.log("Submitting flag:", flagInput);

  // post flag to API
  fetch("https://api-dvwa.onrender.com/api/check_flag", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ flag: flagInput }),
  })
    .then((response) => response.json()) // parse JSON response
    .then((data) => {
      if (data.status === "success") {
        flagMessage.innerHTML = `<span class='text-success'>${data.message} (Exercise ${data.exercise} completed!)</span>`; // display success message
        markExerciseCompleted(data.exercise); // mark exercise as completed
      } else {
        flagMessage.innerHTML = `<span class='text-danger'>${data.message}</span>`; // display error message
      }
    })
    .catch((error) => {
      console.error("Fetch Error:", error);
      flagMessage.innerHTML =
        "<span class='text-danger'>Error submitting flag. Check console.</span>"; // display error message
    });
}

// Mark exercise as completed
function markExerciseCompleted(exercise) {
  let button = document.getElementById(exercise);
  // add exercise to completed set and update progress bar
  if (button) {
    completedExercises.add(exercise);
    button.classList.add("completed-exercise");
    button.innerHTML += " - Complete!"; // add completion message to button
    updateProgress();
  }
}

// Update progress bar
function updateProgress() {
  let progressBar = document.getElementById("progressBar");
  let totalExercises = 5;
  let completedCount = completedExercises.size;
  let progressPercentage = (completedCount / totalExercises) * 100; // calculate percentage
  progressBar.style.width = `${progressPercentage}%`; // update progress bar width
}

// Show exercise modal
function showExercise(exerciseNumber) {
  let modalId = `exercise${exerciseNumber}Modal`;
  let modal = new bootstrap.Modal(document.getElementById(modalId));
  modal.show();
}
