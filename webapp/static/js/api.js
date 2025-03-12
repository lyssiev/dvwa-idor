/* Javascript used for API calls */

function encodeUserId(userId) {
  return btoa(userId.toString()); // Base64 encoding
}

function resetPassword() {
  const new_password = document.getElementById("new_password").value;
  userId = CURRENT_USER_ID;
  userId = encodeUserId(userId);

  fetch("/reset_password_view/", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({
      user_id: userId,
      new_password: new_password,
    }),
  })
    .then((response) => response.json())
    .then((data) => {
      let msgHtml = `<div class="alert alert-light text-dark mt-3 w-100 px-2">${data.message}!</div>`;

      // DVWA - returning the flag if the exercise is complete
      if (data.flag) {
        msgHtml += `<div class="alert alert-success shadow-lg mt-3 position-absolute top-0 end-0" style="width: auto;"><strong>Congratulations!</strong> You found the flag for Exercise 5: ${data.flag}</div>`;
      }
      document.getElementById("resetMessage").innerHTML = msgHtml;
    })
    .catch((err) => {
      console.error("Error:", err);
      document.getElementById("resetMessage").innerHTML =
        '<div class="alert alert-danger">Something went wrong: ' +
        err.message +
        "</div>";
    });
}

// CSRF token cookie from Django Documentation
// https://docs.djangoproject.com/en/3.2/ref/csrf/#ajax
function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === name + "=") {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}
