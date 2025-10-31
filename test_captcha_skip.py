"""
Test script to verify CAPTCHA skipping logic
"""

from playwright.sync_api import sync_playwright
import time


def test_captcha_skip():
    """
    Test CAPTCHA skipping logic
    """
    print("Testing CAPTCHA skipping logic...")
    
    with sync_playwright() as p:
        print("Launching Firefox...")
        browser = p.firefox.launch(headless=False)
        
        print("Creating context with session...")
        context = browser.new_context(storage_state="linkedin_auth.json")
        
        print("Creating page...")
        page = context.new_page()
        
        print("Navigating to LinkedIn...")
        page.goto("https://www.linkedin.com/feed/")
        
        print(f"Current URL: {page.url}")
        
        # Test the CAPTCHA skipping logic
        current_url = page.url.lower()
        is_on_valid_linkedin_page = (
            "linkedin.com" in current_url and 
            "login" not in current_url and 
            "checkpoint" not in current_url and 
            "challenge" not in current_url
        )
        
        if is_on_valid_linkedin_page:
            print("✅ Already on valid LinkedIn page, would skip CAPTCHA detection")
        else:
            print("⚠ Would perform CAPTCHA detection")
            
        # Keep browser open for a moment
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    test_captcha_skip()