"""
Simple session test
"""

from playwright.sync_api import sync_playwright
import time


def simple_test():
    """
    Simple test to load session
    """
    print("Starting simple session test...")
    
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
        print("✅ Test completed successfully!")
        
        # Keep browser open for a moment
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    simple_test()