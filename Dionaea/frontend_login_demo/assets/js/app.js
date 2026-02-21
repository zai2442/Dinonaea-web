/**
 * Dionaea Login Page Logic
 * Handles form validation, API interaction, and UI states.
 */

// Configuration
const CONFIG = {
    API_URL: 'http://localhost:8001/api/v1/auth/login', // 已修改为您的后端地址 (端口 8001)
    DASHBOARD_URL: '/dashboard.html', // Redirect target after login
    ANIMATION_DURATION: 300,
    MOCK_MODE: false // 已关闭 Mock 模式，启用真实接口
};

document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');
    const rememberMeCheckbox = document.getElementById('remember-me');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoading = document.getElementById('btn-loading');
    const globalError = document.getElementById('global-error');
    const globalErrorText = document.getElementById('global-error-text');

    // 1. Initialize: Check for saved username
    const savedUsername = localStorage.getItem('dionaea_remember_username');
    if (savedUsername) {
        usernameInput.value = savedUsername;
        rememberMeCheckbox.checked = true;
    }

    // 2. Input Validation Helpers
    const validateInput = (input, errorId) => {
        const errorEl = document.getElementById(errorId);
        if (!input.value.trim()) {
            input.classList.add('border-error', 'ring-1', 'ring-error');
            input.classList.remove('border-gray-300', 'focus:ring-primary', 'focus:border-primary');
            errorEl.textContent = '此字段不能为空';
            errorEl.classList.remove('hidden');
            return false;
        } else {
            input.classList.remove('border-error', 'ring-1', 'ring-error');
            input.classList.add('border-gray-300', 'focus:ring-primary', 'focus:border-primary');
            errorEl.classList.add('hidden');
            return true;
        }
    };

    // Remove error styles on input
    [usernameInput, passwordInput].forEach(input => {
        input.addEventListener('input', () => {
            input.classList.remove('border-error', 'ring-1', 'ring-error');
            input.classList.add('border-gray-300', 'focus:ring-primary', 'focus:border-primary');
            const errorId = input.id + '-error';
            document.getElementById(errorId).classList.add('hidden');
            hideGlobalError();
        });
    });

    // 3. Form Submission
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Client-side validation
        const isUsernameValid = validateInput(usernameInput, 'username-error');
        const isPasswordValid = validateInput(passwordInput, 'password-error');

        if (!isUsernameValid || !isPasswordValid) {
            // Shake animation for visual feedback
            loginForm.classList.add('animate-shake');
            setTimeout(() => loginForm.classList.remove('animate-shake'), 500);
            return;
        }

        // Set Loading State
        setLoading(true);

        const username = usernameInput.value.trim();
        const password = passwordInput.value.trim();

        try {
            let data;
            
            if (CONFIG.MOCK_MODE) {
                // Simulate network delay
                await new Promise(resolve => setTimeout(resolve, 1500));
                
                // Mock credentials check (for demo)
                if (username === 'admin' && password === 'password') {
                    data = {
                        access_token: 'mock_access_token_12345',
                        token_type: 'bearer',
                        refresh_token: 'mock_refresh_token_67890'
                    };
                } else {
                    throw new Error('用户名或密码错误 (Mock)');
                }
            } else {
                // Real API Call
                // OAuth2PasswordRequestForm expects x-www-form-urlencoded
                const formData = new URLSearchParams();
                formData.append('username', username);
                formData.append('password', password);

                const response = await fetch(CONFIG.API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'Accept': 'application/json'
                    },
                    body: formData
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    // Handle 401/400/422 etc
                    if (response.status === 401 || response.status === 400) {
                        throw new Error(errorData.detail || '用户名或密码错误');
                    } else if (response.status === 422) {
                         throw new Error('格式验证失败');
                    } else {
                        throw new Error('服务器内部错误，请稍后重试');
                    }
                }

                data = await response.json();
            }

            // Login Success
            handleLoginSuccess(data, username);

        } catch (error) {
            // Login Failed
            console.error('Login error:', error);
            showGlobalError(error.message || '网络连接超时，请检查您的网络设置');
            loginForm.classList.add('animate-shake');
            setTimeout(() => loginForm.classList.remove('animate-shake'), 500);
        } finally {
            setLoading(false);
        }
    });

    // 4. Helper Functions
    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.classList.add('btn-loading');
            btnText.classList.add('hidden');
            btnLoading.classList.remove('hidden');
            // Disable inputs
            usernameInput.disabled = true;
            passwordInput.disabled = true;
        } else {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
            // Enable inputs
            usernameInput.disabled = false;
            passwordInput.disabled = false;
            // Focus back on password if failed? Or username?
            if (globalError.classList.contains('hidden') === false) {
                 passwordInput.value = '';
                 passwordInput.focus();
            }
        }
    }

    function showGlobalError(message) {
        globalErrorText.textContent = message;
        globalError.classList.remove('hidden');
        // ARIA alert
        globalError.setAttribute('aria-hidden', 'false');
    }

    function hideGlobalError() {
        globalError.classList.add('hidden');
        globalError.setAttribute('aria-hidden', 'true');
    }

    function handleLoginSuccess(tokenData, username) {
        // Save Token
        localStorage.setItem('dionaea_access_token', tokenData.access_token);
        localStorage.setItem('dionaea_refresh_token', tokenData.refresh_token);

        // Handle "Remember Me"
        if (rememberMeCheckbox.checked) {
            localStorage.setItem('dionaea_remember_username', username);
        } else {
            localStorage.removeItem('dionaea_remember_username');
        }

        // Show success visual (optional, maybe change button color)
        submitBtn.classList.remove('bg-primary', 'hover:bg-primary-hover');
        submitBtn.classList.add('bg-success', 'hover:bg-success');
        btnText.textContent = '登录成功';
        
        // Redirect
        setTimeout(() => {
            window.location.href = CONFIG.DASHBOARD_URL;
        }, 500);
    }
});
