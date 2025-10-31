"""
Test script to verify reCAPTCHA checkbox clicking functionality
"""

import time
from playwright.sync_api import sync_playwright

def test_checkbox_clicking():
    """Test reCAPTCHA checkbox detection and clicking"""
    
    print("🧪 Starting reCAPTCHA checkbox clicking test...")
    
    # Start browser
    playwright = sync_playwright().start()
    browser = playwright.firefox.launch(headless=False)
    page = browser.new_page()
    
    try:
        # Navigate to a page with reCAPTCHA (using Google's test page)
        print("🌐 Navigating to reCAPTCHA test page...")
        page.goto("https://www.google.com/recaptcha/api2/demo")
        time.sleep(3)
        
        # Look for reCAPTCHA iframe
        print("🔍 Looking for reCAPTCHA iframe...")
        recaptcha_iframe = page.query_selector('iframe[title*="reCAPTCHA"]')
        
        if recaptcha_iframe:
            print("✅ Found reCAPTCHA iframe")
            
            # Get iframe bounding box
            bbox = recaptcha_iframe.bounding_box()
            if bbox:
                # Calculate center position
                checkbox_x = bbox['x'] + bbox['width'] / 2
                checkbox_y = bbox['y'] + bbox['height'] / 2
                print(f"📍 Checkbox position: ({checkbox_x}, {checkbox_y})")
                
                # Move mouse to checkbox
                print("🖱️  Moving mouse to checkbox...")
                page.mouse.move(checkbox_x, checkbox_y)
                time.sleep(1)
                
                # Get iframe content
                iframe_element = page.frame_locator('iframe[title*="reCAPTCHA"]').first
                
                # Look for checkbox element
                checkbox = iframe_element.locator('.recaptcha-checkbox-border, #recaptcha-anchor')
                
                if checkbox:
                    print("✅ Found checkbox element")
                    print("🖱️  Clicking checkbox...")
                    
                    # Try clicking the checkbox
                    try:
                        checkbox.click(timeout=5000)
                        print("✅ Checkbox clicked!")
                        
                        # Wait to see if it was successful
                        time.sleep(3)
                        
                        # Check if checkbox is now checked
                        checked = iframe_element.locator('.recaptcha-checkbox-checked')
                        if checked.count() > 0:
                            print("✅ Checkbox is now checked!")
                        else:
                            print("⚠️  Checkbox clicked but not checked")
                            
                    except Exception as e:
                        print(f"❌ Error clicking checkbox: {e}")
                else:
                    print("❌ Could not find checkbox element")
            else:
                print("❌ Could not get iframe bounding box")
        else:
            print("❌ No reCAPTCHA iframe found")
            
    except Exception as e:
        print(f"❌ Error during test: {e}")
    
    finally:
        # Close browser
        print("🔚 Closing browser...")
        browser.close()
        playwright.stop()
        
    print("🏁 Test completed!")

if __name__ == "__main__":
    test_checkbox_clicking()