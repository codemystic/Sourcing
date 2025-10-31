"""
Debug script to understand what's happening with session redirects
"""

from playwright.sync_api import sync_playwright
import time


def debug_session_redirect():
    """
    Debug session redirect behavior
    """
    print("Debugging session redirect behavior...")
    
    with sync_playwright() as p:
        print("Launching Firefox browser...")
        browser = p.firefox.launch(headless=False)
        
        print("Creating context with saved session...")
        context = browser.new_context(storage_state="linkedin_auth.json")
        
        print("Creating new page...")
        page = context.new_page()
        
        print("Enabling console logging...")
        page.on("console", lambda msg: print(f"Console: {msg.text}"))
        page.on("request", lambda request: print(f"Request: {request.url}"))
        page.on("response", lambda response: print(f"Response: {response.status} {response.url}"))
        
        print("Navigating to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=15000, wait_until="domcontentloaded")
        
        print(f"Initial URL: {page.url}")
        time.sleep(2)
        
        # Check URL multiple times
        for i in range(5):
            print(f"Check {i+1}: {page.url}")
            time.sleep(2)
        
        # Try to find navigation elements
        try:
            nav_elements = page.query_selector_all('nav a')
            print(f"Found {len(nav_elements)} navigation elements")
            
            for i, element in enumerate(nav_elements[:5]):  # Show first 5
                text = element.text_content()
                if text:
                    print(f"  Nav element {i+1}: {text.strip()}")
        except Exception as e:
            print(f"Error checking navigation elements: {e}")
        
        # Try to click on the feed link if we can find it
        try:
            feed_link = page.query_selector('a[href="/feed/"]')
            if feed_link:
                print("Found feed link, clicking it...")
                feed_link.click()
                time.sleep(3)
                print(f"URL after clicking feed link: {page.url}")
            else:
                print("No feed link found")
        except Exception as e:
            print(f"Error clicking feed link: {e}")
        
        # Keep browser open for observation
        print("Keeping browser open for 10 seconds for observation...")
        time.sleep(10)
        browser.close()


if __name__ == "__main__":
    debug_session_redirect()