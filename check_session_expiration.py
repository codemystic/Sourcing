"""
Check if LinkedIn session has expired by examining cookie expiration dates
"""

import json
import time


def check_session_expiration():
    """
    Check if LinkedIn session has expired
    """
    print("="*80)
    print("🔍 CHECKING LINKEDIN SESSION EXPIRATION")
    print("="*80)
    
    session_file = "linkedin_auth.json"
    
    try:
        with open(session_file, 'r') as f:
            session_data = json.load(f)
        
        cookies = session_data.get('cookies', [])
        print(f"Found {len(cookies)} cookies")
        
        # Check important cookies
        important_cookies = ['li_at', 'JSESSIONID', 'li_rm']
        current_time = time.time()
        expired_count = 0
        valid_count = 0
        
        print("\nChecking important cookies:")
        for cookie in cookies:
            name = cookie.get('name', '')
            expires = cookie.get('expires', -1)
            
            if name in important_cookies:
                if expires == -1:
                    print(f"  ✅ {name}: Session cookie (no expiration)")
                    valid_count += 1
                elif expires > current_time:
                    days_left = (expires - current_time) / 86400
                    print(f"  ✅ {name}: Valid for {days_left:.1f} days (expires {time.ctime(expires)})")
                    valid_count += 1
                else:
                    print(f"  ❌ {name}: EXPIRED ({time.ctime(expires)})")
                    expired_count += 1
        
        print(f"\nSummary:")
        print(f"  Valid cookies: {valid_count}")
        print(f"  Expired cookies: {expired_count}")
        
        if expired_count > 0:
            print("\n⚠️  Some important cookies have expired.")
            print("   You may need to create a new session.")
        elif valid_count > 0:
            print("\n✅ Session appears to be valid.")
            print("   You should be able to use it for scraping.")
        else:
            print("\n⚠️  No important cookies found.")
            print("   Session may not be valid for LinkedIn.")
            
    except Exception as e:
        print(f"❌ Error checking session: {e}")


if __name__ == "__main__":
    check_session_expiration()