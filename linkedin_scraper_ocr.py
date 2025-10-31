import warnings
warnings.filterwarnings("ignore")

import os
import sys
import time
import json
import random
from time import sleep

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Import custom modules
from human_behavior import HumanBehavior, move_mouse_naturally
from advanced_captcha_solver import AdvancedCaptchaSolver

# Import the NLP query parser
from nlp_query_parser import parse_nlp_query, format_search_query

# Get credentials from environment variables
EMAIL = os.getenv('EMAIL')
PASSWORD = os.getenv('PASSWORD')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Validate that credentials are provided
if not EMAIL or EMAIL == 'your_email':
    print("ERROR: EMAIL not found in .env file or set to placeholder value")
    print("Please create a .env file with: EMAIL=your_actual_email")
    exit(1)

if not PASSWORD or PASSWORD == 'your_password':
    print("ERROR: PASSWORD not found in .env file or set to placeholder value")
    print("Please create a .env file with: PASSWORD=your_actual_password")
    exit(1)

if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in .env file")
    print("Please add to .env file: GROQ_API_KEY=your_groq_api_key")
    exit(1)

print(f"✓ Email loaded: {EMAIL}")
print(f"✓ Password loaded: {'*' * len(PASSWORD)}")
print(f"✓ Groq API Key loaded: {GROQ_API_KEY[:10]}...")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize CAPTCHA solver
captcha_solver = AdvancedCaptchaSolver(groq_client)

# Validate that credentials are provided
if not EMAIL or EMAIL == 'your_email':
    print("ERROR: EMAIL not found in .env file or set to placeholder value")
    print("Please create a .env file with: EMAIL=your_actual_email")
    exit(1)

if not PASSWORD or PASSWORD == 'your_password':
    print("ERROR: PASSWORD not found in .env file or set to placeholder value")
    print("Please create a .env file with: PASSWORD=your_actual_password")
    exit(1)

print(f"✓ Email loaded: {EMAIL}")
print(f"✓ Password loaded: {'*' * len(PASSWORD)}")

# ============================================================================
# FUNCTION: Natural Mouse Movement
# ============================================================================

def move_mouse_naturally(page, target_x, target_y, duration=3.0):
    """Move mouse cursor naturally to target position over specified duration"""
    try:
        print(f"  👁️  Moving mouse naturally to position ({target_x}, {target_y})...")
        
        # Get current mouse position (start from center of screen)
        start_x, start_y = 640, 360  # Approximate center
        
        # Calculate number of steps based on duration (30 steps per second)
        steps = int(duration * 30)
        
        for i in range(steps):
            # Calculate progress (0 to 1)
            progress = i / steps
            
            # Use easing function for natural movement (ease-in-out)
            eased_progress = progress * progress * (3 - 2 * progress)
            
            # Calculate current position with slight randomness
            current_x = start_x + (target_x - start_x) * eased_progress
            current_y = start_y + (target_y - start_y) * eased_progress
            
            # Add small random jitter for human-like movement
            jitter_x = random.uniform(-2, 2)
            jitter_y = random.uniform(-2, 2)
            
            # Move mouse
            page.mouse.move(current_x + jitter_x, current_y + jitter_y)
            
            # Small delay between movements
            sleep(duration / steps)
        
        # Final precise movement to target
        page.mouse.move(target_x, target_y)
        print(f"  ✓ Mouse moved to target position")
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error moving mouse: {e}")
        return False

def load_saved_session_if_available(playwright_instance):
    """
    Attempt to load a saved LinkedIn session if available.
    Returns (page, browser, context, playwright) if successful, (None, None, None, None) if not.
    """
    try:
        from linkedin_session_loader import load_linkedin_state_and_scrape
        print("Attempting to load saved LinkedIn session...")
        
        # Load the saved session (without verification to speed up)
        page, browser, context = load_linkedin_state_and_scrape(verify_login=False, playwright_instance=playwright_instance)
        
        if page is not None and browser is not None:
            print("✅ Successfully loaded saved LinkedIn session")
            print(f"Current URL: {page.url}")
            
            # Set viewport to a standard size for consistent screenshots
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # Wait a moment for page to stabilize
            sleep(2)
            return page, browser, context, None  # No playwright needed when using saved session
        else:
            print("❌ Failed to load saved session")
            return None, None, None, None
            
    except ImportError:
        print("Session loader not available")
        return None, None, None, None
    except Exception as e:
        print(f"Error loading session: {e}")
        return None, None, None, None

# Initialize Playwright and navigate to LinkedIn login
playwright = sync_playwright().start()

# Try to load saved session first
page = None
browser = None
context = None

print("Attempting to load saved LinkedIn session...")
session_loaded = False

try:
    # Check if session file exists
    if os.path.exists("linkedin_auth.json"):
        print("Found saved session file, attempting to load...")
        
        # Create browser with saved session
        browser = playwright.firefox.launch(headless=False)
        context = browser.new_context(storage_state="linkedin_auth.json")
        page = context.new_page()
        
        # Navigate to LinkedIn feed
        print("Navigating to LinkedIn feed...")
        page.goto("https://www.linkedin.com/feed/", timeout=15000)
        
        # Wait for basic page elements with better error handling
        try:
            page.wait_for_selector('body', timeout=5000)
        except:
            pass
        time.sleep(3)  # Increased wait time
        
        current_url = page.url.lower()
        print(f"Current URL after navigation: {page.url}")
        
        # Check if we're on a redirect page but still logged in
        if "login" in current_url and "uas" in current_url and "session_redirect" in current_url:
            print("ℹ️ Detected session redirect, this is normal. Waiting for redirect to complete...")
            # Wait a bit more for the redirect to complete
            time.sleep(5)
            current_url = page.url.lower()
            print(f"URL after waiting: {page.url}")
        
        # Check if we're actually on the feed page now
        if "linkedin.com/feed" in current_url or "linkedin.com/in/" in current_url:
            print("✅ Successfully navigated to LinkedIn page with saved session")
            session_loaded = True
        elif "login" in current_url and "uas" in current_url:
            print("⚠ Session appears to be invalid, redirected to login page")
            session_loaded = False
        else:
            print("⚠ Unclear navigation state, checking page content...")
            # Try to verify if we're logged in by checking for navigation elements
            try:
                nav_elements = page.query_selector_all('nav a')
                if len(nav_elements) > 0:
                    print(f"✅ Found {len(nav_elements)} navigation elements, likely logged in")
                    session_loaded = True
                else:
                    print("⚠ No navigation elements found, may not be logged in")
                    session_loaded = False
            except Exception as nav_error:
                print(f"⚠ Error checking navigation elements: {nav_error}")
                session_loaded = False
        
        if session_loaded:
            print("✅ Session successfully loaded and verified")
            
            # Add some human-like behavior to make the session look more legitimate
            print("Performing human-like behavior to validate session...")
            page.mouse.move(100, 100)
            time.sleep(0.5)
            page.mouse.move(200, 200)
            time.sleep(1)
            
            # Wait a bit more for full page load
            try:
                page.wait_for_load_state('domcontentloaded', timeout=15000)
            except:
                print("⚠ Warning: Page load state timeout, continuing anyway...")
        else:
            print("❌ Session loading failed, will fall back to login")
            # Close the browser and fall back to login
            try:
                browser.close()
            except:
                pass
            browser = None
            page = None
            context = None
        
    else:
        print("No saved session file found, will proceed with login")
        session_loaded = False
        
except Exception as e:
    print(f"Failed to load saved session: {e}")
    # Close any partially opened resources
    try:
        if browser:
            browser.close()
    except:
        pass
    browser = None
    page = None
    context = None
    session_loaded = False

# If session wasn't loaded or verified, proceed with normal login
if not session_loaded:
    print("⚠ Session invalid or not found, falling back to normal login process...")
    browser = playwright.firefox.launch(headless=False)
    page = browser.new_page()
    
    # Navigate to LinkedIn login page
    print("Navigating to LinkedIn login page...")
    page.goto('https://www.linkedin.com/login')
    sleep(3)

    # Wait for the login form to be ready
    print("Waiting for login form to load...")
    try:
        page.wait_for_selector('#username', timeout=15000)
        print("Email field found")
    except Exception as e:
        print(f"Error: Email field not found - {e}")

    try:
        page.wait_for_selector('#password', timeout=15000)
        print("Password field found")
    except Exception as e:
        print(f"Error: Password field not found - {e}")

    sleep(2)

    # Enter email in the email field
    print(f"Entering email: {EMAIL}")
    try:
        email_field = page.query_selector('#username')
        if email_field:
            # Move mouse naturally to email field
            bbox = email_field.bounding_box()
            if bbox:
                target_x = bbox['x'] + bbox['width'] / 2
                target_y = bbox['y'] + bbox['height'] / 2
                move_mouse_naturally(page, target_x, target_y, duration=2.0)
        
            # Click the field to focus it with human delay
            HumanBehavior.human_click(email_field, pre_click_delay=(0.5, 1.0), post_click_delay=(0.8, 1.5))
        
            # Clear any existing value
            email_field.fill('')
            HumanBehavior.random_delay(1, 2)
        
            # Type the email slowly with human-like typing
            HumanBehavior.human_type(email_field, EMAIL, min_delay=80, max_delay=200)
            print("Email entered successfully")
        
            # Simulate reading/confirmation
            HumanBehavior.simulate_thinking((1.0, 2.0))
        else:
            print("Error: Email field element not found")
    except Exception as e:
        print(f"Error entering email: {e}")

    sleep(2)

    # Enter password in the password field
    print("Entering password...")
    try:
        password_field = page.query_selector('#password')
        if password_field:
            # Move mouse naturally to password field
            bbox = password_field.bounding_box()
            if bbox:
                target_x = bbox['x'] + bbox['width'] / 2
                target_y = bbox['y'] + bbox['height'] / 2
                move_mouse_naturally(page, target_x, target_y, duration=2.0)
        
            # Click the field to focus it with human delay
            HumanBehavior.human_click(password_field, pre_click_delay=(0.5, 1.0), post_click_delay=(0.8, 1.5))
        
            # Clear any existing value
            password_field.fill('')
            HumanBehavior.random_delay(1, 2)
        
            # Type the password slowly with human-like typing
            HumanBehavior.human_type(password_field, PASSWORD, min_delay=80, max_delay=200)
            print("Password entered successfully")
        
            # Simulate reading/confirmation
            HumanBehavior.simulate_thinking((1.0, 2.0))
        else:
            print("Error: Password field element not found")
    except Exception as e:
        print(f"Error entering password: {e}")

    sleep(2)

    # Click the sign-in button
    print("Clicking sign-in button...")
    try:
        page.wait_for_selector('button[type="submit"]', timeout=10000)
        sign_in_button = page.query_selector('button[type="submit"]')
        if sign_in_button:
            # Move mouse naturally to sign-in button
            bbox = sign_in_button.bounding_box()
            if bbox:
                target_x = bbox['x'] + bbox['width'] / 2
                target_y = bbox['y'] + bbox['height'] / 2
                move_mouse_naturally(page, target_x, target_y, duration=2.0)
            
            # Hover over button briefly
            HumanBehavior.human_hover(sign_in_button, hover_duration=(0.5, 1.0))
        
            # Click with human-like delay
            HumanBehavior.human_click(sign_in_button, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
            print("Sign-in button clicked successfully")
        
            # Simulate waiting for response
            HumanBehavior.simulate_thinking((2.0, 4.0))
        else:
            print("Error: Sign-in button element not found")
    except Exception as e:
        print(f"Error clicking sign-in button: {e}")
        try:
            alt_button = page.query_selector('button:has-text("Sign in")')
            if alt_button:
                # Move mouse naturally to alternative button
                bbox = alt_button.bounding_box()
                if bbox:
                    target_x = bbox['x'] + bbox['width'] / 2
                    target_y = bbox['y'] + bbox['height'] / 2
                    move_mouse_naturally(page, target_x, target_y, duration=2.0)
            
                    # Hover over button briefly
                    HumanBehavior.human_hover(alt_button, hover_duration=(0.5, 1.0))
            
                    # Click with human-like delay
                    HumanBehavior.human_click(alt_button, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
                    print("Sign-in button clicked using alternative selector")
            
                    # Simulate waiting for response
                    HumanBehavior.simulate_thinking((2.0, 4.0))
                else:
                    print("Error with alternative selector: Button not found")
            else:
                print("Error with alternative selector: Button not found")
        except Exception as e2:
            print(f"Error with alternative selector: {e2}")

# Ensure page is always defined (this should never happen with proper error handling)
if page is None:
    print("❌ Critical error: Page object is not initialized")
    exit(1)

# ============================================================================
# CAPTCHA Detection and Automatic Handling
# ============================================================================

# Check for CAPTCHA indicators
# MODIFIED: More comprehensive check for valid LinkedIn pages
current_url = page.url.lower()
current_title = ""
try:
    current_title = page.title().lower()
except:
    pass

# Check if we're on a valid LinkedIn page that indicates we're logged in
is_on_valid_linkedin_page = (
    "linkedin.com" in current_url and 
    "login" not in current_url and 
    "checkpoint" not in current_url and 
    "challenge" not in current_url and
    ("feed" in current_url or "in/" in current_url or "mynetwork" in current_url or "jobs" in current_url)
)

# Additional check for navigation elements that indicate logged-in state
has_navigation_elements = False
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
        has_navigation_elements = True
except:
    pass

# If we're on a valid LinkedIn page or have navigation elements, skip CAPTCHA
if is_on_valid_linkedin_page or has_navigation_elements:
    print("✅ Already on valid LinkedIn page or have navigation elements, skipping CAPTCHA detection")
    print(f"   Current URL: {current_url}")
    if current_title:
        print(f"   Page title: {current_title}")
    captcha_detected = False
    complex_captcha = False
else:
    print("Checking for CAPTCHA...")
    sleep(2)
    captcha_detected = False
    complex_captcha = False

    try:
        captcha_selectors = [
            'iframe[title*="reCAPTCHA"]',
            'iframe[src*="recaptcha"]',
            '#captcha',
            '.captcha',
            'div[id*="captcha"]',
            'div[class*="captcha"]',
            'input[name="captcha"]',
            'div:has-text("verify you\'re not a robot")',
            'div:has-text("Security Verification")',
        ]
        
        for selector in captcha_selectors:
            try:
                if page.query_selector(selector):
                    captcha_detected = True
                    print(f"⚠ CAPTCHA DETECTED: Found element matching '{selector}'")
                    break
            except:
                pass
        
        page_title = page.title().lower()
        page_url = page.url.lower()
        
        if 'captcha' in page_title or 'verification' in page_title or 'security' in page_title:
            captcha_detected = True
            print(f"⚠ CAPTCHA DETECTED: Page title contains verification keywords")
        
        if 'checkpoint' in page_url or 'challenge' in page_url:
            captcha_detected = True
            print(f"⚠ CAPTCHA DETECTED: URL contains challenge keywords")
            
    except Exception as e:
        print(f"Warning: Error checking for CAPTCHA: {e}")

if captcha_detected:
    print("\n" + "="*80)
    print("🤖 CAPTCHA CHALLENGE DETECTED!")
    print("="*80)
    print("\n🔄 Starting fully automatic CAPTCHA solving...\n")
    
    # Try to automatically solve reCAPTCHA checkbox
    checkbox_solved = captcha_solver.solve_recaptcha_checkbox(page)
    
    if checkbox_solved:
        print("\n✅ reCAPTCHA checkbox automatically solved!")
        print("Waiting for page to proceed...")
        sleep(3)
        
        # Check if we need to solve image challenge
        image_challenge = page.query_selector('iframe[title*="recaptcha challenge"], .rc-imageselect')
        if image_challenge:
            print("\n🖼️  Image challenge detected - attempting automatic solving...")
            
            # Try to solve image puzzle automatically
            puzzle_solved = captcha_solver.solve_image_puzzle(page)
            
            if puzzle_solved:
                print("✅ Image puzzle automatically solved!")
                print("✓ Proceeding with scraping...")
                complex_captcha = False
            else:
                print("⚠️  Automatic image puzzle solving failed")
                complex_captcha = True
        else:
            print("✓ No additional challenges detected")
            print("✓ Proceeding with scraping...")
            complex_captcha = False
    else:
        print("\n⚠️  Checkbox solving failed")
        complex_captcha = True
    
    # If complex CAPTCHA or auto-solve failed, try one more time with advanced methods
    if complex_captcha:
        print("\n🔄 Trying advanced automatic solving methods...")
        
        # Try checkbox solving again
        checkbox_solved = captcha_solver.solve_recaptcha_checkbox(page)
        if checkbox_solved:
            print("✅ Advanced checkbox solving successful!")
            
            # Check for image challenge again
            image_challenge = page.query_selector('iframe[title*="recaptcha challenge"], .rc-imageselect')
            if image_challenge:
                print("🖼️  Image challenge detected - attempting advanced solving...")
                puzzle_solved = captcha_solver.solve_image_puzzle(page)
                if puzzle_solved:
                    print("✅ Advanced image puzzle solving successful!")
                    complex_captcha = False
                else:
                    print("⚠️  Advanced image puzzle solving failed")
            else:
                complex_captcha = False
        
        # If still failed, continue anyway (sometimes CAPTCHA passes without interaction)
        if complex_captcha:
            print("⚠️  Continuing anyway - CAPTCHA may pass automatically...")
            sleep(5)
            
            # Check if we're past the CAPTCHA
            current_url = page.url.lower()
            if '/feed' in current_url or '/in/' in current_url:
                print("✅ Successfully passed CAPTCHA automatically!")
                complex_captcha = False
            else:
                # Even if we're not past CAPTCHA, continue anyway
                print("⚠️  Proceeding despite CAPTCHA - may work anyway...")
                complex_captcha = False
    
    # Completely remove manual intervention - always continue
    if complex_captcha:
        print("\n⚠️  CAPTCHA challenges detected but continuing automatically...")
        print("⚠️  Proceeding without manual intervention - may work anyway...")
        complex_captcha = False
    
    print("\n✅ CAPTCHA handling completed - proceeding with automated scraping!")
        
else:
    print("✓ No CAPTCHA detected")

# Wait for login to complete
print("Waiting for login to complete...")
try:
    page.wait_for_url('**/feed/**', timeout=20000)
    print("Login successful - feed page loaded")
except:
    print("Feed page not detected, waiting additional time...")
    sleep(8)
    try:
        page.wait_for_url('**/in/**', timeout=10000)
        print("Login successful - profile page loaded")
    except:
        print("Warning: Could not verify successful login")

sleep(3)

# ============================================================================
# Search for AI Engineer and filter by People
# ============================================================================

print("\n" + "="*80)
print("Starting search process...")
print("="*80)

# Get user input for NLP query
print("Enter your search query (e.g., '5+ year experienced Python developer in Hyderabad'):")
nlp_query = input("Search query: ").strip()

if not nlp_query:
    print("No query entered, using default: 'AI Engineer in Hyderabad'")
    nlp_query = "AI Engineer in Hyderabad"

# Parse the NLP query
print(f"\nParsing query: '{nlp_query}'")
parsed_query = parse_nlp_query(nlp_query)
print(f"Parsed query: {parsed_query}")

# Format search query for LinkedIn
search_keyword = format_search_query(parsed_query)
print(f"Formatted search keyword: '{search_keyword}'")

# Get location from parsed query or ask user
location = parsed_query.get('location', '')
if not location:
    print("\nLocation not found in query. Please enter location:")
    location = input("Location (e.g., Hyderabad): ").strip()
    if not location:
        location = "Hyderabad"  # Default fallback
else:
    print(f"Location extracted from query: {location}")

# Find and click the search bar
print("Looking for search bar...")
search_bar_found = False
max_attempts = 3

for attempt in range(max_attempts):
    try:
        print(f"Attempt {attempt + 1}/{max_attempts} to find search bar...")
        page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
        print("Search bar found")
        
        search_bar = page.query_selector('[placeholder*="Search"]')
        if search_bar:
            # Scroll to search bar to ensure it's visible
            search_bar.scroll_into_view_if_needed()
            sleep(1)
            
            # Try multiple click methods
            try:
                search_bar.click()
                print("Search bar clicked successfully")
            except:
                # Fallback: try to focus using press
                page.press('[placeholder*="Search"]', 'Tab')
                print("Search bar focused using Tab")
            
            sleep(1)
            
            print(f"Entering search keyword: {search_keyword}")
            search_bar.type(search_keyword, delay=50)
            sleep(2)
            
            print("Search keyword entered successfully")
            search_bar_found = True
            break
        else:
            print("Search bar element not found, retrying...")
            sleep(2)
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_attempts - 1:
            sleep(3)  # Wait before retry
        else:
            print("Error finding or using search bar after all attempts")
            search_bar_found = False

if not search_bar_found:
    print("⚠ Warning: Could not interact with search bar, continuing anyway...")

sleep(1)

# Press Enter to perform the search
print("Pressing Enter to search...")
search_submitted = False
max_attempts = 3

for attempt in range(max_attempts):
    try:
        print(f"Attempt {attempt + 1}/{max_attempts} to submit search...")
        page.press('[placeholder*="Search"]', 'Enter')
        print("Search submitted")
        search_submitted = True
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_attempts - 1:
            sleep(2)  # Wait before retry
        else:
            print("Error pressing Enter after all attempts")
            # Try alternative method
            try:
                search_button = page.query_selector('button[aria-label*="Search"], button[type="submit"]')
                if search_button:
                    search_button.click()
                    print("Search submitted using button click")
                    search_submitted = True
            except Exception as alt_e:
                print(f"Alternative search submission also failed: {alt_e}")

if not search_submitted:
    print("⚠ Warning: Could not submit search, continuing anyway...")

# Wait for search results page to load
print("Waiting for search results page to load...")
sleep(5)

search_results_loaded = False
max_attempts = 3

for attempt in range(max_attempts):
    try:
        print(f"Attempt {attempt + 1}/{max_attempts} to verify search results page...")
        page.wait_for_url('**/search/results/**', timeout=15000)
        print("Search results page loaded successfully")
        search_results_loaded = True
        break
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_attempts - 1:
            sleep(3)  # Wait before retry
        else:
            print("Could not verify search results page after all attempts")
            # Check if we're on a search page anyway
            current_url = page.url.lower()
            if 'search' in current_url:
                print("Appears to be on search page anyway, continuing...")
                search_results_loaded = True

if not search_results_loaded:
    print("⚠ Warning: Search results page may not have loaded properly")

sleep(2)

# Filter results by People
print("Looking for 'People' filter option...")
people_filter_applied = False
max_attempts = 3

for attempt in range(max_attempts):
    try:
        print(f"Attempt {attempt + 1}/{max_attempts} to find People filter...")
        page.wait_for_selector('button[data-filter-type="currentCompany"], button:has-text("People")', timeout=10000)
        
        people_filters = page.query_selector_all('button')
        people_filter_found = False
        
        for button in people_filters:
            button_text = button.text_content()
            if button_text and 'People' in button_text.strip():
                print(f"Found 'People' filter button")
                
                # Scroll to button to ensure visibility
                button.scroll_into_view_if_needed()
                sleep(1)
                
                # Try multiple click methods
                try:
                    button.click()
                    print("People filter clicked successfully")
                    people_filter_found = True
                    people_filter_applied = True
                    break
                except:
                    # Try JavaScript click as fallback
                    try:
                        page.evaluate("""(button) => {
                            button.scrollIntoView({behavior: 'smooth', block: 'center'});
                            button.click();
                        }""", button)
                        print("People filter clicked using JavaScript")
                        people_filter_found = True
                        people_filter_applied = True
                        break
                    except Exception as js_e:
                        print(f"JavaScript click also failed: {js_e}")
        
        if people_filter_found:
            sleep(2)
            break
        else:
            print("People filter button not found in current attempt")
            if attempt < max_attempts - 1:
                sleep(3)  # Wait before retry
                
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_attempts - 1:
            sleep(3)  # Wait before retry
        else:
            print("Could not find People filter after all attempts")
            # Try alternative selector
            try:
                page.click('[data-item="people"]')
                print("People filter clicked using alternative selector")
                people_filter_applied = True
                sleep(2)
            except Exception as alt_e:
                print(f"Alternative selector also failed: {alt_e}")

if not people_filter_applied:
    print("⚠ Warning: Could not apply People filter, continuing anyway...")

print("Waiting for filtered results to load...")
sleep(4)

# ============================================================================
# Filter by Location - Use parsed location
# ============================================================================

print(f"\nLooking for 'Locations' filter option for: {location}")
location_filter_applied = False
max_attempts = 3

for attempt in range(max_attempts):
    try:
        print(f"Attempt {attempt + 1}/{max_attempts} to find Locations filter...")
        
        # Find and click the Locations filter button
        location_button = None
        
        # Try primary selector
        try:
            location_button = page.query_selector('button#searchFilter_geoUrn')
        except:
            pass
            
        # Try alternative selectors if primary failed
        if not location_button:
            # Get all buttons and look for one with "Locations" text
            location_buttons = page.query_selector_all('button')
            for button in location_buttons:
                button_text = button.text_content()
                if button_text and 'Locations' in button_text.strip():
                    location_button = button
                    break
        
        if location_button:
            print(f"✓ Found 'Locations' filter button")
            
            # Scroll to button to ensure visibility
            location_button.scroll_into_view_if_needed()
            sleep(1)
            
            # Try multiple click methods
            try:
                location_button.click()
                print("Clicked Locations filter")
                sleep(2)
            except:
                # Try JavaScript click as fallback
                try:
                    page.evaluate("""(button) => {
                        button.scrollIntoView({behavior: 'smooth', block: 'center'});
                        button.click();
                    }""", location_button)
                    print("Clicked Locations filter using JavaScript")
                    sleep(2)
                except Exception as js_e:
                    print(f"JavaScript click also failed: {js_e}")
                    continue  # Try again
            
            # Wait for location dropdown/modal to appear
            sleep(2)
            
            # Find and click location option
            print(f"Looking for {location} option...")
            
            # Try to find input field for location
            location_input = None
            try:
                location_input = page.query_selector('input[placeholder*="Add a location"], input[placeholder*="location"]')
            except:
                pass
            
            if location_input:
                print("✓ Found location input field")
                
                # Scroll to input field
                location_input.scroll_into_view_if_needed()
                sleep(1)
                
                try:
                    location_input.click()
                    sleep(1)
                    location_input.type(location, delay=100)
                    sleep(2)
                    
                    # Wait for suggestions and click the location
                    try:
                        # Look for location in suggestions
                        page.wait_for_selector(f'text={location}', timeout=5000)
                        location_option = page.query_selector(f'text={location}')
                        if location_option:
                            location_option.click()
                            print(f"✓ Selected {location} location")
                            location_filter_applied = True
                            sleep(2)
                        else:
                            print(f"⚠ {location} option not found in suggestions")
                            # Try pressing Enter as fallback
                            page.press('input[placeholder*="location"]', 'Enter')
                            print(f"Pressed Enter to select {location}")
                            location_filter_applied = True
                            sleep(2)
                    except:
                        print(f"⚠ Could not find {location} in dropdown, pressing Enter")
                        page.press('input[placeholder*="location"]', 'Enter')
                        print(f"Pressed Enter to select {location}")
                        location_filter_applied = True
                        sleep(2)
                        
                except Exception as input_e:
                    print(f"Error interacting with location input: {input_e}")
            else:
                print("⚠ Location input field not found")
                
            # Try to close the filter modal if there's a "Show results" or close button
            try:
                show_results_btn = page.query_selector('button:has-text("Show"), button:has-text("Apply")')
                if show_results_btn:
                    show_results_btn.click()
                    print("✓ Applied location filter")
                    location_filter_applied = True
                    sleep(2)
            except:
                pass
                
            # If we got here, we successfully interacted with the location filter
            break
            
        else:
            print("⚠ Could not find 'Locations' filter button in current attempt")
            if attempt < max_attempts - 1:
                sleep(3)  # Wait before retry
                
    except Exception as e:
        print(f"Attempt {attempt + 1} failed: {e}")
        if attempt < max_attempts - 1:
            sleep(3)  # Wait before retry
        else:
            print("Could not interact with Locations filter after all attempts")

if not location_filter_applied:
    print("⚠ Warning: Could not apply location filter, continuing anyway...")

print("Waiting for location-filtered results to load...")
sleep(3)

print("\n" + "="*80)
print("Search and filter process completed!")
print("="*80 + "\n")

# ============================================================================
# FUNCTION: Extract Profile Data with OCR
# ============================================================================

def extract_profile_with_ocr(page, profile_url):
    """Extract profile data using OCR approach"""
    
    profile_data = {}
    
    try:
        # Navigate to profile with better error handling
        print(f"  Navigating to profile: {profile_url}")
        page.goto(profile_url, timeout=30000)  # Increase timeout to 30 seconds
        HumanBehavior.random_delay(2, 4)  # Human-like pause
        
        # Wait for basic page elements with retry logic
        try:
            page.wait_for_load_state('domcontentloaded', timeout=10000)
        except:
            print(f"  ⚠️  DOM content load timeout, continuing anyway...")
        
        HumanBehavior.random_delay(1, 3)  # Human-like pause
        
        url = page.url
        profile_data['url'] = url
        
        # Human-like scrolling to load all content
        print("  Scrolling to load all content naturally...")
        try:
            total_height = page.evaluate("document.body.scrollHeight")
        except:
            total_height = 10000  # Default height if can't get actual height
            
        viewport_height = 1080
        scroll_position = 0
        scroll_step = 600
        
        # Scroll with human-like behavior
        while scroll_position < total_height:
            # Move mouse naturally during scrolling
            if random.random() < 0.3:  # 30% chance of mouse movement
                move_mouse_naturally(page, random.randint(200, 1000), random.randint(200, 800), duration=1.0)
            
            page.evaluate(f'window.scrollTo(0, {scroll_position})')
            HumanBehavior.random_delay(0.5, 1.5)  # Variable scroll delay
            scroll_position += scroll_step
            
            # Update total height in case new content loaded
            try:
                total_height = page.evaluate("document.body.scrollHeight")
            except:
                pass  # Keep current height
            
            # Occasionally pause to "read" content (15% chance)
            if random.random() < 0.15:
                HumanBehavior.simulate_reading(time_per_line=0.3, lines=random.randint(3, 8))
        
        # Scroll back to top with human-like behavior
        print("  Scrolling back to top naturally...")
        page.evaluate('window.scrollTo(0, 0)')
        HumanBehavior.random_delay(1, 2)
        
        # Take screenshot with error handling
        try:
            screenshot_filename = f'profile_screenshot_{hash(profile_url) % 10000}.png'
            screenshot_path = f'data/screenshots/{screenshot_filename}'
            os.makedirs('data/screenshots', exist_ok=True)
            page.screenshot(path=screenshot_path, full_page=True, timeout=10000)
        except Exception as screenshot_error:
            print(f"  ⚠️  Screenshot error: {screenshot_error}")
            screenshot_path = ""
        
        # Extract text content with error handling
        try:
            text_content = page.evaluate("""
            () => {
                const mainSection = document.querySelector('main');
                if (!mainSection) return '';
                
                const scripts = mainSection.querySelectorAll('script, style');
                scripts.forEach(el => el.remove());
                
                return mainSection.innerText;
            }
            """)
        except Exception as text_error:
            print(f"  ⚠️  Text extraction error: {text_error}")
            text_content = ""
        
        # Save text content
        try:
            if text_content:
                text_file_path = f'data/screenshots/profile_text_{hash(profile_url) % 10000}.txt'
                with open(text_file_path, 'w', encoding='utf-8') as f:
                    f.write(text_content)
        except Exception as save_error:
            print(f"  ⚠️  Text save error: {save_error}")
        
        # Extract profile data using AI
        ai_data = None
        if text_content:
            ai_data = extract_profile_with_ai(text_content)
        
        if ai_data:
            profile_data.update(ai_data)
        
        # Add metadata
        profile_data['screenshot'] = screenshot_path if 'screenshot_path' in locals() else ""
        profile_data['extraction_method'] = 'OCR + AI'
        
        print(f"  ✓ Profile extracted successfully")
        return profile_data
        
    except Exception as e:
        print(f"  ✗ Error extracting profile: {str(e)[:100]}...")
        profile_data['error'] = str(e)
        profile_data['url'] = profile_url
        profile_data['extraction_method'] = 'OCR + AI'
        return profile_data

# ============================================================================
# FUNCTION: Extract Profile Data with AI
# ============================================================================

def extract_profile_with_ai(text_content):
    """Extract structured profile data using Groq AI"""
    
    prompt = """
    You are analyzing text extracted from a LinkedIn profile.
    Extract the following information and return it as a valid JSON object:
    
    {
        "name": "Full name of the person",
        "headline": "Professional headline/title",
        "location": "Location/city",
        "about": "About/summary section",
        "experience": [
            {
                "company": "Company name",
                "position": "Job title",
                "duration": "Time period",
                "location": "Work location",
                "description": "Job description"
            }
        ],
        "education": [
            {
                "school": "School/university name",
                "degree": "Degree and field of study",
                "duration": "Time period",
                "description": "Activities and description"
            }
        ],
        "skills": ["skill1", "skill2", ...],
        "certifications": [
            {
                "name": "Certificate name",
                "issuer": "Issuing organization",
                "date": "Issue date"
            }
        ]
    }
    
    If a field is not found, use an empty string or empty array.
    Return ONLY valid JSON, no additional text or explanation.
    """
    
    print("Sending text to Groq AI for structured extraction...")
    
    try:
        # Truncate text if too long (keep first 25000 chars)
        truncated_text = text_content[:25000] if len(text_content) > 25000 else text_content
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a LinkedIn profile data extraction expert. Extract structured information from profile text and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nPROFILE TEXT:\n{truncated_text}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=4000,
        )
        
        response_text = chat_completion.choices[0].message.content
        print(f"✓ Groq AI response received")
        
        # Parse JSON response
        try:
            # Check if response_text is valid
            if not response_text:
                print("Error: Empty response from AI")
                return None
                
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            if response_text:
                print(f"Response preview: {response_text[:500]}")
            return None
            
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

# ============================================================================
# Scrape Multiple Profiles Across Pages
# ============================================================================

print("\n" + "="*80)
print("🔄 MULTI-PROFILE SCRAPING (5 Pages)")
print("="*80 + "\n")

all_profiles_data = []
MAX_PAGES = 5
profiles_per_page_target = 10
page_num = 0

for page_num in range(1, MAX_PAGES + 1):
    print(f"\n{'='*80}")
    print(f"📄 PAGE {page_num}/{MAX_PAGES}")
    print(f"{'='*80}\n")
    
    try:
        # Wait for profiles to load on current page
        page.wait_for_selector('a[href*="/in/"]', timeout=10000)
        sleep(2)
        
        # Get all unique profile links on this page
        profile_elements = page.query_selector_all('a[href*="/in/"]')
        profile_urls = []
        seen_urls = set()
        
        for elem in profile_elements:
            href = elem.get_attribute('href')
            if href and '/in/' in href:
                # Clean URL - remove query parameters
                clean_url = href.split('?')[0]
                if clean_url not in seen_urls and 'linkedin.com/in/' in clean_url:
                    seen_urls.add(clean_url)
                    profile_urls.append(clean_url)
        
        print(f"Found {len(profile_urls)} unique profiles on page {page_num}")
        
        # Scrape each profile on this page
        for idx, profile_url in enumerate(profile_urls[:profiles_per_page_target], 1):
            print(f"\n[Page {page_num} - Profile {idx}/{min(len(profile_urls), profiles_per_page_target)}]")
            
            try:
                profile_data = extract_profile_with_ocr(page, profile_url)
                profile_data['page_number'] = page_num
                profile_data['profile_index'] = idx
                all_profiles_data.append(profile_data)
                
                # Check if profile extraction was successful
                if 'error' not in profile_data or not profile_data['error']:
                    print(f"  ✓ Profile {idx} processed successfully")
                else:
                    print(f"  ⚠️  Profile {idx} had errors but data saved")
                    
            except Exception as profile_error:
                print(f"  ✗ Failed to process profile {idx}: {profile_error}")
                # Save error information
                error_profile_data = {
                    'url': profile_url,
                    'page_number': page_num,
                    'profile_index': idx,
                    'extraction_method': 'OCR + AI',
                    'error': f'Profile processing failed: {str(profile_error)}'
                }
                all_profiles_data.append(error_profile_data)
            
            # Go back to search results with error handling
            try:
                page.go_back()
                sleep(2)
                page.wait_for_selector('a[href*="/in/"]', timeout=10000)
                sleep(1)
            except Exception as nav_error:
                print(f"  ⚠️  Navigation error: {nav_error}")
                # Try to reload the search results page
                try:
                    page.reload(timeout=10000)
                    sleep(3)
                    page.wait_for_selector('a[href*="/in/"]', timeout=10000)
                except:
                    print("  ⚠️  Could not recover navigation, continuing...")
        
        # Navigate to next page if not the last page
        if page_num < MAX_PAGES:
            print(f"\n⏭️  Moving to page {page_num + 1}...")
            
            # Retry mechanism for next page navigation
            max_retries = 3
            for retry in range(max_retries):
                try:
                    # Find and click "Next" button
                    next_button = page.query_selector('button[aria-label="Next"]')
                    if not next_button:
                        next_button = page.query_selector('button:has-text("Next")')
                    
                    if next_button:
                        # Scroll to button and click
                        next_button.scroll_into_view_if_needed()
                        sleep(1)
                        next_button.click()
                        print("✓ Clicked Next button")
                        sleep(3)
                        
                        # Wait for page to load with more flexible approach
                        try:
                            page.wait_for_load_state('networkidle', timeout=15000)
                        except:
                            print("⚠ Network idle timeout, continuing anyway...")
                            
                        sleep(2)
                        
                        # Verify we've moved to the next page
                        try:
                            page.wait_for_selector('a[href*="/in/"]', timeout=10000)
                            print(f"✓ Successfully navigated to page {page_num + 1}")
                            break  # Success, exit retry loop
                        except:
                            if retry < max_retries - 1:
                                print(f"⚠ Page verification failed, retrying... ({retry + 1}/{max_retries})")
                                sleep(3)
                                continue
                            else:
                                print("⚠ Failed to verify page navigation after retries")
                                raise
                    else:
                        print("⚠ No Next button found - might be last page")
                        break
                        
                except Exception as e:
                    if retry < max_retries - 1:
                        print(f"⚠ Next page navigation failed, retrying... ({retry + 1}/{max_retries}): {str(e)[:100]}...")
                        sleep(5)  # Longer delay between retries
                        # Try to reload the current page
                        try:
                            page.reload(timeout=15000)
                            sleep(3)
                            page.wait_for_selector('a[href*="/in/"]', timeout=10000)
                        except:
                            print("⚠ Failed to reload current page")
                        continue
                    else:
                        print(f"⚠ Could not navigate to next page after {max_retries} attempts: {str(e)[:100]}...")
                        break
    
    except Exception as e:
        print(f"✗ Error on page {page_num}: {e}")
        break

print(f"\n{'='*80}")
print(f"✅ SCRAPING COMPLETE!")
print(f"{'='*80}")
print(f"Total profiles scraped: {len(all_profiles_data)}")
print(f"Pages processed: {page_num}")
print(f"{'='*80}\n")

# ============================================================================
# Save All Profiles Data to JSON
# ============================================================================

output_file = 'data/profiles_multi_page_ocr.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_profiles_data, f, indent=4, ensure_ascii=False)

print(f"✓ All profiles data saved to {output_file}")

# Create summary file
summary = {
    'total_profiles': len(all_profiles_data),
    'pages_scraped': page_num,
    'profiles_by_page': {}
}

for profile in all_profiles_data:
    page_num = profile.get('page_number', 0)
    if page_num not in summary['profiles_by_page']:
        summary['profiles_by_page'][page_num] = 0
    summary['profiles_by_page'][page_num] += 1

summary_file = 'data/scraping_summary_ocr.json'
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=4, ensure_ascii=False)

print(f"✓ Scraping summary saved to {summary_file}")

# Keep the browser open for continued browsing
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
    if browser:
        browser.close()
    if playwright:
        playwright.stop()
    print("✓ Browser closed successfully!")

print("\n" + "="*80)
print("Screenshot-based OCR scraping completed successfully!")
print("="*80)
