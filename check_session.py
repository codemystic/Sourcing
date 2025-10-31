"""
Script to check if the LinkedIn session file exists and is valid
"""

import os
import json


def check_session_file():
    """
    Check if the LinkedIn session file exists and is valid
    """
    session_file = "linkedin_auth.json"
    
    print("="*80)
    print("🔍 CHECKING LINKEDIN SESSION FILE")
    print("="*80)
    
    # Check if file exists
    if not os.path.exists(session_file):
        print(f"❌ Session file '{session_file}' not found.")
        print("\nTo create a session file, you can:")
        print("1. Run 'python linkedin_scraper.py' (will automatically save session after login)")
        print("2. Run 'python manual_login_and_save.py' (for manual login with 2FA)")
        return False
    
    print(f"✅ Session file '{session_file}' found.")
    
    # Check file size
    file_size = os.path.getsize(session_file)
    print(f"📄 File size: {file_size} bytes")
    
    if file_size == 0:
        print("❌ Session file is empty.")
        print("Please run 'python linkedin_scraper.py' or 'python manual_login_and_save.py' to create a new session.")
        return False
    
    # Try to parse JSON
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        print("✅ Session file is valid JSON.")
        
        # Check structure
        if not isinstance(session_data, dict):
            print("❌ Session file does not contain a JSON object.")
            return False
            
        if 'cookies' not in session_data:
            print("❌ Session file missing 'cookies' key.")
            return False
            
        cookies = session_data.get('cookies', [])
        print(f"🍪 Number of cookies: {len(cookies)}")
        
        if len(cookies) == 0:
            print("⚠️  Session file contains no cookies (may be expired).")
            return False
            
        # Check some cookie properties
        valid_cookies = 0
        for cookie in cookies:
            if isinstance(cookie, dict) and 'name' in cookie and 'value' in cookie:
                valid_cookies += 1
                
        print(f"✅ Valid cookies: {valid_cookies}")
        
        if valid_cookies == 0:
            print("❌ No valid cookies found in session file.")
            return False
            
        print("\n✅ Session file appears to be valid!")
        print("You can now use it with the session loader.")
        return True
        
    except json.JSONDecodeError as e:
        print(f"❌ Session file is not valid JSON: {e}")
        return False
    except Exception as e:
        print(f"❌ Error reading session file: {e}")
        return False


def main():
    """Main function"""
    try:
        is_valid = check_session_file()
        if not is_valid:
            print("\n❌ Session file is not valid or missing.")
        else:
            print("\n✅ Session file is ready to use!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
    
    print("\n" + "="*80)
    print("🏁 SESSION CHECK COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()