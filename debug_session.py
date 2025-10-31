"""
Debug script to test LinkedIn session loading step by step
"""

from playwright.sync_api import sync_playwright
import json
import os
import time


def debug_session_loading():
    """
    Debug LinkedIn session loading step by step
    """
    print("="*80)
    print("🔍 DEBUGGING LINKEDIN SESSION LOADING")
    print("="*80)
    
    session_file = "linkedin_auth.json"
    
    # Step 1: Check session file
    print("Step 1: Checking session file...")
    if not os.path.exists(session_file):
        print(f"❌ Session file '{session_file}' not found.")
        return
    
    print(f"✅ Session file found: {session_file}")
    
    # Step 2: Load and validate session file
    print("Step 2: Loading and validating session file...")
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        if not isinstance(session_data, dict) or 'cookies' not in session_data:
            print("❌ Session file is not valid.")
            return
            
        print(f"✅ Session file loaded successfully. Cookies: {len(session_data.get('cookies', []))}")
    except Exception as e:
        print(f"❌ Error loading session file: {e}")
        return
    
    # Step 3: Initialize Playwright
    print("Step 3: Initializing Playwright...")
    try:
        with sync_playwright() as p:
            print("✅ Playwright initialized")
            
            # Step 4: Launch browser
            print("Step 4: Launching Firefox browser...")
            try:
                browser = p.firefox.launch(headless=False)
                print("✅ Firefox browser launched")
                
                # Step 5: Create context with session
                print("Step 5: Creating browser context with session...")
                try:
                    context = browser.new_context(storage_state=session_file)
                    print("✅ Browser context created with session")
                    
                    # Step 6: Create page
                    print("Step 6: Creating new page...")
                    try:
                        page = context.new_page()
                        print("✅ New page created")
                        
                        # Step 7: Navigate to LinkedIn
                        print("Step 7: Navigating to LinkedIn...")
                        try:
                            print("   Going to https://www.linkedin.com/feed/")
                            page.goto("https://www.linkedin.com/feed/", timeout=30000)
                            print("✅ Navigated to LinkedIn feed")
                            
                            # Step 8: Wait for page load
                            print("Step 8: Waiting for page to load...")
                            page.wait_for_load_state('networkidle', timeout=30000)
                            time.sleep(3)
                            print("✅ Page loaded")
                            
                            # Step 9: Check current URL
                            print("Step 9: Checking current URL...")
                            current_url = page.url
                            print(f"✅ Current URL: {current_url}")
                            
                            print("\n🎉 Session loading completed successfully!")
                            print("The session file is working correctly.")
                            
                        except Exception as e:
                            print(f"❌ Error navigating to LinkedIn: {e}")
                            # Try alternative URL
                            try:
                                print("   Trying alternative URL: https://www.linkedin.com/")
                                page.goto("https://www.linkedin.com/", timeout=30000)
                                print("✅ Navigated to LinkedIn home")
                                page.wait_for_load_state('networkidle', timeout=30000)
                                time.sleep(3)
                                print("✅ Page loaded")
                                current_url = page.url
                                print(f"✅ Current URL: {current_url}")
                            except Exception as e2:
                                print(f"❌ Error with alternative URL: {e2}")
                                
                    except Exception as e:
                        print(f"❌ Error creating page: {e}")
                        
                except Exception as e:
                    print(f"❌ Error creating context: {e}")
                    
            except Exception as e:
                print(f"❌ Error launching browser: {e}")
                
    except Exception as e:
        print(f"❌ Error initializing Playwright: {e}")
    
    print("\n" + "="*80)
    print("🏁 DEBUG SESSION LOADING COMPLETE")
    print("="*80)


if __name__ == "__main__":
    debug_session_loading()