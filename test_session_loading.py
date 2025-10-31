"""
Test script to verify session loading works correctly
"""

from playwright.sync_api import sync_playwright
from linkedin_session_loader import load_linkedin_state_and_scrape
import time


def test_session_loading():
    """
    Test session loading with shared Playwright instance
    """
    print("Testing session loading with shared Playwright instance...")
    
    # Create Playwright instance
    playwright = sync_playwright().start()
    
    try:
        # Try to load session
        page, browser, context = load_linkedin_state_and_scrape(
            verify_login=False, 
            playwright_instance=playwright
        )
        
        if page is not None and browser is not None:
            print("✅ Session loaded successfully!")
            print(f"Current URL: {page.url}")
            
            # Wait a moment
            time.sleep(2)
            
            # Close browser
            browser.close()
        else:
            print("❌ Failed to load session")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        try:
            playwright.stop()
        except:
            pass


if __name__ == "__main__":
    test_session_loading()