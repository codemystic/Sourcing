"""
LinkedIn Session Loader Module

This module provides functionality to load an existing authenticated LinkedIn session
using Playwright and a stored session state file (linkedin_auth.json).
"""

from playwright.sync_api import sync_playwright
import json
import os
import time
from human_behavior import HumanBehavior, move_mouse_naturally


def is_session_valid(page) -> bool:
    """
    Check if the current session appears to be valid (user is logged in).
    
    Args:
        page: Playwright page object
        
    Returns:
        bool: True if session appears valid, False otherwise
    """
    try:
        # Check if we're on a LinkedIn page
        current_url = page.url.lower()
        print(f"Checking session validity for URL: {current_url}")
        
        # If we're on LinkedIn and not on a login page, likely logged in
        if "linkedin.com" in current_url and "login" not in current_url:
            print("On LinkedIn site and not on login page")
            return True
            
        # Check for common elements that indicate a logged-in user
        logged_in_indicators = [
            'img[alt*="profile photo"]',
            'img[alt*="profile picture"]',
            'nav[aria-label="primary"]',
            'a[href*="/mynetwork/"]',
            'a[href*="/jobs/"]',
            '[data-control-name="nav.homepage"]',
            '[data-control-name="nav.mynetwork"]',
            '[data-control-name="nav.jobs"]',
            '.nav-item__profile-member-photo',
            '.global-nav__me-photo'
        ]
        
        found_indicators = 0
        for selector in logged_in_indicators:
            try:
                element = page.query_selector(selector)
                if element:
                    print(f"Found logged-in indicator: {selector}")
                    found_indicators += 1
                    if found_indicators >= 2:  # If we find 2 indicators, likely logged in
                        return True
            except:
                continue
                
        # Check for error messages that indicate login issues
        error_indicators = [
            'login',
            'sign in',
            'authentication',
            'verify your identity'
        ]
        
        page_text = ""
        try:
            page_text = page.text_content('body').lower()
        except:
            pass
            
        for indicator in error_indicators:
            if indicator in page_text and "linkedin.com" in current_url:
                # But if we're on a LinkedIn page and see these words, 
                # it might just be part of normal content
                if indicator == "login" and "login" not in current_url:
                    # "Login" might just be in the page content, not indicating a problem
                    continue
                elif indicator != "login":
                    # Other indicators on LinkedIn site might be problematic
                    print(f"Found potential login issue indicator: {indicator}")
                    return False
                    
        return found_indicators > 0  # Return True if we found any indicators
    except Exception as e:
        print(f"Error in session validation: {e}")
        return False


def load_linkedin_state_and_scrape(verify_login=True, playwright_instance=None):
    """
    Load an existing LinkedIn session from stored state and perform scraping.
    
    This function loads authentication state from 'linkedin_auth.json' file,
    initializes a browser session with that state, and navigates to LinkedIn feed.
    
    Args:
        verify_login (bool): Whether to verify the login was successful
        playwright_instance: Optional existing Playwright instance to use
        
    Returns:
        tuple: (page, browser, context) if successful, (None, None, None) if failed
    """
    
    # Check if session file exists
    session_file = "linkedin_auth.json"
    if not os.path.exists(session_file):
        print(f"Error: Session file '{session_file}' not found.")
        print("Please ensure you have a valid LinkedIn session state file.")
        print("Run 'python linkedin_scraper.py' or 'python manual_login_and_save.py' to create one.")
        return None, None, None
    
    # Verify the session file is valid JSON and not empty
    try:
        if os.path.getsize(session_file) == 0:
            print(f"Error: Session file '{session_file}' is empty.")
            print("Please run 'python linkedin_scraper.py' or 'python manual_login_and_save.py' to create a new session.")
            return None, None, None
            
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        if not isinstance(session_data, dict):
            print(f"Error: Session file '{session_file}' is not a valid session state file.")
            print("Please run 'python linkedin_scraper.py' or 'python manual_login_and_save.py' to create a new session.")
            return None, None, None
            
        if 'cookies' not in session_data or not session_data['cookies']:
            print(f"Warning: Session file '{session_file}' contains no cookies.")
            print("Session might be invalid or expired.")
            
    except json.JSONDecodeError:
        print(f"Error: Session file '{session_file}' is not valid JSON.")
        print("Please run 'python linkedin_scraper.py' or 'python manual_login_and_save.py' to create a new session.")
        return None, None, None
    except Exception as e:
        print(f"Error reading session file: {e}")
        print("Please run 'python linkedin_scraper.py' or 'python manual_login_and_save.py' to create a new session.")
        return None, None, None
    
    try:
        # Use provided Playwright instance or create new one
        if playwright_instance is not None:
            p = playwright_instance
            need_to_stop = False
        else:
            p = sync_playwright().start()
            need_to_stop = True
            
        try:
            # Launch browser in non-headless mode to avoid detection
            print("Launching Firefox browser...")
            browser = p.firefox.launch(headless=False)
            print("✅ Firefox browser launched")
            
            print("Creating browser context with session...")
            context = browser.new_context(storage_state=session_file)
            print("✅ Browser context created with session")
            
            print("Creating new page...")
            page = context.new_page()
            print("✅ New page created")
            
            print("Loading LinkedIn session...")
            # Add error handling for page navigation with shorter timeout
            try:
                print("Navigating to LinkedIn feed...")
                page.goto("https://www.linkedin.com/feed/", timeout=15000)
                print("✅ Navigated to LinkedIn feed")
                
                # Wait for basic page elements with shorter timeout
                print("Waiting for basic page elements...")
                try:
                    page.wait_for_selector('body', timeout=5000)
                except:
                    pass
                time.sleep(2)
                print("✅ Basic page elements loaded")
            except Exception as nav_error:
                print(f"Warning: Could not navigate to feed page: {nav_error}")
                # Try a different page
                try:
                    print("Trying alternative navigation to LinkedIn home...")
                    page.goto("https://www.linkedin.com/", timeout=15000)
                    try:
                        page.wait_for_selector('body', timeout=5000)
                    except:
                        pass
                    time.sleep(2)
                    print("✅ Navigated to LinkedIn home")
                except Exception as second_nav_error:
                    print(f"Warning: Could not navigate to home page: {second_nav_error}")
                    # Continue anyway, session might still be valid
            
            print(f"Current URL: {page.url}")
            
            if verify_login:
                print("Verifying login status...")
                # Simplified verification
                current_url = page.url.lower()
                if "linkedin.com" in current_url and "login" not in current_url:
                    print("✅ Session appears to be valid")
                    return page, browser, context
                else:
                    print("⚠ Warning: Session may not be valid")
                    # Check if we can still return the page
                    if "linkedin.com" in current_url:
                        print("✅ Returning page anyway (on LinkedIn site)")
                        return page, browser, context
                    else:
                        print("❌ Session does not appear to be valid")
                        return None, None, None
            else:
                print("✓ LinkedIn session loaded (verification skipped)")
                return page, browser, context
                
        except Exception as e:
            print(f"Error loading LinkedIn session: {e}")
            import traceback
            traceback.print_exc()
            return None, None, None
        finally:
            # Only stop Playwright if we created it
            if need_to_stop and hasattr(p, 'stop'):
                try:
                    p.stop()
                except:
                    pass
                    
        return page, browser, context
                
    except Exception as e:
        print(f"Error loading LinkedIn session: {e}")
        import traceback
        traceback.print_exc()
        return None, None, None


def save_current_session(context, filename="linkedin_auth.json"):
    """
    Save the current browser context state to a file for future use.
    
    Args:
        context: Playwright browser context
        filename (str): Name of file to save session state to
    """
    try:
        context.storage_state(path=filename)
        print(f"✓ Session state saved to {filename}")
    except Exception as e:
        print(f"Error saving session state: {e}")


def scrape_with_existing_session(search_query="AI Engineer"):
    """
    Perform scraping using an existing authenticated session.
    
    Args:
        search_query (str): Query to search for on LinkedIn
    """
    
    print("="*80)
    print("🚀 LINKEDIN SESSION LOADER")
    print("="*80)
    
    # Load existing session
    page, browser, context = load_linkedin_state_and_scrape()
    
    if page is None or browser is None or context is None:
        print("❌ Failed to load LinkedIn session")
        return
    
    try:
        # Perform a search using the authenticated session
        print(f"\n🔍 Performing search for: '{search_query}'")
        
        # Find and click the search bar
        try:
            page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
            search_bar = page.query_selector('[placeholder*="Search"]')
            
            if search_bar:
                # Move mouse naturally to search bar
                bbox = search_bar.bounding_box()
                if bbox:
                    target_x = bbox['x'] + bbox['width'] / 2
                    target_y = bbox['y'] + bbox['height'] / 2
                    move_mouse_naturally(page, target_x, target_y, duration=2.0)
                
                # Click the search bar to focus it
                HumanBehavior.human_click(search_bar, pre_click_delay=(0.5, 1.0), post_click_delay=(0.8, 1.5))
                
                # Type the search keyword
                print(f"Entering search keyword: {search_query}")
                HumanBehavior.human_type(search_bar, search_query, min_delay=80, max_delay=200)
                
                # Simulate reading/confirmation
                HumanBehavior.simulate_thinking((1.0, 2.0))
                print("Search keyword entered successfully")
                
                # Press Enter to perform the search
                page.press('[placeholder*="Search"]', 'Enter')
                print("Search submitted")
                
                # Wait for results
                HumanBehavior.simulate_thinking((2.0, 4.0))
                
                # Wait for search results page to load
                page.wait_for_url('**/search/results/**', timeout=15000)
                print("Search results page loaded successfully")
                
            else:
                print("Error: Search bar element not found")
                
        except Exception as e:
            print(f"Error performing search: {e}")
        
        # Keep browser open for continued use
        print("\n" + "="*80)
        print("🤖 BROWSER KEPT OPEN FOR CONTINUED BROWSING")
        print("="*80)
        print("You can continue using the browser manually.")
        print("Press Ctrl+C in this console to exit completely.")
        print("="*80)
        
        # Keep the script running to maintain browser open
        try:
            while True:
                time.sleep(10)  # Keep alive
        except KeyboardInterrupt:
            print("\nReceived interrupt signal, closing browser...")
            
    finally:
        # Clean up resources
        try:
            if browser is not None:
                browser.close()
        except:
            pass


if __name__ == "__main__":
    scrape_with_existing_session()