"""
Simple test to verify session loading works correctly
"""

from playwright.sync_api import sync_playwright
import time


def test_session_loading():
    """
    Test session loading
    """
    print("Testing session loading...")
    
    with sync_playwright() as p:
        print("Launching Firefox browser...")
        browser = p.firefox.launch(headless=False)
        
        print("Creating context with saved session...")
        context = browser.new_context(storage_state="linkedin_auth.json")
        
        print("Creating new page...")
        page = context.new_page()
        
        print("Navigating to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=15000)
        
        # Wait for page to load
        try:
            page.wait_for_load_state('domcontentloaded', timeout=10000)
        except:
            print("⚠ Page load timeout, continuing anyway...")
        
        time.sleep(3)
        
        current_url = page.url.lower()
        print(f"Current URL: {page.url}")
        
        # Check if we're logged in
        if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
            print("✅ Successfully logged in with saved session!")
        elif "login" in current_url:
            print("❌ Session invalid, redirected to login page")
        else:
            print("⚠ Unclear if logged in, checking page content...")
            
            # Try to find navigation elements
            try:
                nav_elements = page.query_selector_all('nav a')
                linkedin_indicators = 0
                
                for element in nav_elements:
                    text_content = element.text_content()
                    if text_content is not None:
                        text = text_content.strip().lower()
                        if any(keyword in text for keyword in ['home', 'my network', 'jobs', 'messaging', 'me']):
                            linkedin_indicators += 1
                
                if linkedin_indicators >= 2:
                    print("✅ Found navigation elements, likely logged in")
                else:
                    print("⚠ Not enough navigation elements found")
            except Exception as e:
                print(f"Error checking navigation elements: {e}")
        
        # Keep browser open for observation
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    test_session_loading()