import warnings
warnings.filterwarnings("ignore")

import os
import json
import base64
import random
import time
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from groq import Groq
from PIL import Image
from faker import Faker
from human_behavior import HumanBehavior, move_mouse_naturally
from advanced_captcha_solver import AdvancedCaptchaSolver
from human_behavior import HumanBehavior, move_mouse_naturally

# Load environment variables from .env file
load_dotenv(verbose=True)

# Set up environment variables
EMAIL = os.environ.get('EMAIL')
PASSWORD = os.environ.get('PASSWORD')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

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

# Initialize Faker for generating realistic user agents and data
fake = Faker()

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize advanced CAPTCHA solver
captcha_solver = AdvancedCaptchaSolver(groq_client)

# ============================================================================
# STEALTH UTILITIES - Human-like Behavior Simulation
# ============================================================================

# HumanBehavior class is imported from human_behavior module

class StealthConfig:
    """Anti-detection configuration"""
    
    # Realistic user agents (recent browsers)
    USER_AGENTS = [
        # Chrome on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        # Chrome on macOS
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        # Edge on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        # Firefox on Windows
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
    ]
    
    # Common screen resolutions
    SCREEN_SIZES = [
        {"width": 1920, "height": 1080},
        {"width": 1366, "height": 768},
        {"width": 1536, "height": 864},
        {"width": 1440, "height": 900},
        {"width": 2560, "height": 1440},
    ]
    
    @staticmethod
    def get_random_user_agent():
        """Get a random realistic user agent"""
        return random.choice(StealthConfig.USER_AGENTS)
    
    @staticmethod
    def get_random_screen_size():
        """Get a random common screen resolution"""
        return random.choice(StealthConfig.SCREEN_SIZES)
    
    @staticmethod
    def get_browser_context_options():
        """Get stealth browser context options"""
        screen_size = StealthConfig.get_random_screen_size()
        user_agent = StealthConfig.get_random_user_agent()
        
        return {
            'user_agent': user_agent,
            'viewport': screen_size,
            'screen': screen_size,
            'device_scale_factor': random.choice([1, 1.5, 2]),
            'is_mobile': False,
            'has_touch': False,
            'locale': random.choice(['en-US', 'en-GB']),
            'timezone_id': random.choice(['America/New_York', 'America/Los_Angeles', 'America/Chicago']),
            'permissions': [],
            'geolocation': None,
            'color_scheme': random.choice(['light', 'dark']),
            'extra_http_headers': {
                'Accept-Language': 'en-US,en;q=0.9',
                'Accept-Encoding': 'gzip, deflate, br',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'DNT': '1',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            }
        }

# ============================================================================
# Initialize Browser with Stealth Settings
# ============================================================================

print("\n" + "="*80)
print("Initializing stealth browser...")
print("="*80 + "\n")

playwright = sync_playwright().start()

# Get stealth configuration
stealth_options = StealthConfig.get_browser_context_options()
print(f"✓ User Agent: {stealth_options['user_agent'][:80]}...")
print(f"✓ Screen Size: {stealth_options['viewport']['width']}x{stealth_options['viewport']['height']}")
print(f"✓ Locale: {stealth_options['locale']}")
print(f"✓ Timezone: {stealth_options['timezone_id']}")

# Launch browser with stealth settings
browser = playwright.firefox.launch(
    headless=False
)

# Create context with stealth options
context = browser.new_context(**stealth_options)

# Add extra stealth scripts
context.add_init_script("""
    // Overwrite the navigator.webdriver property
    Object.defineProperty(navigator, 'webdriver', {
        get: () => undefined
    });
    
    // Overwrite the navigator.plugins property
    Object.defineProperty(navigator, 'plugins', {
        get: () => [1, 2, 3, 4, 5]
    });
    
    // Overwrite the navigator.languages property
    Object.defineProperty(navigator, 'languages', {
        get: () => ['en-US', 'en']
    });
    
    // Add chrome object
    window.chrome = {
        runtime: {}
    };
    
    // Overwrite permissions
    const originalQuery = window.navigator.permissions.query;
    window.navigator.permissions.query = (parameters) => (
        parameters.name === 'notifications' ?
        Promise.resolve({ state: Notification.permission }) :
        originalQuery(parameters)
    );
""")

page = context.new_page()

# Ensure page fits to device width and handles responsive design properly
page.add_init_script("""
    // Add viewport meta tag if not present
    if (!document.querySelector('meta[name="viewport"]')) {
        const meta = document.createElement('meta');
        meta.name = 'viewport';
        meta.content = 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no';
        document.head.appendChild(meta);
    }
""")

# Set additional page settings for proper rendering
page.set_extra_http_headers({
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': stealth_options['extra_http_headers']['Accept-Language'],
    'Cache-Control': 'max-age=0',
})

print("✓ Stealth browser initialized successfully")
print("✓ Page configured to fit device width")

# ============================================================================
# Navigate to LinkedIn Login with Human Behavior
# ============================================================================

print("\n" + "="*80)
print("Navigating to LinkedIn login page...")
print("="*80 + "\n")

page.goto('https://www.linkedin.com/login')
HumanBehavior.random_delay(2, 4)

# Wait for the login form to be ready
print("Waiting for login form to load...")
try:
    page.wait_for_selector('#username', timeout=15000)
    print("✓ Email field found")
except Exception as e:
    print(f"✗ Error: Email field not found - {e}")

try:
    page.wait_for_selector('#password', timeout=15000)
    print("✓ Password field found")
except Exception as e:
    print(f"✗ Error: Password field not found - {e}")

HumanBehavior.random_delay(1, 2)

# ============================================================================
# Login with Human-like Typing
# ============================================================================

print(f"\nEntering credentials with human-like typing speed...")

# Enter email with human-like behavior
try:
    email_field = page.query_selector('#username')
    if email_field:
        # Move mouse naturally to email field
        bbox = email_field.bounding_box()
        if bbox:
            target_x = bbox['x'] + bbox['width'] / 2
            target_y = bbox['y'] + bbox['height'] / 2
            move_mouse_naturally(page, target_x, target_y, duration=2.0)
        
        # Scroll to field if needed
        email_field.scroll_into_view_if_needed()
        HumanBehavior.random_delay(1, 2)
        
        # Click with human delay
        HumanBehavior.human_click(email_field, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
        
        # Clear field
        email_field.fill('')
        HumanBehavior.random_delay(1, 2)
        
        # Type like a human (120-300ms per keystroke)
        print(f"Typing email: {EMAIL}")
        HumanBehavior.human_type(email_field, EMAIL, min_delay=120, max_delay=300)
        print("✓ Email entered successfully")
        
        # Simulate reading/confirmation
        HumanBehavior.simulate_thinking((1.0, 2.0))
    else:
        print("✗ Error: Email field element not found")
except Exception as e:
    print(f"✗ Error entering email: {e}")

HumanBehavior.random_delay(1, 3)

# Enter password with human-like behavior
try:
    password_field = page.query_selector('#password')
    if password_field:
        # Move mouse naturally to password field
        bbox = password_field.bounding_box()
        if bbox:
            target_x = bbox['x'] + bbox['width'] / 2
            target_y = bbox['y'] + bbox['height'] / 2
            move_mouse_naturally(page, target_x, target_y, duration=2.0)
        
        # Scroll to field if needed
        password_field.scroll_into_view_if_needed()
        HumanBehavior.random_delay(1, 2)
        
        # Click with human delay
        HumanBehavior.human_click(password_field, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
        
        # Clear field
        password_field.fill('')
        HumanBehavior.random_delay(1, 2)
        
        # Type password (slightly faster typing for passwords is normal)
        print("Typing password...")
        HumanBehavior.human_type(password_field, PASSWORD, min_delay=80, max_delay=250)
        print("✓ Password entered successfully")
        
        # Simulate reading/confirmation
        HumanBehavior.simulate_thinking((1.0, 2.0))
    else:
        print("✗ Error: Password field element not found")
except Exception as e:
    print(f"✗ Error entering password: {e}")

HumanBehavior.random_delay(1, 2)

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
            
            # Scroll to button if needed
            sign_in_button.scroll_into_view_if_needed()
            HumanBehavior.random_delay(1, 2)
            
            # Hover over button briefly
            HumanBehavior.human_hover(sign_in_button, hover_duration=(0.5, 1.5))
            
            # Click with human-like delay
            HumanBehavior.human_click(sign_in_button, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
            print("✓ Sign-in button clicked successfully")
            
            # Simulate waiting for response
            HumanBehavior.simulate_thinking((2.0, 4.0))
    else:
        print("✗ Error: Sign-in button element not found")
except Exception as e:
    print(f"✗ Error clicking sign-in button: {e}")

# ============================================================================
# CAPTCHA Detection and Automatic Handling
# ============================================================================

print("\n" + "="*80)
print("Checking for CAPTCHA...")
print("="*80 + "\n")
HumanBehavior.random_delay(1, 2)

# Function to automatically handle reCAPTCHA checkbox with single attempt
def auto_solve_recaptcha_checkbox(page):
    """Automatically detect and click reCAPTCHA checkbox with human-like behavior (single attempt)"""
    try:
        print(f"  🔄 Looking for reCAPTCHA checkbox...")
        HumanBehavior.random_delay(1, 2)
        
        recaptcha_iframe = page.query_selector('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]')
        
        if recaptcha_iframe:
            print(f"  ✓ Found reCAPTCHA iframe")
            iframe_element = page.frame_locator('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]').first
            
            try:
                checkbox = iframe_element.locator('.recaptcha-checkbox-border, #recaptcha-anchor')
                if checkbox:
                    print(f"  🖱️  Clicking reCAPTCHA checkbox with human-like behavior...")
                    HumanBehavior.random_delay(1, 2)
                    
                    # Try multiple click methods
                    try:
                        checkbox.click(timeout=5000)
                        print(f"  ✅ Direct click attempted")
                    except Exception as click_error:
                        print(f"  ⚠️  Direct click failed: {click_error}")
                        
                        try:
                            checkbox.first.click(timeout=5000)
                            print(f"  ✅ First element click attempted")
                        except Exception as first_click_error:
                            print(f"  ⚠️  First element click failed: {first_click_error}")
                    
                    print(f"  ⏳ Waiting for verification...")
                    HumanBehavior.random_delay(4, 6)
                    
                    checked = iframe_element.locator('.recaptcha-checkbox-checked')
                    if checked.count() > 0:
                        print(f"  ✅ reCAPTCHA checkbox verified successfully!")
                        HumanBehavior.random_delay(1, 2)
                        return True
                    else:
                        print(f"  ⚠️  Checkbox clicked but not yet verified")
                        return False
            except Exception as e:
                print(f"  ⚠️  Failed: {e}")
                return False
        else:
            print(f"  ℹ️  No reCAPTCHA checkbox found")
            current_url = page.url.lower()
            if '/feed' in current_url or '/in/' in current_url:
                print(f"  ✅ Already on LinkedIn feed/profile - CAPTCHA may have auto-passed!")
                return True
            HumanBehavior.random_delay(1, 2)
            return False
            
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False

# Check for CAPTCHA indicators
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
        'div:has-text("Let\'s do a quick security check")',
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
        print(f"⚠ CAPTCHA DETECTED: Page title contains verification keywords: '{page.title()}'")
    
    if 'checkpoint' in page_url or 'challenge' in page_url:
        captcha_detected = True
        print(f"⚠ CAPTCHA DETECTED: URL contains challenge keywords: {page_url}")
    
    if '/login' in page_url and not '/feed' in page_url:
        HumanBehavior.random_delay(2, 3)
        if '/login' in page.url:
            print("⚠ Still on login page - possible CAPTCHA or verification needed")
            captcha_detected = True
        
except Exception as e:
    print(f"⚠ Warning: Error checking for CAPTCHA: {e}")

if captcha_detected:
    print("\n" + "="*80)
    print("🤖 CAPTCHA / SECURITY CHALLENGE DETECTED!")
    print("="*80)
    
    # Try to automatically solve reCAPTCHA checkbox
    checkbox_solved = captcha_solver.solve_recaptcha_checkbox(page)
    
    if checkbox_solved:
        print("\n✅ reCAPTCHA checkbox automatically solved!")
        print("Waiting for page to proceed...")
        HumanBehavior.random_delay(2, 4)
        
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
            complex_captcha = False
            
            # Verify we're past the challenge
            current_url = page.url
            if '/feed' in current_url or '/in/' in current_url:
                print("✓ Successfully passed security verification automatically!")
            else:
                print(f"⚠ Still on verification page, may need manual intervention")
                complex_captcha = True
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
            HumanBehavior.random_delay(5, 8)
            
            # Check if we're past the CAPTCHA
            current_url = page.url
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
    print("✓ No CAPTCHA detected - proceeding normally")

# Wait for login to complete
print("\nWaiting for login to complete...")
try:
    page.wait_for_url('**/feed/**', timeout=20000)
    print("✓ Login successful - feed page loaded")
except:
    print("Feed page not detected, waiting additional time...")
    HumanBehavior.random_delay(5, 8)
    try:
        page.wait_for_url('**/in/**', timeout=10000)
        print("✓ Login successful - profile page loaded")
    except:
        print("⚠ Warning: Could not verify successful login")

HumanBehavior.random_delay(2, 4)

# Perform some random actions (look natural)
print("Performing natural browsing actions...")
HumanBehavior.random_page_actions(page)

# ============================================================================
# Search for Profiles with Human Behavior
# ============================================================================

print("\n" + "="*80)
print("Starting search process...")
print("="*80 + "\n")

# Find and click the search bar with human behavior
print("Looking for search bar...")
try:
    page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
    print("✓ Search bar found")
    
    search_bar = page.query_selector('[placeholder*="Search"]')
    if search_bar:
        # Scroll to search bar if needed
        search_bar.scroll_into_view_if_needed()
        HumanBehavior.random_delay(1, 2)
        
        # Click the search bar
        search_bar.click()
        HumanBehavior.random_delay(1, 2)
        
        # Type search keyword with human speed
        search_keyword = "AI Engineer"
        print(f"Typing search keyword: {search_keyword}")
        HumanBehavior.human_type(search_bar, search_keyword, min_delay=100, max_delay=280)
        HumanBehavior.random_delay(1, 2)
        
        print("✓ Search keyword entered successfully")
    else:
        print("✗ Error: Search bar element not found")
except Exception as e:
    print(f"✗ Error finding or using search bar: {e}")

HumanBehavior.random_delay(1, 2)

# Press Enter to perform the search
print("Pressing Enter to search...")
try:
    page.press('[placeholder*="Search"]', 'Enter')
    print("✓ Search submitted")
except Exception as e:
    print(f"✗ Error pressing Enter: {e}")

# Wait for search results page to load
print("Waiting for search results page to load...")
HumanBehavior.random_delay(3, 5)

try:
    page.wait_for_url('**/search/results/**', timeout=15000)
    print("✓ Search results page loaded successfully")
except Exception as e:
    print(f"⚠ Warning: Could not verify search results page: {e}")
    HumanBehavior.random_delay(2, 3)

HumanBehavior.random_delay(1, 2)

# Random browsing behavior before filtering
print("Browsing results naturally...")
HumanBehavior.random_page_actions(page)

# Filter results by People
print("\nLooking for 'People' filter option...")
try:
    page.wait_for_selector('button[data-filter-type="currentCompany"], button:has-text("People")', timeout=10000)
    
    people_filters = page.query_selector_all('button')
    people_filter_found = False
    
    for button in people_filters:
        button_text = button.text_content()
        if button_text and 'People' in button_text.strip():
            print(f"✓ Found 'People' filter button")
            button.scroll_into_view_if_needed()
            HumanBehavior.random_delay(1, 2)
            button.click()
            people_filter_found = True
            HumanBehavior.random_delay(2, 3)
            break
    
    if not people_filter_found:
        print("⚠ Warning: Could not find 'People' filter button")
        
except Exception as e:
    print(f"✗ Error filtering by People: {e}")

print("Waiting for filtered results to load...")
HumanBehavior.random_delay(3, 5)

print("\n✓ Search and filter process completed!\n")

# ============================================================================
# Click on First Candidate Profile
# ============================================================================

print("\n" + "="*80)
print("Selecting first candidate...")
print("="*80 + "\n")

try:
    print("Waiting for candidate profiles to load...")
    page.wait_for_selector('a[href*="/in/"]', timeout=10000)
    
    profile_links = page.query_selector_all('a[href*="/in/"]')
    
    if profile_links:
        print(f"✓ Found {len(profile_links)} candidate profiles")
        
        # Scroll to first profile naturally
        first_profile = profile_links[0]
        first_profile.scroll_into_view_if_needed()
        HumanBehavior.random_delay(1, 2)
        
        # Get profile URL
        profile_url = first_profile.get_attribute('href')
        print(f"First candidate profile URL: {profile_url}")
        
        # Random mouse movement before clicking
        print("Hovering over profile...")
        first_profile.hover()
        HumanBehavior.random_delay(1, 2)
        
        print("Clicking on first candidate...")
        first_profile.click()
        HumanBehavior.random_delay(2, 3)
        
        print("✓ Profile clicked, waiting for page to load...")
        page.wait_for_load_state('networkidle', timeout=15000)
        HumanBehavior.random_delay(2, 4)
        
    else:
        print("✗ Error: No candidate profiles found")
        profile_url = None
        
except Exception as e:
    print(f"✗ Error selecting first candidate: {e}")
    profile_url = None

# Get the actual profile URL
url = page.url
print(f"Current profile URL: {url}")

# ============================================================================
# Human-like Scrolling to Load All Content
# ============================================================================

print("\n" + "="*80)
print("Reading profile with human-like scrolling...")
print("="*80 + "\n")

# Get the total page height
total_height = page.evaluate("document.body.scrollHeight")
print(f"Total page height: {total_height}px")

# Human-like scrolling pattern
viewport_height = stealth_options['viewport']['height']
current_position = 0

print("Scrolling down naturally...")
scroll_iterations = 0

while current_position < total_height - viewport_height:
    # Random scroll distance (humans don't scroll uniformly)
    scroll_distance = random.randint(300, 600)
    target_position = min(current_position + scroll_distance, total_height)
    
    # Scroll with human-like behavior
    HumanBehavior.human_scroll(page, target_position, viewport_height)
    current_position = page.evaluate("window.pageYOffset")
    
    # Random pause to "read" content
    read_time = random.uniform(1.5, 4.0)
    print(f"  Scrolled to {current_position}px, reading for {read_time:.1f}s...")
    time.sleep(read_time)
    
    # Update total height in case new content loaded
    total_height = page.evaluate("document.body.scrollHeight")
    
    scroll_iterations += 1
    
    # Occasionally scroll back up slightly (humans do this)
    if random.random() < 0.15:  # 15% chance
        backscroll = random.randint(50, 150)
        print(f"  Scrolling back {backscroll}px (re-reading)...")
        page.evaluate(f"window.scrollBy(0, -{backscroll})")
        time.sleep(random.uniform(0.5, 1.5))

print(f"✓ Completed {scroll_iterations} scroll iterations")

# Scroll back to top naturally
print("\nScrolling back to top...")
HumanBehavior.human_scroll(page, 0, viewport_height)
HumanBehavior.random_delay(1, 2)

# ============================================================================
# Take Full Page Screenshot
# ============================================================================

print("\n" + "="*80)
print("Taking full page screenshot...")
print("="*80 + "\n")

os.makedirs('data/screenshots', exist_ok=True)

screenshot_path = 'data/screenshots/profile_fullpage_stealth.png'

# Ensure content is rendered properly and fits device width before screenshot
page.evaluate("""
    () => {
        // Force layout recalculation to fit device width
        document.body.style.width = '100%';
        document.documentElement.style.width = '100%';
        
        // Remove any horizontal overflow
        document.body.style.overflowX = 'hidden';
        document.documentElement.style.overflowX = 'hidden';
        
        // Trigger reflow to apply changes
        void document.body.offsetHeight;
    }
""")

HumanBehavior.random_delay(1, 2)

page.screenshot(path=screenshot_path, full_page=True)
print(f"✓ Full page screenshot saved: {screenshot_path}")
print(f"✓ Screenshot fitted to device width: {stealth_options['viewport']['width']}px")

img = Image.open(screenshot_path)
print(f"✓ Screenshot dimensions: {img.size[0]}x{img.size[1]} pixels")

# ============================================================================
# Extract Text Content
# ============================================================================

print("\n" + "="*80)
print("Extracting visible text content...")
print("="*80 + "\n")

text_content = page.evaluate("""
() => {
    const mainSection = document.querySelector('main');
    if (!mainSection) return '';
    
    const scripts = mainSection.querySelectorAll('script, style');
    scripts.forEach(el => el.remove());
    
    return mainSection.innerText;
}
""")

print(f"✓ Extracted {len(text_content)} characters of text")

text_file_path = 'data/screenshots/profile_text_stealth.txt'
with open(text_file_path, 'w', encoding='utf-8') as f:
    f.write(text_content)
print(f"✓ Text content saved: {text_file_path}")

# ============================================================================
# Extract Profile Data Using AI
# ============================================================================

def extract_profile_with_ai(text_content):
    """Extract structured profile data using Groq AI"""
    
    prompt = """
    Extract LinkedIn profile information from this text and return as valid JSON:
    
    {
        "name": "Full name",
        "headline": "Professional headline",
        "location": "City, State/Country",
        "about": "About section summary",
        "experience": [
            {
                "company": "Company name",
                "position": "Job title",
                "duration": "Start - End date",
                "location": "Work location",
                "description": "Job description"
            }
        ],
        "education": [
            {
                "school": "School name",
                "degree": "Degree and field",
                "duration": "Years attended",
                "description": "Activities/honors"
            }
        ],
        "skills": ["skill1", "skill2"],
        "certifications": [
            {
                "name": "Cert name",
                "issuer": "Organization",
                "date": "Issue date"
            }
        ]
    }
    
    Return ONLY valid JSON, no explanation.
    """
    
    print("Sending data to Groq AI for extraction...")
    
    try:
        truncated_text = text_content[:25000] if len(text_content) > 25000 else text_content
        
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a LinkedIn profile data extraction expert. Return only valid JSON."
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
        print(f"✓ AI response received")
        
        # Parse JSON
        if response_text:
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            return data
        return None
            
    except Exception as e:
        print(f"✗ Error calling Groq API: {e}")
        return None

print("\n" + "="*80)
print("Extracting structured data with AI...")
print("="*80 + "\n")

profile_data = extract_profile_with_ai(text_content)

if profile_data:
    profile_data['url'] = url
    profile_data['screenshot'] = screenshot_path
    profile_data['extraction_method'] = 'Stealth OCR + AI'
    profile_data['user_agent'] = stealth_options['user_agent']
    
    print(f"\n✓ Profile data extracted successfully!")
    print(f"  - Name: {profile_data.get('name', 'N/A')}")
    print(f"  - Location: {profile_data.get('location', 'N/A')}")
    print(f"  - Experience entries: {len(profile_data.get('experience', []))}")
    print(f"  - Education entries: {len(profile_data.get('education', []))}")
    print(f"  - Skills: {len(profile_data.get('skills', []))}")
else:
    print("\n✗ Failed to extract profile data")
    profile_data = {
        'url': url,
        'screenshot': screenshot_path,
        'extraction_method': 'Stealth OCR + AI',
        'error': 'Extraction failed'
    }

# ============================================================================
# FUNCTION: Extract Profile Data with Stealth
# ============================================================================

def extract_profile_with_stealth(page, profile_url):
    """Extract profile data using stealth approach"""
    
    profile_data = {}
    
    try:
        # Navigate to profile
        print(f"  Navigating to profile: {profile_url}")
        page.goto(profile_url)
        HumanBehavior.random_delay(2, 4)
        page.wait_for_load_state('networkidle', timeout=15000)
        HumanBehavior.random_delay(2, 4)
        
        url = page.url
        profile_data['url'] = url
        
        # Human-like scrolling to load all content
        print("  Scrolling to load all content...")
        total_height = page.evaluate("document.body.scrollHeight")
        viewport_height = stealth_options['viewport']['height']
        current_position = 0
        
        print("  Scrolling down naturally...")
        scroll_iterations = 0
        
        while current_position < total_height - viewport_height:
            # Random scroll distance
            scroll_distance = random.randint(300, 600)
            target_position = min(current_position + scroll_distance, total_height)
            
            # Scroll with human-like behavior
            HumanBehavior.human_scroll(page, target_position, viewport_height)
            current_position = page.evaluate("window.pageYOffset")
            
            # Random pause to "read" content
            read_time = random.uniform(1.5, 4.0)
            print(f"    Scrolled to {current_position}px, reading for {read_time:.1f}s...")
            time.sleep(read_time)
            
            # Update total height
            total_height = page.evaluate("document.body.scrollHeight")
            
            scroll_iterations += 1
            
            # Occasionally scroll back up slightly
            if random.random() < 0.15:  # 15% chance
                backscroll = random.randint(50, 150)
                print(f"    Scrolling back {backscroll}px (re-reading)...")
                page.evaluate(f"window.scrollBy(0, -{backscroll})")
                time.sleep(random.uniform(0.5, 1.5))
        
        # Scroll back to top naturally
        print("  Scrolling back to top...")
        HumanBehavior.human_scroll(page, 0, viewport_height)
        HumanBehavior.random_delay(1, 2)
        
        # Take screenshot
        screenshot_filename = f'profile_screenshot_stealth_{hash(profile_url) % 10000}.png'
        screenshot_path = f'data/screenshots/{screenshot_filename}'
        os.makedirs('data/screenshots', exist_ok=True)
        page.screenshot(path=screenshot_path, full_page=True)
        
        # Extract text content
        text_content = page.evaluate("""
        () => {
            const mainSection = document.querySelector('main');
            if (!mainSection) return '';
            
            const scripts = mainSection.querySelectorAll('script, style');
            scripts.forEach(el => el.remove());
            
            return mainSection.innerText;
        }
        """)
        
        # Save text content
        text_file_path = f'data/screenshots/profile_text_stealth_{hash(profile_url) % 10000}.txt'
        with open(text_file_path, 'w', encoding='utf-8') as f:
            f.write(text_content)
        
        # Extract profile data using AI
        ai_data = extract_profile_with_ai(text_content)
        
        if ai_data:
            profile_data.update(ai_data)
        
        # Add metadata
        profile_data['screenshot'] = screenshot_path
        profile_data['extraction_method'] = 'Stealth OCR + AI'
        profile_data['user_agent'] = stealth_options['user_agent']
        
        print(f"  ✓ Profile extracted successfully")
        return profile_data
        
    except Exception as e:
        print(f"  ✗ Error extracting profile: {e}")
        profile_data['error'] = str(e)
        return profile_data

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
        HumanBehavior.random_delay(2, 4)
        
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
                profile_data = extract_profile_with_stealth(page, profile_url)
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
                    'extraction_method': 'Stealth OCR + AI',
                    'error': f'Profile processing failed: {str(profile_error)}'
                }
                all_profiles_data.append(error_profile_data)
            
            # Go back to search results with error handling
            try:
                page.go_back()
                HumanBehavior.random_delay(2, 4)
                page.wait_for_selector('a[href*="/in/"]', timeout=10000)
                HumanBehavior.random_delay(1, 2)
            except Exception as nav_error:
                print(f"  ⚠️  Navigation error: {nav_error}")
                # Try to reload the search results page
                try:
                    page.reload(timeout=10000)
                    HumanBehavior.random_delay(3, 5)
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
                        next_button.scroll_into_view_if_needed()
                        HumanBehavior.random_delay(1, 2)
                        next_button.click()
                        print("✓ Clicked Next button")
                        HumanBehavior.random_delay(3, 5)
                        
                        # Wait for page to load with more flexible approach
                        try:
                            page.wait_for_load_state('networkidle', timeout=15000)
                        except:
                            print("⚠ Network idle timeout, continuing anyway...")
                            
                        HumanBehavior.random_delay(2, 4)
                        
                        # Verify we've moved to the next page
                        try:
                            page.wait_for_selector('a[href*="/in/"]', timeout=10000)
                            print(f"✓ Successfully navigated to page {page_num + 1}")
                            break  # Success, exit retry loop
                        except:
                            if retry < max_retries - 1:
                                print(f"⚠ Page verification failed, retrying... ({retry + 1}/{max_retries})")
                                HumanBehavior.random_delay(3, 5)
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
                        HumanBehavior.random_delay(5, 8)  # Longer delay between retries
                        # Try to reload the current page
                        try:
                            page.reload(timeout=15000)
                            HumanBehavior.random_delay(3, 5)
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

output_file = 'data/profiles_multi_page_stealth.json'
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

summary_file = 'data/scraping_summary_stealth.json'
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=4, ensure_ascii=False)

print(f"✓ Scraping summary saved to {summary_file}")

# ============================================================================
# Cleanup - Human-like Exit
# ============================================================================

print("\n" + "="*80)
print("Cleaning up...")
print("="*80 + "\n")

# Random browsing before exit (look natural)
print("Performing natural exit behavior...")
HumanBehavior.random_page_actions(page)
HumanBehavior.random_delay(1, 2)

# Close browser
context.close()
# browser.close()
# playwright.stop()

print("\n" + "="*80)
print("🤖 BROWSER KEPT OPEN FOR CONTINUED BROWSING")
print("="*80)
print("You can continue using the browser manually.")
print("To close the browser, press Ctrl+C in this console.")
print("="*80)

# Keep the script running to maintain browser open
try:
    while True:
        time.sleep(10)  # Keep alive
except KeyboardInterrupt:
    print("\nReceived interrupt signal, closing browser...")
    browser.close()
    playwright.stop()
    print("✓ Browser closed successfully!")

print("\n" + "="*80)
print("✓ STEALTH SCRAPING COMPLETED SUCCESSFULLY!")
print("="*80)
print(f"\n📊 Results:")
print(f"  📁 Data: {output_file}")
print(f"  📊 Summary: {summary_file}")
print("\n" + "="*80)
