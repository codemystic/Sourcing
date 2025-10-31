"""
Check if the LinkedIn session file is valid and not expired
"""

import json
import time


def check_session_validity():
    """
    Check if the LinkedIn session file is valid and not expired
    """
    session_file = "linkedin_auth.json"
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        print("Session file loaded successfully")
        print(f"Number of cookies: {len(session_data.get('cookies', []))}")
        
        # Check for important cookies
        important_cookies = ['li_at', 'JSESSIONID', 'li_rm']
        current_time = time.time()
        valid_cookies = 0
        expired_cookies = 0
        
        for cookie in session_data.get('cookies', []):
            name = cookie.get('name', '')
            expires = cookie.get('expires', -1)
            
            if name in important_cookies:
                if expires == -1:
                    print(f"  ✅ {name}: Session cookie (no expiration)")
                    valid_cookies += 1
                elif expires > current_time:
                    days_left = (expires - current_time) / 86400
                    print(f"  ✅ {name}: Valid for {days_left:.1f} days (expires {time.ctime(expires)})")
                    valid_cookies += 1
                else:
                    print(f"  ❌ {name}: EXPIRED ({time.ctime(expires)})")
                    expired_cookies += 1
        
        print(f"\nSummary:")
        print(f"  Valid cookies: {valid_cookies}")
        print(f"  Expired cookies: {expired_cookies}")
        
        if expired_cookies > 0:
            print("\n⚠️  Some important cookies have expired.")
            print("   You may need to create a new session.")
            return False
        elif valid_cookies > 0:
            print("\n✅ Session appears to be valid.")
            return True
        else:
            print("\n⚠️  No important cookies found.")
            return False
            
    except Exception as e:
        print(f"❌ Error checking session: {e}")
        return False


if __name__ == "__main__":
    is_valid = check_session_validity()
    if is_valid:
        print("\n✅ You can use the saved session for scraping.")
    else:
        print("\n❌ You should create a new session by logging in.")