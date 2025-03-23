document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const usernameError = document.getElementById('usernameError');
    const passwordError = document.getElementById('passwordError');
    const togglePassword = document.getElementById('togglePassword');
    const submitBtn = document.getElementById('submitBtn');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');

    // Get CSRF token from meta tag
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Password visibility toggle
    togglePassword.addEventListener('click', function() {
        const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
        passwordInput.setAttribute('type', type);
        
        // Update icon based on password visibility
        const paths = this.querySelector('svg').querySelectorAll('path');
        if (type === 'text') {
            paths[0].setAttribute('d', 'M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21');
        } else {
            paths[0].setAttribute('d', 'M15 12a3 3 0 11-6 0 3 3 0 016 0z');
            paths[1].setAttribute('d', 'M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z');
        }
    });

    // Username validation
    function validateUsername(username) {
        return username.length >= 3 && /^[a-zA-Z0-9_-]+$/.test(username);
    }

    // Password validation (min 8 chars, 1 uppercase, 1 lowercase, 1 number)
    function validatePassword(password) {
        const minLength = password.length >= 8;
        const hasUpperCase = /[A-Z]/.test(password);
        const hasLowerCase = /[a-z]/.test(password);
        const hasNumber = /\d/.test(password);
        return { 
            isValid: minLength && hasUpperCase && hasLowerCase && hasNumber,
            errors: {
                minLength,
                hasUpperCase,
                hasLowerCase,
                hasNumber
            }
        };
    }

    // Real-time validation
    usernameInput.addEventListener('input', function() {
        if (!validateUsername(this.value)) {
            usernameError.textContent = 'Username must be at least 3 characters and contain only letters, numbers, underscores, and hyphens';
            usernameError.classList.remove('hidden');
        } else {
            usernameError.classList.add('hidden');
        }
    });

    passwordInput.addEventListener('input', function() {
        const validation = validatePassword(this.value);
        if (!validation.isValid) {
            let errorMsg = 'Password must contain:';
            if (!validation.errors.minLength) errorMsg += ' 8+ characters,';
            if (!validation.errors.hasUpperCase) errorMsg += ' uppercase letter,';
            if (!validation.errors.hasLowerCase) errorMsg += ' lowercase letter,';
            if (!validation.errors.hasNumber) errorMsg += ' number,';
            passwordError.textContent = errorMsg.slice(0, -1);
            passwordError.classList.remove('hidden');
        } else {
            passwordError.classList.add('hidden');
        }
    });

    // Form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        // Clear previous error messages
        errorMessage.textContent = '';
        errorMessage.style.display = 'none';
        
        // Show loading state
        submitBtn.disabled = true;
        loadingSpinner.classList.remove('hidden');
        
        try {
            const response = await fetch('/auth/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    username: usernameInput.value,
                    password: passwordInput.value,
                    remember: document.getElementById('remember').checked
                })
            });

            const data = await response.json();
            
            if (response.ok) {
                // Store token in localStorage
                if (data.token) {
                    localStorage.setItem('auth_token', data.token);
                    // Redirect to the application with token
                    window.location.href = `${data.redirect}?token=${data.token}`;
                } else {
                    errorMessage.textContent = 'Authentication token not received';
                    errorMessage.style.display = 'block';
                }
            } else {
                // Show error message
                errorMessage.textContent = data.message || 'An error occurred. Please try again later.';
                errorMessage.style.display = 'block';
            }
        } catch (error) {
            console.error('Login error:', error);
            errorMessage.textContent = 'An error occurred. Please try again later.';
            errorMessage.style.display = 'block';
        } finally {
            // Reset loading state
            submitBtn.disabled = false;
            loadingSpinner.classList.add('hidden');
        }
    });
}); 