"""
Auto Session Handler for LinkedIn Scraper

This script demonstrates how to automatically use saved sessions
to avoid repeated logins.
"""

import os
from linkedin_session_loader import load_linkedin_state_and_scrape

def has_saved_session():
    """Check if a saved session exists"""
    return os.path.exists("linkedin_auth.json") and os.path.getsize("linkedin_auth.json") > 0

def load_saved_session():
    """Load a saved session if available"""
    if not has_saved_session():
        print("No saved session found.")
        return None, None, None
    
    print("Loading saved LinkedIn session...")
    return load_linkedin_state_and_scrape()

def main():
    print("="*60)
    print("AUTO SESSION HANDLER")
    print("="*60)
    
    # Check for saved session
    if has_saved_session():
        print("✅ Saved session found!")
        page, browser, context = load_saved_session()
        
        if page and browser and context:
            print("✅ Successfully loaded saved session!")
            print(f"Current page: {page.url}")
            
            # Your scraping logic would go here
            print("You can now perform scraping without logging in!")
            
            # Don't forget to close the browser when done
            browser.close()
            return True
        else:
            print("❌ Failed to load saved session")
            return False
    else:
        print("❌ No saved session found.")
        print("Please run 'python manual_login_and_save.py' to create one.")
        return False

if __name__ == "__main__":
    main()