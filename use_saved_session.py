"""
Example script showing how to use saved LinkedIn session to avoid logging in every time
"""

from linkedin_session_loader import load_linkedin_state_and_scrape
import time


def scrape_with_saved_session():
    """
    Use saved session to perform scraping without logging in
    """
    print("="*80)
    print("🚀 USING SAVED LINKEDIN SESSION")
    print("="*80)
    
    # Load the saved session
    print("Loading saved LinkedIn session...")
    page, browser, context = load_linkedin_state_and_scrape()
    
    if page is None or browser is None or context is None:
        print("❌ Failed to load session")
        return
    
    try:
        print("✅ Session loaded successfully!")
        print(f"Current URL: {page.url}")
        
        # Wait a moment for page to stabilize
        time.sleep(2)
        
        # Check if we're on LinkedIn
        if "linkedin.com" in page.url.lower():
            print("✅ Successfully on LinkedIn site")
            
            # Now you can perform scraping without logging in
            # Example: Navigate to a search page
            print("\n🔍 Performing a quick test...")
            
            # Try to find the search bar
            try:
                page.wait_for_selector('[placeholder*="Search"]', timeout=5000)
                print("✅ Search bar found - session is working!")
            except:
                print("⚠️ Search bar not immediately visible, but session may still be valid")
            
        else:
            print("⚠️ Not on LinkedIn site - session may have issues")
        
        # Keep browser open for continued use for a short time
        print("\n" + "="*80)
        print("🤖 BROWSER KEPT OPEN FOR 30 SECONDS FOR TESTING")
        print("="*80)
        print("You can interact with the browser manually.")
        print("Browser will close automatically in 30 seconds.")
        print("="*80)
        
        # Keep the script running for 30 seconds then close
        time.sleep(30)
        print("\nClosing browser automatically...")
            
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
    scrape_with_saved_session()
    print("\n" + "="*80)
    print("🏁 SESSION USAGE COMPLETE")
    print("="*80)