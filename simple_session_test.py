"""
Simple test to load LinkedIn session
"""

from playwright.sync_api import sync_playwright
import time


def simple_session_test():
    """
    Simple test to load LinkedIn session
    """
    print("Testing LinkedIn session loading...")
    
    try:
        with sync_playwright() as p:
            print("1. Launching Firefox...")
            browser = p.firefox.launch(headless=False)
            
            print("2. Creating context with session...")
            context = browser.new_context(storage_state="linkedin_auth.json")
            
            print("3. Creating page...")
            page = context.new_page()
            
            print("4. Navigating to LinkedIn...")
            page.goto("https://www.linkedin.com/feed/")
            
            print("5. Waiting for load...")
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            print(f"6. Current URL: {page.url}")
            
            print("✅ Session loaded successfully!")
            
            # Keep browser open for a moment
            time.sleep(10)
            browser.close()
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    simple_session_test()