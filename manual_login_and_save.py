"""
Script to manually log in to LinkedIn and save the session for future use
Useful for handling 2FA and other authentication challenges
"""

from playwright.sync_api import sync_playwright
import time


def manual_login_and_save():
    """
    Open browser for manual login and save authenticated session
    """
    print("="*80)
    print("🔐 MANUAL LINKEDIN LOGIN")
    print("="*80)
    print("This script will open a browser window for manual LinkedIn login.")
    print("You can handle 2FA, CAPTCHA, and other authentication challenges.")
    print("After login completes, the session will be saved automatically.\n")
    
    try:
        with sync_playwright() as p:
            # Launch browser in non-headless mode
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
            
            # Wait for successful login by checking URL
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
                
                # Wait before next check
                time.sleep(10)
                check_count += 1
                print(f"   Check {check_count}/{max_checks}...")
            
            if logged_in:
                print("\n✅ Login detected! Saving session state...")
                
                # Save the authenticated session state
                context.storage_state(path="linkedin_auth.json")
                print("✅ Saved LinkedIn auth to 'linkedin_auth.json'")
                print("   You can now use this session with the scraper!")
            else:
                print("\n⚠️ Timeout waiting for login. Saving current session state anyway...")
                context.storage_state(path="linkedin_auth.json")
                print("✅ Saved current session state to 'linkedin_auth.json'")
            
            # Close browser
            browser.close()
            print("\n✅ Browser closed. Session saving complete!")
            
    except Exception as e:
        print(f"\n❌ Error during session saving: {e}")
        print("Please try running the script again.")


def main():
    """Main function"""
    try:
        manual_login_and_save()
    except KeyboardInterrupt:
        print("\n\n⚠️ Script interrupted by user.")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "="*80)
    print("🏁 MANUAL LOGIN COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()