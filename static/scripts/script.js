function toggleMenu() {
    var navtexts = document.getElementsByClassName("nav-text");
    var navbutton = document.getElementById("sidebar-btn");

    for (var i = 0; i < navtexts.length; i++) {
        navtexts[i].classList.toggle("show-nav-text");
    }

    // Toggle between chevron icons for the sidebar button
    navbutton.classList.toggle('bxs-chevrons-left');
    navbutton.classList.toggle('bxs-chevrons-right');
}

function checkSignup() {
    var usernameInput = document.getElementById("username").value;
    var emailInput = document.getElementById("email").value;
    var passwordInput = document.getElementById("password").value;

    if (!usernameInput || !passwordInput || !emailInput) {
        var attempt = document.getElementById("attempt-msg");
        attempt.style.color = "red";
        attempt.innerHTML = "Please fill in all fields!";
        return;
    }

    fetch('/signup', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'username': usernameInput,
            'password': passwordInput,
            'email': emailInput
        }),
    })
    .then(response => response.json())
    .then(data => {
        var attempt = document.getElementById("attempt-msg");
        attempt.style.color = data.authenticated ? "green" : "red";
        attempt.innerHTML = data.message;

        if (data.authenticated) {
            setTimeout(function() {
                window.location.replace("/login");
            }, 2000);
        }
        else if (data.message.includes("Email is already taken")) {
            document.getElementById("email").value = "";
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
}
