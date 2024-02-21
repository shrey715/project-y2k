function toggleMenu() {
    var navtexts = document.getElementsByClassName("nav-text");
    var navbutton = document.getElementById("sidebar-btn");

    for (var i = 0; i < navtexts.length; i++) {
        navtexts[i].classList.toggle("show-nav-text");
    }

    navbutton.classList.toggle('bxs-chevrons-left');
    navbutton.classList.toggle('bxs-chevrons-right');
}

function checkLogin() {
    var usernameInput = document.getElementById("username").value;
    var passwordInput = document.getElementById("password").value;

    if (!usernameInput || !passwordInput) {
        var attempt = document.getElementById("attempt-msg");
        attempt.style.color = "red";
        attempt.innerHTML = "Please fill in all fields!";
        return;
    }

    fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
            'username': usernameInput,
            'password': passwordInput
        }),
    })
    .then(response => response.json())
    .then(data => {
        var attempt = document.getElementById("attempt-msg");
        attempt.style.color = data.authenticated ? "green" : "red";
        attempt.innerHTML = data.message;

        if (data.authenticated) {
            localStorage.setItem('jwtToken', data.access_token);
            setTimeout(function() {
                fetch(`/dashboard/${usernameInput}`, {
                    method: 'GET',
                    headers: {
                        'Authorization': `Bearer ${data.access_token}`,
                        'Content-Type': 'application/json'
                    },
                })
                .then(response => response.json())
                .then(dashboardData => {
                    console.log(dashboardData);
                })
                .catch(error => {
                    console.error('Error fetching dashboard data:', error);
                });

                window.location.replace(`/${usernameInput}/dashboard`);
            }, 2000);
        }
    })
    .catch((error) => {
        console.error('Error:', error);
    });
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