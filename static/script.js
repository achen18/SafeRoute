
const loginForm = document.getElementById('login-form');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const username = document.getElementById('username').value;
        const password = document.getElementById('password').value;

        const response = await fetch('/login', { // Raw route
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        if (response.ok) {
            window.location.href = 'index.html';
        } else {
            const result = await response.json();
            document.getElementById('message').innerText = result.error;
        }
    });
}

const regForm = document.getElementById('register-form');
if (regForm) {
    regForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            fname: document.getElementById('fname').value,
            lname: document.getElementById('lname').value,
            username: document.getElementById('username').value,
            password: document.getElementById('password').value,
            role: document.getElementById('role').value
        };

        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            alert("Account created! Please login.");
            window.location.href = 'login.html';
        } else {
            const result = await response.json();
            document.getElementById('message').innerText = result.error;
        }
    });
}

const logoutBtn = document.getElementById('logout-btn');
if (logoutBtn) {
    logoutBtn.addEventListener('click', async () => {
        const response = await fetch('/logout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });

        if (response.ok) {
            // Reload the index page to update Jinja template view state
            window.location.href = '/';
        } else {
            alert("Failed to sign out cleanly.");
        }
    });
}