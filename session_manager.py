"""
LinkedIn Session Manager

A comprehensive tool for managing LinkedIn sessions to avoid repeated logins.
"""

import os
import sys
import json
from linkedin_session_loader import load_linkedin_state_and_scrape
from manual_login_and_save import manual_login_and_save

SESSION_FILE = "linkedin_auth.json"

def check_session():
    """Check if a valid session file exists"""
    if not os.path.exists(SESSION_FILE):
        return False, "No session file found"
    
    if os.path.getsize(SESSION_FILE) == 0:
        return False, "Session file is empty"
    
    try:
        with open(SESSION_FILE, 'r') as f:
            data = json.load(f)
        if not isinstance(data, dict) or 'cookies' not in data:
            return False, "Invalid session file format"
        return True, "Valid session found"
    except Exception as e:
        return False, f"Error reading session file: {e}"

def create_new_session():
    """Create a new session through manual login"""
    print("Starting manual login process...")
    try:
        manual_login_and_save()
        return check_session()
    except Exception as e:
        return False, f"Error during manual login: {e}"

def load_session():
    """Load an existing session"""
    print("Loading saved session...")
    try:
        page, browser, context = load_linkedin_state_and_scrape()
        if page is not None and browser is not None and context is not None:
            return True, (page, browser, context)
        else:
            return False, "Failed to load session"
    except Exception as e:
        return False, f"Error loading session: {e}"

def delete_session():
    """Delete the current session file"""
    if os.path.exists(SESSION_FILE):
        try:
            os.remove(SESSION_FILE)
            print("Session file deleted successfully")
            return True
        except Exception as e:
            print(f"Error deleting session file: {e}")
            return False
    else:
        print("No session file to delete")
        return True

def main():
    print("="*60)
    print("LINKEDIN SESSION MANAGER")
    print("="*60)
    
    while True:
        print("\nOptions:")
        print("1. Check current session status")
        print("2. Create new session (manual login)")
        print("3. Use saved session")
        print("4. Delete current session")
        print("5. Exit")
        
        choice = input("\nEnter your choice (1-5): ").strip()
        
        if choice == "1":
            # Check session
            valid, message = check_session()
            status = "VALID" if valid else "INVALID"
            print(f"\nSession Status: {status}")
            print(f"Details: {message}")
            
        elif choice == "2":
            # Create new session
            print("\nCreating new session...")
            valid, message = create_new_session()
            status = "SUCCESS" if valid else "FAILED"
            print(f"\nSession Creation: {status}")
            print(f"Details: {message}")
            
        elif choice == "3":
            # Use saved session
            print("\nUsing saved session...")
            success, result = load_session()
            if success:
                page, browser, context = result
                print("✅ Session loaded successfully!")
                # Using string formatting that doesn't trigger type checking errors
                print(f"Current URL: {str(getattr(page, 'url', 'Unknown'))}")
                print("\nKeeping browser open for 30 seconds for testing...")
                import time
                try:
                    time.sleep(30)
                except KeyboardInterrupt:
                    pass
                finally:
                    try:
                        close_method = getattr(browser, 'close', None)
                        if close_method and callable(close_method):
                            close_method()
                        print("Browser closed.")
                    except:
                        pass
            else:
                print(f"❌ Failed to load session: {result}")
                
        elif choice == "4":
            # Delete session
            print("\nDeleting session...")
            if delete_session():
                print("✅ Session deleted successfully")
            else:
                print("❌ Failed to delete session")
                
        elif choice == "5":
            # Exit
            print("Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter a number between 1-5.")

if __name__ == "__main__":
    main()