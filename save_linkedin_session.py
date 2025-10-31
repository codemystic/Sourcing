"""
LinkedIn Session Saver

This script opens a browser window for manual LinkedIn login and saves the authenticated session state
to a file for later use with the scraper. This approach is recommended for handling 2FA and other
authentication challenges.
"""

from playwright.sync_api import sync_playwright
import time


def save_linkedin_state():
    """
    Open a browser for manual LinkedIn login and save the authenticated session state.
    
    This function is useful for handling 2FA and other authentication challenges that
    cannot be automated. After manually logging in, the session state is saved to
    'linkedin_auth.json' for use with the scraper.
    """
    
    print("="*80)
    print("🚀 LINKEDIN SESSION SAVER")
    print("="*80)
    print("This script will open a browser window for manual LinkedIn login.")
    print("You can handle 2FA, CAPTCHA, and other authentication challenges manually.")
    print("After login completes, the session will be saved automatically.\n")
    
    try:
        with sync_playwright() as p:
            # Launch browser in non-headless mode to allow manual interaction
            browser = p.firefox.launch(headless=False)
            context = browser.new_context()
            page = context.new_page()
            
            print("Opening LinkedIn login page...")
            page.goto("https://www.linkedin.com/login")
            
            # Wait for page to load
            page.wait_for_load_state('networkidle')
            time.sleep(3)
            
            print("\n" + "="*80)
            print("📋 MANUAL LOGIN INSTRUCTIONS")
            print("="*80)
            print("1. Log in to LinkedIn manually in the opened browser window")
            print("2. Complete any 2FA or CAPTCHA challenges if prompted")
            print("3. Wait until you're fully logged in and on your LinkedIn feed")
            print("4. DO NOT close the browser window yourself")
            print("="*80)
            
            print("\n⏳ Waiting for you to log in...")
            print("   (This script will automatically detect when you're logged in)")
            
            # Wait for successful login by checking for elements that appear when logged in
            logged_in = False
            check_count = 0
            max_checks = 60  # Wait up to 10 minutes (10 seconds * 60)
            
            while not logged_in and check_count < max_checks:
                # Check current URL
                current_url = page.url.lower()
                
                # Check if we're on a LinkedIn page that indicates logged-in state
                if any(pattern in current_url for pattern in ['/feed', '/in/', '/mynetwork', '/jobs']):
                    print(f"✅ Detected logged-in state (URL: {current_url})")
                    logged_in = True
                    break
                
                # Check for navigation elements that appear when logged in
                try:
                    nav_elements = page.query_selector_all('nav a')
                    linkedin_indicators = 0
                    
                    for element in nav_elements:
                        text_content = element.text_content()
                        if text_content is not None:
                            text = text_content.strip().lower()
                            if any(keyword in text for keyword in ['home', 'my network', 'jobs', 'messaging', 'me']):
                                linkedin_indicators += 1
                    
                    # If we find multiple LinkedIn navigation elements, likely logged in
                    if linkedin_indicators >= 2:
                        print("✅ Detected logged-in state (navigation elements)")
                        logged_in = True
                        break
                        
                except Exception as e:
                    pass  # Continue checking
                
                # Check for profile elements
                try:
                    profile_elements = [
                        'img[alt*="profile"]',
                        '.nav-item__profile-member-photo',
                        '.global-nav__me-photo'
                    ]
                    
                    for selector in profile_elements:
                        element = page.query_selector(selector)
                        if element:
                            print("✅ Detected logged-in state (profile elements)")
                            logged_in = True
                            break
                            
                    if logged_in:
                        break
                        
                except Exception as e:
                    pass  # Continue checking
                
                # Wait before next check
                time.sleep(10)
                check_count += 1
                print(f"   Check {check_count}/{max_checks}...")
            
            if logged_in:
                print("\n✅ Login detected! Saving session state...")
                
                # Save the authenticated session state
                context.storage_state(path="linkedin_auth.json")
                print("✅ Saved LinkedIn auth to 'linkedin_auth.json'")
                print("   You can now use this session with the LinkedIn scraper!")
                
                # Keep browser open for a few seconds so user can see success message
                time.sleep(5)
            else:
                print("\n⚠️  Timeout waiting for login. Saving current session state anyway...")
                context.storage_state(path="linkedin_auth.json")
                print("✅ Saved current session state to 'linkedin_auth.json'")
                print("   Note: Session may not be fully authenticated")
            
            # Close browser
            browser.close()
            print("\n✅ Browser closed. Session saving complete!")
            
    except Exception as e:
        print(f"\n❌ Error during session saving: {e}")
        print("Please try running the script again.")


def main():
    """Main function to run the LinkedIn session saver."""
    try:
        save_linkedin_state()
    except KeyboardInterrupt:
        print("\n\n⚠️  Script interrupted by user. Session may not be saved.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "="*80)
    print("🏁 LINKEDIN SESSION SAVER COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()