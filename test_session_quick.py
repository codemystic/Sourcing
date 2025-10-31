"""
Quick test for LinkedIn session loading
"""

from linkedin_session_loader import load_linkedin_state_and_scrape
import time


def quick_session_test():
    """
    Quick test to load LinkedIn session
    """
    print("Testing LinkedIn session loading...")
    
    # Load session without verification for quick test
    page, browser, context = load_linkedin_state_and_scrape(verify_login=False)
    
    if page is None or browser is None or context is None:
        print("❌ Failed to load session")
        return
    
    try:
        print("✅ Session loaded successfully!")
        print(f"Current URL: {page.url}")
        
        # Test a simple action
        try:
            page.wait_for_selector('body', timeout=5000)
            print("✅ Page is responsive")
        except Exception as e:
            print(f"⚠️ Page may not be fully responsive: {e}")
        
        # Wait a moment to see if everything loads
        time.sleep(3)
        
    except Exception as e:
        print(f"❌ Error during session test: {e}")
    finally:
        # Always close browser in this test
        try:
            browser.close()
            print("✅ Browser closed")
        except:
            pass
        
    print("✅ Session test completed!")


if __name__ == "__main__":
    quick_session_test()