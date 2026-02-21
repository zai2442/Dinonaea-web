import sys
import os
from playwright.sync_api import sync_playwright

def test_login():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        # The server is started at the root of frontend_login_demo
        page.goto('http://localhost:8000/index.html')
        
        # Check title
        print(f"Page Title: {page.title()}")
        assert "Dionaea 管理系统登录" in page.title()
        print("✅ Page loaded successfully.")

        # Check form elements
        assert page.is_visible('#username')
        assert page.is_visible('#password')
        assert page.is_visible('#submit-btn')
        print("✅ Form elements found.")

        # Test Validation
        print("Testing validation...")
        page.click('#submit-btn')
        # Wait for error message animation/visibility
        page.wait_for_selector('#username-error', state='visible')
        page.wait_for_selector('#password-error', state='visible')
        print("✅ Validation works (empty fields show error).")

        # Test Mock Login
        print("Testing mock login...")
        page.fill('#username', 'admin')
        page.fill('#password', 'password')
        
        # Setup dialog handler before clicking
        dialog_received = False
        def handle_dialog(dialog):
            nonlocal dialog_received
            print(f"Dialog message: {dialog.message}")
            if "登录成功" in dialog.message:
                dialog_received = True
            dialog.accept()

        page.on("dialog", handle_dialog)
        
        page.click('#submit-btn')
        
        # Wait for the login process (1.5s delay in mock)
        page.wait_for_timeout(3000) 
        
        if dialog_received:
            print("✅ Login success dialog received.")
        else:
            print("❌ Login success dialog NOT received.")
            sys.exit(1)
        
        browser.close()

if __name__ == "__main__":
    test_login()
