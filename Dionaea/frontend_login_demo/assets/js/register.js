/**
 * Dionaea Register Page Logic
 * Handles form validation, API interaction, and UI states.
 */

// Configuration
const CONFIG = {
    API_URL: 'http://localhost:8001/api/v1/auth/register', // Adjust if backend is on a different port/host
    LOGIN_URL: 'index.html', // Redirect target after success
    MOCK_MODE: false // Set to false to use real API
};

document.addEventListener('DOMContentLoaded', () => {
    const registerForm = document.getElementById('registerForm');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const confirmPasswordInput = document.getElementById('confirm-password');
    const termsCheckbox = document.getElementById('terms');
    const submitBtn = document.getElementById('submit-btn');
    const btnText = document.getElementById('btn-text');
    const btnLoading = document.getElementById('btn-loading');
    const globalError = document.getElementById('global-error');
    const globalErrorText = document.getElementById('global-error-text');
    const globalSuccess = document.getElementById('global-success');
    const globalSuccessText = document.getElementById('global-success-text');

    // 1. Input Validation Helpers
    const validateInput = (input, errorId, checkFn) => {
        const errorEl = document.getElementById(errorId);
        let errorMessage = null;

        if (!input.value.trim()) {
            errorMessage = '此字段不能为空';
        } else if (checkFn) {
            errorMessage = checkFn(input.value.trim());
        }

        if (errorMessage) {
            showInputError(input, errorEl, errorMessage);
            return false;
        } else {
            clearInputError(input, errorEl);
            return true;
        }
    };

    const showInputError = (input, errorEl, msg) => {
        input.classList.add('border-error', 'ring-1', 'ring-error');
        input.classList.remove('border-gray-300', 'focus:ring-primary', 'focus:border-primary');
        errorEl.textContent = msg;
        errorEl.classList.remove('hidden');
    };

    const clearInputError = (input, errorEl) => {
        input.classList.remove('border-error', 'ring-1', 'ring-error');
        input.classList.add('border-gray-300', 'focus:ring-primary', 'focus:border-primary');
        errorEl.classList.add('hidden');
    };

    // Real-time validation listeners
    [usernameInput, emailInput, passwordInput, confirmPasswordInput].forEach(input => {
        input.addEventListener('input', () => {
            const errorId = input.id + '-error';
            clearInputError(input, document.getElementById(errorId));
            hideGlobalError();
        });
    });

    // 2. Form Submission
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Validation Rules
        const isUsernameValid = validateInput(usernameInput, 'username-error', (val) => {
            if (val.length < 3 || val.length > 50) return '用户名长度需在 3-50 个字符之间';
            return null;
        });

        const isEmailValid = validateInput(emailInput, 'email-error', (val) => {
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(val)) return '请输入有效的邮箱地址';
            return null;
        });

        const isPasswordValid = validateInput(passwordInput, 'password-error', (val) => {
            if (val.length < 6) return '密码长度至少为 6 位';
            return null;
        });

        const isConfirmPasswordValid = validateInput(confirmPasswordInput, 'confirm-password-error', (val) => {
            if (val !== passwordInput.value.trim()) return '两次输入的密码不一致';
            return null;
        });
        
        const isTermsAccepted = termsCheckbox.checked;
        if (!isTermsAccepted) {
            document.getElementById('terms-error').textContent = '请阅读并同意服务条款';
            document.getElementById('terms-error').classList.remove('hidden');
        } else {
            document.getElementById('terms-error').classList.add('hidden');
        }


        if (!isUsernameValid || !isEmailValid || !isPasswordValid || !isConfirmPasswordValid || !isTermsAccepted) {
            registerForm.classList.add('animate-shake');
            setTimeout(() => registerForm.classList.remove('animate-shake'), 500);
            return;
        }

        // Set Loading State
        setLoading(true);

        const userData = {
            username: usernameInput.value.trim(),
            email: emailInput.value.trim(),
            password: passwordInput.value.trim()
        };

        try {
            let data;
            
            if (CONFIG.MOCK_MODE) {
                await new Promise(resolve => setTimeout(resolve, 1500));
                // Mock success
                data = { username: userData.username, email: userData.email, id: 123 };
            } else {
                const response = await fetch(CONFIG.API_URL, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json'
                    },
                    body: JSON.stringify(userData)
                });

                if (!response.ok) {
                    const errorData = await response.json().catch(() => ({}));
                    if (response.status === 400 || response.status === 422) {
                         throw new Error(errorData.detail || '注册请求无效');
                    } else if (response.status === 409) {
                         throw new Error('用户名或邮箱已被注册');
                    } else {
                        throw new Error('服务器内部错误，请稍后重试');
                    }
                }
                data = await response.json();
            }

            // Success
            handleRegisterSuccess(data);

        } catch (error) {
            console.error('Register error:', error);
            showGlobalError(error.message || '网络连接超时');
            registerForm.classList.add('animate-shake');
            setTimeout(() => registerForm.classList.remove('animate-shake'), 500);
        } finally {
            setLoading(false);
        }
    });

    // 3. Helper Functions
    function setLoading(isLoading) {
        if (isLoading) {
            submitBtn.disabled = true;
            submitBtn.classList.add('btn-loading');
            btnText.classList.add('hidden');
            btnLoading.classList.remove('hidden');
            [usernameInput, emailInput, passwordInput, confirmPasswordInput, termsCheckbox].forEach(el => el.disabled = true);
        } else {
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-loading');
            btnText.classList.remove('hidden');
            btnLoading.classList.add('hidden');
            [usernameInput, emailInput, passwordInput, confirmPasswordInput, termsCheckbox].forEach(el => el.disabled = false);
        }
    }

    function showGlobalError(message) {
        globalErrorText.textContent = message;
        globalError.classList.remove('hidden');
        globalSuccess.classList.add('hidden');
    }

    function hideGlobalError() {
        globalError.classList.add('hidden');
    }

    function handleRegisterSuccess(data) {
        globalSuccessText.textContent = `注册成功！欢迎 ${data.username}。即将跳转登录页...`;
        globalSuccess.classList.remove('hidden');
        globalError.classList.add('hidden');
        
        // Clear form
        registerForm.reset();
        
        // Redirect
        setTimeout(() => {
            window.location.href = CONFIG.LOGIN_URL;
        }, 2000);
    }
});
