import sys
import os
from playwright.sync_api import sync_playwright

def test_register():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # Ensure server is running at localhost:8000
        page.goto('http://localhost:8000/register.html')
        
        # Check title
        print(f"Page Title: {page.title()}")
        assert "Dionaea 管理系统注册" in page.title()
        print("✅ Page loaded successfully.")

        # Check form elements
        assert page.is_visible('#username')
        assert page.is_visible('#email')
        assert page.is_visible('#password')
        assert page.is_visible('#confirm-password')
        assert page.is_visible('#submit-btn')
        print("✅ Form elements found.")

        # Test Validation
        print("Testing validation...")
        page.click('#submit-btn')
        # Wait for error message animation/visibility
        page.wait_for_selector('#username-error', state='visible')
        page.wait_for_selector('#email-error', state='visible')
        page.wait_for_selector('#password-error', state='visible')
        print("✅ Validation works (empty fields show error).")

        # Test Registration Flow
        print("Testing registration...")
        # Generate random username to avoid conflict
        import random
        rand_suffix = random.randint(1000, 9999)
        test_username = f"testuser_{rand_suffix}"
        test_email = f"testuser_{rand_suffix}@example.com"
        
        page.fill('#username', test_username)
        page.fill('#email', test_email)
        page.fill('#password', 'password123')
        page.fill('#confirm-password', 'password123')
        page.check('#terms')
        
        page.click('#submit-btn')
        
        # Wait for success message
        try:
            page.wait_for_selector('#global-success', state='visible', timeout=5000)
            print(f"✅ Registration success message visible for {test_username}.")
        except Exception:
            print("❌ Registration failed or success message not found.")
            # Check for error message
            if page.is_visible('#global-error'):
                error_text = page.inner_text('#global-error-text')
                print(f"Global Error: {error_text}")
            
            # Take screenshot
            page.screenshot(path="register_fail.png")
            sys.exit(1)
        
        browser.close()

if __name__ == "__main__":
    test_register()
