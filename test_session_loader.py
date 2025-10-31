"""
Test script for the LinkedIn session loader functionality.
"""

import os
import sys

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from linkedin_session_loader import load_linkedin_state_and_scrape


def test_session_loading():
    """
    Test the session loading functionality.
    """
    print("="*80)
    print("🧪 TESTING LINKEDIN SESSION LOADER")
    print("="*80)
    
    # Check if session file exists
    session_file = "linkedin_auth.json"
    if not os.path.exists(session_file):
        print(f"⚠️  Session file '{session_file}' not found.")
        print("   Please run 'linkedin_scraper.py' first to create a session file.")
        return
    
    print(f"✅ Found session file: {session_file}")
    
    # Try to load the session
    print("\n🔄 Attempting to load LinkedIn session...")
    page, browser, context = load_linkedin_state_and_scrape()
    
    if page and browser and context:
        print("✅ Session loaded successfully!")
        print(f"📄 Current page URL: {page.url}")
        
        # Test navigation to a public profile
        try:
            print("\n🔍 Testing navigation to a public profile...")
            page.goto("https://www.linkedin.com/in/elonmusk")
            page.wait_for_load_state('networkidle')
            print("✅ Navigation successful!")
            
            # Get page title as a simple test
            title = page.title()
            print(f"📄 Page title: {title}")
            
        except Exception as e:
            print(f"⚠️  Navigation test failed: {e}")
        
        # Close browser
        print("\n🛑 Closing browser...")
        browser.close()
        print("✅ Browser closed successfully!")
        
    else:
        print("❌ Failed to load session")


if __name__ == "__main__":
    test_session_loading()
    print("\n🏁 Test completed!")