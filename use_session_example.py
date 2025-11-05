"""
Example script showing how to automatically use saved LinkedIn sessions
to avoid logging in repeatedly
"""

from linkedin_session_loader import load_linkedin_state_and_scrape
from playwright.sync_api import sync_playwright
import time
import sys
import os

def check_and_use_saved_session():
    """
    Check if a saved session exists and use it if valid
    """
    session_file = "linkedin_auth.json"
    
    # Check if session file exists
    if not os.path.exists(session_file):
        print("❌ No saved session found.")
        return None, None, None
        
    print("✅ Saved session file found!")
    
    # Try to load the saved session
    print("Loading saved LinkedIn session...")
    page, browser, context = load_linkedin_state_and_scrape()
    
    if page is None or browser is None or context is None:
        print("❌ Failed to load saved session. You may need to log in again.")
        return None, None, None
        
    print("✅ Session loaded successfully!")
    print(f"Current URL: {page.url}")
    return page, browser, context

def main():
    print("="*80)
    print("🚀 LINKEDIN SCRAPER WITH AUTO SESSION HANDLING")
    print("="*80)
    
    # Try to use saved session first
    page, browser, context = check_and_use_saved_session()
    
    if page is None:
        print("\n📝 Need to log in manually...")
        print("Please run 'python manual_login_and_save.py' to create a new session.")
        return
        
    try:
        # At this point, you're logged in and can perform scraping operations
        print("\n🔍 You're now logged in with the saved session!")
        print("Performing a quick test...")
        
        # Example: Navigate to a search page
        try:
            # Wait for search bar to appear
            page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
            print("✅ Ready to perform scraping operations!")
            
            # Here you can add your actual scraping logic
            # For example:
            # page.fill('[placeholder*="Search"]', 'Python Developer')
            # page.press('[placeholder*="Search"]', 'Enter')
            # ... rest of your scraping code
            
        except Exception as e:
            print(f"⚠️ Warning: Could not find search bar ({e})")
            print("Session might still be valid, continuing anyway...")
            
        print("\n" + "="*80)
        print("🎉 SUCCESS! You're using a saved session.")
        print("You didn't need to log in again!")
        print("="*80)
        
        # Keep browser open for continued use
        print("\n🤖 Browser kept open for 30 seconds for testing...")
        print("Press Ctrl+C to exit early")
        
        # Wait for 30 seconds or until user interrupts
        try:
            time.sleep(30)
        except KeyboardInterrupt:
            print("\nExiting...")
            
    except Exception as e:
        print(f"❌ Error during session use: {e}")
    finally:
        # Clean up resources
        try:
            if browser is not None:
                browser.close()
                print("✅ Browser closed successfully!")
        except Exception as e:
            print(f"❌ Error closing browser: {e}")

if __name__ == "__main__":
    main()