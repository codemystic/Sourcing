"""
Test script for improved search functionality
"""

from playwright.sync_api import sync_playwright
import time


def test_search_functionality():
    """
    Test the improved search functionality
    """
    print("Testing improved search functionality...")
    
    with sync_playwright() as p:
        print("Launching Firefox browser...")
        browser = p.firefox.launch(headless=False)
        page = browser.new_page()
        
        print("Navigating to LinkedIn...")
        page.goto("https://www.linkedin.com/feed/")
        time.sleep(3)
        
        # Test search bar interaction
        print("Testing search bar interaction...")
        try:
            page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
            print("✓ Search bar found")
            
            search_bar = page.query_selector('[placeholder*="Search"]')
            if search_bar:
                # Scroll to search bar
                search_bar.scroll_into_view_if_needed()
                time.sleep(1)
                
                # Try clicking
                search_bar.click()
                print("✓ Search bar clicked")
                time.sleep(1)
                
                # Type search query
                search_query = "Python Developer"
                search_bar.type(search_query, delay=50)
                print(f"✓ Typed search query: {search_query}")
                time.sleep(2)
                
                # Submit search
                page.press('[placeholder*="Search"]', 'Enter')
                print("✓ Search submitted")
                time.sleep(3)
                
                # Check if we're on search results page
                current_url = page.url.lower()
                if 'search' in current_url and 'results' in current_url:
                    print("✓ Successfully navigated to search results")
                else:
                    print(f"⚠ Not on expected search results page. Current URL: {current_url}")
                    
            else:
                print("✗ Search bar element not found")
                
        except Exception as e:
            print(f"✗ Error during search test: {e}")
        
        # Keep browser open briefly for observation
        time.sleep(5)
        browser.close()
        print("Test completed!")


if __name__ == "__main__":
    test_search_functionality()