"""
Example usage of the LinkedIn session loader module.

This script demonstrates how to load an existing authenticated LinkedIn session
and perform scraping without having to log in each time.
"""

from linkedin_session_loader import load_linkedin_state_and_scrape, scrape_with_existing_session
import time


def main():
    """
    Main function demonstrating session loading functionality.
    """
    print("="*80)
    print("🚀 LINKEDIN SESSION LOADER EXAMPLE")
    print("="*80)
    
    # Example 1: Load session and get page object for custom scraping
    print("\n📝 Example 1: Load session and perform custom actions")
    page, browser, context = load_linkedin_state_and_scrape()
    
    if page and browser and context:
        print("✅ Session loaded successfully!")
        print(f"📄 Current page URL: {page.url}")
        
        # You can now perform any custom scraping actions here
        # For example, navigate to a specific profile or perform a custom search
        
        # For demonstration, let's just close the browser after a short delay
        print("⏳ Keeping browser open for 5 seconds for demonstration...")
        time.sleep(5)
        browser.close()
    else:
        print("❌ Failed to load session")
        return
    
    # Example 2: Use the built-in scraping function
    print("\n" + "="*80)
    print("📝 Example 2: Use built-in scraping function")
    print("="*80)
    
    # This will load the session and perform a search
    # Note: This will keep the browser open indefinitely until Ctrl+C is pressed
    # Uncomment the line below to run this example:
    # scrape_with_existing_session("Machine Learning Engineer")


if __name__ == "__main__":
    main()
    print("\n✅ Example completed!")