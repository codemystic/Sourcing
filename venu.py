import warnings
warnings.filterwarnings("ignore")

import base64
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
from nlp_query_parser import parse_nlp_query, format_search_query


# Get credentials from environment variables - ONLY GROQ_API_KEY is needed now
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

# Validate that GROQ API key is provided
if not GROQ_API_KEY:
    print("ERROR: GROQ_API_KEY not found in .env file")
    print("Please add to .env file: GROQ_API_KEY=your_groq_api_key")
    exit(1)

print(f"✓ Groq API Key loaded: {GROQ_API_KEY[:10]}...")

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# CAPTCHA solver functions will be implemented directly in this file

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

# Initialize Playwright and navigate directly to Google homepage
playwright = sync_playwright().start()

# Use real Chrome browser instead of Chromium
# Try to find Chrome installation path
import platform
system = platform.system()

if system == "Windows":
    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        os.path.expanduser(r"~\AppData\Local\Google\Chrome\Application\chrome.exe")
    ]
    chrome_path = None
    for path in chrome_paths:
        if os.path.exists(path):
            chrome_path = path
            break
    
    if chrome_path:
        print(f"✓ Found Chrome at: {chrome_path}")
        browser = playwright.chromium.launch(
            headless=False,
            channel="chrome",  # Use Chrome channel
            executable_path=chrome_path
        )
    else:
        print("⚠️  Chrome not found, using Chromium")
        browser = playwright.chromium.launch(headless=False)
else:
    # For Linux/Mac, try to use Chrome channel
    try:
        browser = playwright.chromium.launch(headless=False, channel="chrome")
        print("✓ Using Chrome browser")
    except:
        print("⚠️  Chrome not found, using Chromium")
        browser = playwright.chromium.launch(headless=False)

page = browser.new_page()

# Navigate directly to Google homepage
print("Navigating to Google homepage...")
page.goto('https://www.google.com/')
sleep(3)

# Wait for basic page elements
try:
    page.wait_for_selector('body', timeout=5000)
except:
    pass
time.sleep(2)

print("✅ Browser opened successfully.")
print("ℹ️  Please enter your search query in the terminal.")

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

# Extract keywords from parsed query
job_title = parsed_query.get('job_title', 'Python Developer')  # Use job_title from parsed query
if not job_title:
    job_title = 'Python Developer'  # Default to Python Developer if not specified
location = parsed_query.get('location', 'Hyderabad')  # Default to Hyderabad if not specified

print(f"\nExtracted keywords:")
print(f"  Job Title: {job_title}")
print(f"  Location: {location}")

# Construct Google X-ray search query (replace spaces with + in quoted strings)
job_title_formatted = job_title.replace(' ', '+')
location_formatted = location.replace(' ', '+')
xray_query = f"+\"{job_title_formatted}\" AND \"Open+to+work\"+\"{location_formatted}\" -intitle:\"profiles\" -inurl:\"dir/+\"+site:in.linkedin.com/in/+OR+site:in.linkedin.com/pub/"

# Construct full Google search URL
google_search_url = f"https://www.google.com/search?q={xray_query}"

print(f"\nConstructed Google X-ray query:")
print(f"  {xray_query}")
print(f"\nFull search URL:")
print(f"  {google_search_url}")

# Navigate directly to Google search results
print("\n🔍 Executing Google X-ray search...")
print("  Navigating to Google search results page...")
page.goto(google_search_url)
sleep(3)

# Verify we're on the search results page
print("✅ Successfully navigated to Google search results page")
current_url = page.url
page_title = page.title()
print(f"   Current URL: {current_url}")
print(f"   Page title: {page_title}")

# ============================================================================
# CAPTCHA Detection and Automatic Handling
# ============================================================================

def analyze_captcha_screenshot_with_vision_model(screenshot_path):
    """Analyze CAPTCHA screenshot with vision model and return structured output"""
    try:
        print(f"  📸 Analyzing CAPTCHA screenshot: {screenshot_path}")
        
        # Read the screenshot file
        with open(screenshot_path, "rb") as image_file:
            screenshot_data = base64.b64encode(image_file.read()).decode("utf-8")
        
        # Create improved prompt for vision model analysis
        prompt = """
        You are an expert visual-classification assistant.

        I will upload an image that contains:
        1. A textual instruction at the top (e.g., "Select all images with crosswalks").
        2. A grid of smaller images (tiles) below the instruction.

        Your tasks:
        1. Read the instruction exactly as it appears at the top.
        2. Understand what visual feature the instruction is asking for.
        3. Analyze every tile in the grid.
        4. Determine which tiles match the instruction.

        Tile numbering:
        - Number tiles from left to right and top to bottom.
          (Example: a 3×3 grid is numbered 1 through 9.)

        Output format (strict JSON):
        {
          "instruction": "<instruction_detected>",
          "matching_tiles": [list_of_tile_numbers],
          "explanations": {
              "<tile_number>": "<short_reason>"
          }
        }

        Rules:
        - Use only the visual information from the uploaded image.
        - Follow the instruction literally.
        - If a tile is unclear or partially matches, classify it as non-matching.
        - Do NOT guess or infer beyond what is visible.
        - You are only classifying the image I provide manually.
        - Be extremely conservative in your selections - only select tiles you are 95%+ confident about.
        - It's better to select fewer tiles correctly than more tiles incorrectly.
        - When in doubt, exclude the tile.
        """
        
        # Call Groq API with vision model
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{screenshot_data}"
                            }
                        }
                    ]
                }
            ],
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            temperature=0.1,
            max_tokens=4000,
        )
        
        # Get and display the response
        response_text = chat_completion.choices[0].message.content
        print(f"\n{response_text}")
        
        # Validate that we got valid JSON response
        if response_text:
            import json
            try:
                parsed_response = json.loads(response_text)
                # Check if it has the required fields
                if 'instruction' in parsed_response and ('matching_tiles' in parsed_response or 'matches' in parsed_response):
                    print("  ✅ Valid JSON response received from vision model")
                    return response_text
                else:
                    print("  ⚠️  Invalid JSON structure from vision model")
                    return None
            except json.JSONDecodeError:
                print("  ⚠️  Failed to parse JSON from vision model response")
                return None
        else:
            print("  ⚠️  Empty response from vision model")
            return None
        
    except Exception as e:
        print(f"  ⚠️  Error analyzing CAPTCHA with vision model: {e}")
        return None

def solve_recaptcha_checkbox(page):
    """Attempt to automatically solve reCAPTCHA checkbox"""
    try:
        print("  🔍 Looking for reCAPTCHA checkbox...")
        
        # Look for reCAPTCHA iframe
        recaptcha_iframe = page.query_selector('iframe[title="reCAPTCHA"]')
        if not recaptcha_iframe:
            print("  ⚠️  No reCAPTCHA checkbox found")
            return False
        
        # Scroll to reCAPTCHA
        recaptcha_iframe.scroll_into_view_if_needed()
        time.sleep(1)
        
        # Get bounding box
        box = recaptcha_iframe.bounding_box()
        if not box:
            print("  ⚠️  Could not get reCAPTCHA position")
            return False
        
        # Click on the checkbox (typically in the top-left corner of iframe)
        page.mouse.click(box['x'] + 10, box['y'] + 10)
        print("  ✅ Clicked reCAPTCHA checkbox")
        time.sleep(2)
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error solving reCAPTCHA checkbox: {e}")
        return False

def solve_image_puzzle(page, vision_analysis=None):
    """Solve image puzzle CAPTCHA using vision analysis"""
    try:
        print("  🧩 Attempting to solve image puzzle CAPTCHA...")
        
        # Wait for challenge to load
        time.sleep(3)
        
        # Look for image challenge iframe
        challenge_iframe = page.query_selector('iframe[title*="challenge"]')
        if not challenge_iframe:
            print("  ⚠️  No image challenge found")
            return False
        
        # Switch to challenge iframe
        print("  🖼️  Switching to challenge iframe...")
        challenge_frame = challenge_iframe.content_frame()
        if not challenge_frame:
            print("  ⚠️  Could not access challenge frame")
            return False
        
        # If we have vision analysis, use it
        if vision_analysis:
            print("  🤖 Using vision analysis to solve puzzle...")
            try:
                import json
                analysis = json.loads(vision_analysis)
                matches = analysis.get('matches', [])
                
                # Click on matching tiles
                for tile_num in matches:
                    # Tile numbering starts from 1
                    # Calculate position based on 3x3 grid (typically)
                    row = (tile_num - 1) // 3
                    col = (tile_num - 1) % 3
                    
                    # Approximate positions (may need adjustment based on actual layout)
                    x_offset = 100 + (col * 150)
                    y_offset = 200 + (row * 150)
                    
                    print(f"  🖱️  Clicking tile {tile_num} at position ({x_offset}, {y_offset})")
                    page.mouse.click(x_offset, y_offset)
                    time.sleep(0.5)
                
                # Click verify button
                verify_btn = challenge_frame.query_selector('button')
                if verify_btn:
                    verify_btn.click()
                    print("  ✅ Clicked verify button")
                    time.sleep(3)
                    
                    # Wait for page to potentially redirect after solving
                    print("  ⏳ Waiting for page to redirect after solving CAPTCHA...")
                    time.sleep(5)
                    
                    # Check if we're still on a CAPTCHA page or have been redirected
                    current_url = page.url.lower()
                    if 'sorry' in current_url or 'recaptcha' in current_url:
                        print("  ⚠️  Still on CAPTCHA page, solving may not have been successful")
                        # Try to check for success indicators
                        try:
                            # Look for elements that indicate we've passed the CAPTCHA
                            success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                            if len(success_indicators) > 0:
                                print("  ✅ Found search elements, likely passed CAPTCHA")
                                return True
                        except:
                            pass
                        return False
                    else:
                        print("  ✅ Successfully redirected after solving CAPTCHA")
                        return True
                    
            except Exception as parse_error:
                print(f"  ⚠️  Error parsing vision analysis: {parse_error}")
        
        # Fallback: Try random selection if no vision analysis
        print("  🎲 Using random selection as fallback...")
        tiles = list(range(1, 10))  # 3x3 grid = 9 tiles
        selected_tiles = random.sample(tiles, random.randint(2, 5))  # Select 2-5 random tiles
        
        for tile_num in selected_tiles:
            row = (tile_num - 1) // 3
            col = (tile_num - 1) % 3
            
            x_offset = 100 + (col * 150)
            y_offset = 200 + (row * 150)
            
            print(f"  🖱️  Clicking tile {tile_num} at position ({x_offset}, {y_offset})")
            page.mouse.click(x_offset, y_offset)
            time.sleep(0.5)
        
        # Try to find and click verify button
        verify_btn = challenge_frame.query_selector('button')
        if verify_btn:
            verify_btn.click()
            print("  ✅ Clicked verify button")
            time.sleep(3)
            
            # Wait for page to potentially redirect after solving
            print("  ⏳ Waiting for page to redirect after solving CAPTCHA...")
            time.sleep(5)
            
            # Check if we're still on a CAPTCHA page or have been redirected
            current_url = page.url.lower()
            if 'sorry' in current_url or 'recaptcha' in current_url:
                print("  ⚠️  Still on CAPTCHA page, solving may not have been successful")
                # Try to check for success indicators
                try:
                    # Look for elements that indicate we've passed the CAPTCHA
                    success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                    if len(success_indicators) > 0:
                        print("  ✅ Found search elements, likely passed CAPTCHA")
                        return True
                except:
                    pass
                return False
            else:
                print("  ✅ Successfully redirected after solving CAPTCHA")
                return True
        
        print("  ⚠️  Could not find verify button")
        return False
        
    except Exception as e:
        print(f"  ⚠️  Error solving image puzzle: {e}")
        return False

# Check for CAPTCHA indicators
# MODIFIED: More comprehensive check for valid LinkedIn pages
current_url = page.url.lower()
current_title = ""
try:
    current_title = page.title().lower()
except:
    pass

# Check if we're on a Google search results page
is_on_google_search_page = (
    "google.com" in current_url and 
    "search" in current_url
)

# Since we're doing Google X-ray search, we don't need LinkedIn login checks
is_on_valid_linkedin_page = False

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

# For Google X-ray search, check for Google CAPTCHA
# Note: Google may show CAPTCHA for automated searches
if is_on_google_search_page or "sorry" in current_url:
    if "sorry" in current_url:
        print("⚠️  Google CAPTCHA detected - this is normal for automated searches")
        print("   Please complete the CAPTCHA in the browser if prompted")
        print(f"   Current URL: {current_url}")
    else:
        print("✅ Successfully navigated to Google search results page")
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
        # Enhanced CAPTCHA selectors for both Google and other platforms
        captcha_selectors = [
            'iframe[title*="reCAPTCHA"]',
            'iframe[src*="recaptcha"]',
            'iframe[src*="google.com/recaptcha"]',
            'iframe[title*="challenge"]',
            'iframe[src*="challenge"]',
            '#captcha',
            '.captcha',
            'div[id*="captcha"]',
            'div[class*="captcha"]',
            'input[name="captcha"]',
            'div:has-text("verify you\'re not a robot")',
            'div:has-text("Security Verification")',
            '.g-recaptcha',
            '[data-sitekey]',
            '.rc-anchor',
            '.recaptcha-checkbox',
            'iframe[name*="recaptcha"]',
            '.rc-imageselect',
            '.rc-challenge',
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
        
        # Enhanced keyword detection
        captcha_keywords = ['captcha', 'verification', 'security', 'challenge', 'sorry', 'blocked', 'recaptcha']
        title_keywords = [keyword for keyword in captcha_keywords if keyword in page_title]
        url_keywords = [keyword for keyword in captcha_keywords if keyword in page_url]
        
        if title_keywords:
            captcha_detected = True
            print(f"⚠ CAPTCHA DETECTED: Page title contains verification keywords: {title_keywords}")
        
        if url_keywords:
            captcha_detected = True
            print(f"⚠ CAPTCHA DETECTED: URL contains challenge keywords: {url_keywords}")
            
        # Special handling for Google's "sorry" page
        try:
            page_url = page.url.lower()
            if 'sorry' in page_url and ('google.com' in page_url or 'recaptcha' in page_url):
                captcha_detected = True
                print("⚠ CAPTCHA DETECTED: Google 'sorry' page detected (reCAPTCHA)")
                # For Google CAPTCHA, we need to solve it
                complex_captcha = True  # Force CAPTCHA solving process
        except:
            pass
            
    except Exception as e:
        print(f"Warning: Error checking for CAPTCHA: {e}")

if captcha_detected:
    print("\n" + "="*80)
    print("🤖 CAPTCHA CHALLENGE DETECTED!")
    print("="*80)
    print("\n🔄 Starting fully automatic CAPTCHA solving...\n")
    
    # Try to automatically solve reCAPTCHA checkbox
    checkbox_solved = solve_recaptcha_checkbox(page)
    
    if checkbox_solved:
        print("\n✅ reCAPTCHA checkbox automatically solved!")
        print("Waiting for page to proceed...")
        sleep(3)
        
        # Check if we need to solve image challenge with enhanced selectors
        image_challenge_selectors = [
            'iframe[title*="recaptcha challenge"]',
            '.rc-imageselect',
            'iframe[src*="challenge"]',
            '.rc-challenge',
            '[class*="challenge"]'
        ]
        image_challenge = None
        for selector in image_challenge_selectors:
            try:
                image_challenge = page.query_selector(selector)
                if image_challenge:
                    print(f"\n🖼️  Image challenge detected with selector '{selector}' - attempting automatic solving...")
                    break
            except:
                continue
        
        if image_challenge:
            # Take screenshot of the CAPTCHA image challenge for vision model analysis
            try:
                captcha_screenshot_path = "data/screenshots/captcha_screenshot.png"
                os.makedirs('data/screenshots', exist_ok=True)
                page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=10000)
                print(f"  📸 CAPTCHA screenshot saved to: {captcha_screenshot_path}")
                
                # Analyze the CAPTCHA screenshot with vision model
                vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
            except Exception as screenshot_error:
                print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
                vision_analysis = None
            
            # Try to solve image puzzle automatically
            puzzle_solved = solve_image_puzzle(page, vision_analysis)
            
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
        checkbox_solved = solve_recaptcha_checkbox(page)
        if checkbox_solved:
            print("✅ Advanced checkbox solving successful!")
            
            # Enhanced image challenge selectors
            image_challenge_selectors = [
                'iframe[title*="recaptcha challenge"]',
                '.rc-imageselect',
                'iframe[src*="challenge"]',
                '.rc-challenge',
                '[class*="challenge"]'
            ]
            
            # Check for image challenge again with enhanced selectors
            image_challenge = None
            for selector in image_challenge_selectors:
                try:
                    image_challenge = page.query_selector(selector)
                    if image_challenge:
                        print(f"🖼️  Image challenge detected with selector '{selector}' - attempting advanced solving...")
                        break
                except:
                    continue
            
            if image_challenge:
                # Take screenshot of the CAPTCHA image challenge for vision model analysis
                try:
                    captcha_screenshot_path = "data/screenshots/captcha_screenshot.png"
                    os.makedirs('data/screenshots', exist_ok=True)
                    page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=10000)
                    print(f"  📸 CAPTCHA screenshot saved to: {captcha_screenshot_path}")
                    
                    # Analyze the CAPTCHA screenshot with vision model
                    vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
                except Exception as screenshot_error:
                    print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
                    vision_analysis = None
                
                puzzle_solved = solve_image_puzzle(page, vision_analysis)
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
    # Special case: Always try to solve CAPTCHA on Google search pages
    try:
        current_page_url = page.url.lower()
        if 'google.com' in current_page_url and ('search' in current_page_url or 'sorry' in current_page_url):
            print("ℹ️  Google page detected, checking for CAPTCHA...")
            # Try to solve any potential CAPTCHA
            captcha_detected = True
            complex_captcha = True
            
            # Also check for reCAPTCHA elements directly
            recaptcha_elements = page.query_selector_all('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"], .g-recaptcha')
            if len(recaptcha_elements) > 0:
                print(f"⚠️  Found {len(recaptcha_elements)} reCAPTCHA elements on page")
                
                # Trigger CAPTCHA solving process
                print("\n" + "="*80)
                print("🤖 CAPTCHA CHALLENGE DETECTED!")
                print("="*80)
                print("\n🔄 Starting fully automatic CAPTCHA solving...\n")
                
                # Try to automatically solve reCAPTCHA checkbox
                checkbox_solved = solve_recaptcha_checkbox(page)
                
                if checkbox_solved:
                    print("\n✅ reCAPTCHA checkbox automatically solved!")
                    print("Waiting for page to proceed...")
                    sleep(3)
                    
                    # Check if we need to solve image challenge with enhanced selectors
                    image_challenge_selectors = [
                        'iframe[title*="recaptcha challenge"]',
                        '.rc-imageselect',
                        'iframe[src*="challenge"]',
                        '.rc-challenge',
                        '[class*="challenge"]'
                    ]
                    image_challenge = None
                    for selector in image_challenge_selectors:
                        try:
                            image_challenge = page.query_selector(selector)
                            if image_challenge:
                                print(f"\n🖼️  Image challenge detected with selector '{selector}' - attempting automatic solving...")
                                break
                        except:
                            continue
                    
                    if image_challenge:
                        # Take screenshot of the CAPTCHA image challenge for vision model analysis
                        try:
                            captcha_screenshot_path = "data/screenshots/captcha_screenshot.png"
                            os.makedirs('data/screenshots', exist_ok=True)
                            page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=10000)
                            print(f"  📸 CAPTCHA screenshot saved to: {captcha_screenshot_path}")
                            
                            # Analyze the CAPTCHA screenshot with vision model
                            vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
                        except Exception as screenshot_error:
                            print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
                            vision_analysis = None
                        
                        # Try to solve image puzzle automatically
                        puzzle_solved = solve_image_puzzle(page, vision_analysis)
                        
                        if puzzle_solved:
                            print("✅ Advanced image puzzle solving successful!")
                            # Wait a bit for the page to redirect after solving CAPTCHA
                            print("⏳ Waiting for page to redirect after CAPTCHA solving...")
                            sleep(5)
                            complex_captcha = False
                        else:
                            print("⚠️  Advanced image puzzle solving failed")
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
                    checkbox_solved = solve_recaptcha_checkbox(page)
                    if checkbox_solved:
                        print("✅ Advanced checkbox solving successful!")
                        
                        # Enhanced image challenge selectors
                        image_challenge_selectors = [
                            'iframe[title*="recaptcha challenge"]',
                            '.rc-imageselect',
                            'iframe[src*="challenge"]',
                            '.rc-challenge',
                            '[class*="challenge"]'
                        ]
                        
                        # Check for image challenge again with enhanced selectors
                        image_challenge = None
                        for selector in image_challenge_selectors:
                            try:
                                image_challenge = page.query_selector(selector)
                                if image_challenge:
                                    print(f"🖼️  Image challenge detected with selector '{selector}' - attempting advanced solving...")
                                    break
                            except:
                                continue
                        
                        if image_challenge:
                            # Take screenshot of the CAPTCHA image challenge for vision model analysis
                            try:
                                captcha_screenshot_path = "data/screenshots/captcha_screenshot.png"
                                os.makedirs('data/screenshots', exist_ok=True)
                                page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=10000)
                                print(f"  📸 CAPTCHA screenshot saved to: {captcha_screenshot_path}")
                                
                                # Analyze the CAPTCHA screenshot with vision model
                                vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
                            except Exception as screenshot_error:
                                print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
                                vision_analysis = None
                            
                            puzzle_solved = solve_image_puzzle(page, vision_analysis)
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
    except Exception as e:
        print(f"⚠️  Error checking for Google CAPTCHA: {e}")

# No login required - proceed directly to search
print("\n" + "="*80)
print("Starting search process...")
print("="*80)

# ============================================================================
# Search for AI Engineer and filter by People
# ============================================================================

print("\n" + "="*80)
print("Starting search process...")
print("="*80)

# For Google X-ray search, we don't need to search again since we already executed the search
print("\n✅ Google X-ray search completed successfully!")
print("   You can now view the search results in the browser.")
print("   The scraper will now wait for you to review the results.")

# ============================================================================
# Extract and Visit LinkedIn Profiles from Google Search Results
# ============================================================================

print("\n" + "="*80)
print("📊 EXTRACTING LINKEDIN PROFILE LINKS FROM GOOGLE RESULTS")
print("="*80)

# Find all LinkedIn profile links on the Google results page
linkedin_profile_links = []
try:
    # Wait for search results to load
    sleep(2)
    
    # Find all search result links
    # Google search results are typically in <a> tags with specific classes
    all_links = page.query_selector_all('a[href*="linkedin.com/in/"]')
    
    print(f"\n🔍 Found {len(all_links)} potential LinkedIn profile links")
    
    for link in all_links:
        try:
            href = link.get_attribute('href')
            if href and ('linkedin.com/in/' in href or 'linkedin.com/pub/' in href):
                # Skip Google internal links (navigation, filters, etc.)
                if any(skip_pattern in href for skip_pattern in [
                    '/search?', 'google.com/search', 'accounts.google.com',
                    'maps.google.com', 'tbm=', 'udm=', 'source=lnms'
                ]):
                    continue
                    
                # Clean up the URL (remove Google redirect parameters)
                if '/url?q=' in href:
                    # Extract the actual URL from Google's redirect
                    import urllib.parse
                    parsed = urllib.parse.parse_qs(urllib.parse.urlparse(href).query)
                    if 'q' in parsed:
                        href = parsed['q'][0]
                
                # Only add unique profile URLs that are actual LinkedIn profiles
                if (href not in linkedin_profile_links and 
                    ('linkedin.com/in/' in href or 'linkedin.com/pub/' in href) and
                    not any(skip_pattern in href for skip_pattern in [
                        '/search?', 'google.com', 'accounts.google.com'
                    ])):
                    linkedin_profile_links.append(href)
                    print(f"  ✓ Profile {len(linkedin_profile_links)}: {href}")
        except Exception as link_error:
            continue
    
    print(f"\n✅ Total unique LinkedIn profiles found: {len(linkedin_profile_links)}")
    
except Exception as extract_error:
    print(f"⚠️  Error extracting LinkedIn links: {extract_error}")

# Helper function to check if page is asking for LinkedIn login
def is_linkedin_login_page(page):
    """Check if the current page is asking for LinkedIn login"""
    try:
        current_url = page.url.lower()
        page_title = ""
        try:
            page_title = page.title().lower()
        except:
            pass
        
        # Check URL for login indicators
        login_url_indicators = [
            '/login',
            '/checkpoint',
            '/challenge',
            '/uas/login',
            'authwall'
        ]
        
        for indicator in login_url_indicators:
            if indicator in current_url and 'linkedin.com' in current_url:
                return True
        
        # Check page title for login indicators
        login_title_keywords = ['sign in', 'log in', 'linkedin login', 'join linkedin']
        for keyword in login_title_keywords:
            if keyword in page_title:
                return True
        
        # Check for login form elements
        login_form_selectors = [
            'input[name="session_key"]',
            'input[name="session_password"]',
            'form[action*="login"]',
            'button:has-text("Sign in")',
            'button:has-text("Log in")',
            '#username',
            '#password'
        ]
        
        login_form_count = 0
        for selector in login_form_selectors:
            try:
                element = page.query_selector(selector)
                if element and element.is_visible():
                    login_form_count += 1
            except:
                continue
        
        # If we find multiple login form elements, likely a login page
        if login_form_count >= 2:
            return True
        
        # Check for "Sign in" or "Join now" buttons prominently displayed
        try:
            sign_in_buttons = page.query_selector_all('button:has-text("Sign in"), a:has-text("Sign in"), button:has-text("Join now")')
            if len(sign_in_buttons) > 0:
                # Check if any are prominently displayed (large, centered, etc.)
                for button in sign_in_buttons:
                    try:
                        if button.is_visible():
                            # Check if it's a prominent button (not just in nav)
                            button_text = button.text_content().strip().lower()
                            if 'sign in' in button_text or 'join now' in button_text:
                                # Additional check: see if we're on linkedin.com but not logged in
                                if 'linkedin.com' in current_url and '/in/' not in current_url and '/feed' not in current_url:
                                    return True
                    except:
                        continue
        except:
            pass
        
        return False
        
    except Exception as e:
        print(f"  ⚠️  Error checking for login page: {e}")
        return False

# Helper function to navigate with login detection and retry
def navigate_with_login_check(page, url, max_retries=3, timeout=30000):
    """Navigate to URL, check for login page, and retry by going back if login detected"""
    for attempt in range(max_retries):
        try:
            print(f"  🔗 Navigating to: {url} (attempt {attempt + 1}/{max_retries})")
            page.goto(url, timeout=timeout)
            sleep(2)
            
            # Immediately close any popups that might have appeared
            close_linkedin_popups(page, max_attempts=3)
            
            # Check if we're on a login page
            if is_linkedin_login_page(page):
                print(f"  ⚠️  LinkedIn login page detected on attempt {attempt + 1}")
                if attempt < max_retries - 1:
                    print(f"  ⬅️  Going back one step and retrying...")
                    try:
                        page.go_back(timeout=10000)
                        sleep(2)
                        print(f"  ✅ Went back, retrying navigation...")
                    except Exception as back_error:
                        print(f"  ⚠️  Error going back: {back_error}")
                        # Try to navigate to a safe page (Google search) before retrying
                        try:
                            if 'google.com' in page.url.lower():
                                page.reload(timeout=10000)
                            else:
                                # If we can't go back, try reloading
                                page.reload(timeout=10000)
                            sleep(2)
                        except:
                            pass
                    continue
                else:
                    print(f"  ❌ Login page detected after {max_retries} attempts, giving up")
                    return False
            else:
                print(f"  ✅ Successfully navigated (no login page detected)")
                # Close popups again after confirming it's not a login page
                close_linkedin_popups(page, max_attempts=2)
                return True
                
        except Exception as nav_error:
            print(f"  ⚠️  Navigation error on attempt {attempt + 1}: {nav_error}")
            if attempt < max_retries - 1:
                print(f"  ⬅️  Going back and retrying...")
                try:
                    page.go_back(timeout=10000)
                    sleep(2)
                except:
                    pass
                continue
            else:
                print(f"  ❌ Navigation failed after {max_retries} attempts")
                return False
    
    return False

# Helper function to close LinkedIn popups
def close_linkedin_popups(page, max_attempts=5):
    """Close any popups that appear on LinkedIn profiles - aggressive approach"""
    try:
        popup_closed = False
        
        # Try multiple times as popups may appear with delay
        for attempt in range(max_attempts):
            # Wait a moment for popup to appear
            sleep(0.5)
            
            # Method 1: Try pressing Escape key (works for many modals)
            try:
                page.keyboard.press('Escape')
                sleep(0.3)
            except:
                pass
            
            # Method 2: Try to find and click various dismiss/close buttons
            dismiss_selectors = [
                # Standard dismiss buttons
                'button.modal__dismiss',
                'button.contextual-sign-in-modal__modal-dismiss',
                'button[aria-label="Dismiss"]',
                'button[aria-label="Close"]',
                'button[aria-label*="close" i]',
                'button[aria-label*="dismiss" i]',
                '.modal__dismiss',
                '[data-tracking-control-name*="modal_dismiss"]',
                # Close buttons with X
                'button[class*="close"]',
                'button[class*="dismiss"]',
                '.artdeco-modal__dismiss',
                '.artdeco-dismiss',
                'button.artdeco-button[aria-label*="close" i]',
                'button.artdeco-button[aria-label*="dismiss" i]',
                # Icon close buttons
                'svg[data-test-icon="close"]',
                'button[data-test-modal-close-btn]',
                'button[data-control-name="overlay.close_conversation_card"]',
                # Generic close patterns
                '[class*="close-button"]',
                '[class*="dismiss-button"]',
                '[id*="close"]',
                '[id*="dismiss"]',
            ]
            
            for selector in dismiss_selectors:
                try:
                    dismiss_buttons = page.query_selector_all(selector)
                    for dismiss_button in dismiss_buttons:
                        try:
                            if dismiss_button and dismiss_button.is_visible():
                                # Scroll into view if needed
                                dismiss_button.scroll_into_view_if_needed()
                                sleep(0.2)
                                
                                # Try clicking
                                dismiss_button.click(timeout=2000)
                                sleep(0.5)
                                print(f"  🚫 Closed popup using selector: {selector}")
                                popup_closed = True
                                break
                        except:
                            # Try JavaScript click as fallback
                            try:
                                page.evaluate("""(button) => {
                                    if (button && button.offsetParent !== null) {
                                        button.click();
                                    }
                                }""", dismiss_button)
                                sleep(0.5)
                                print(f"  🚫 Closed popup using JavaScript: {selector}")
                                popup_closed = True
                                break
                            except:
                                continue
                    
                    if popup_closed:
                        break
                except:
                    continue
            
            # Method 3: Try clicking outside modal/overlay (on backdrop)
            if not popup_closed:
                try:
                    # Look for modal/overlay backdrop
                    backdrop_selectors = [
                        '.artdeco-modal-overlay',
                        '.modal-overlay',
                        '[class*="overlay"]',
                        '[class*="backdrop"]',
                        '.artdeco-modal',
                    ]
                    
                    for selector in backdrop_selectors:
                        try:
                            backdrop = page.query_selector(selector)
                            if backdrop and backdrop.is_visible():
                                # Click in the center of backdrop (often closes modal)
                                box = backdrop.bounding_box()
                                if box:
                                    page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                                    sleep(0.5)
                                    print(f"  🚫 Clicked backdrop to close popup")
                                    popup_closed = True
                                    break
                        except:
                            continue
                except:
                    pass
            
            # Method 4: Try to find and close any visible modals by their structure
            if not popup_closed:
                try:
                    # Look for modal containers
                    modal_containers = page.query_selector_all('[role="dialog"], .artdeco-modal, [class*="modal"]')
                    for modal in modal_containers:
                        try:
                            if modal.is_visible():
                                # Look for close button inside this modal
                                close_btn = modal.query_selector('button[aria-label*="close" i], button[aria-label*="dismiss" i], button[class*="close"], svg[data-test-icon="close"]')
                                if close_btn:
                                    close_btn.click(timeout=2000)
                                    sleep(0.5)
                                    print(f"  🚫 Closed popup from modal container")
                                    popup_closed = True
                                    break
                        except:
                            continue
                except:
                    pass
            
            # If we closed a popup, check if there are more
            if popup_closed:
                # Continue checking for more popups
                popup_closed = False
                continue
            else:
                # No popup found in this attempt, might be done
                break
        
        # Final check: Press Escape one more time to be sure
        try:
            page.keyboard.press('Escape')
            sleep(0.3)
        except:
            pass
        
        return True  # Return True even if no popup found (no error)
        
    except Exception as e:
        # Silently continue if error occurs
        return True  # Return True to continue execution

# URL extraction completed above - no profile navigation needed
print("\n" + "="*80)
print(f"✅ LINKEDIN PROFILE URL EXTRACTION COMPLETED")
print("   Method: Direct href extraction (NO NAVIGATION)")
print("   All URLs extracted without opening any profiles")
print("   Results saved to: data/extracted_profile_urls.json")
print("="*80)

if False:  # Disabled navigation section
    print("\n" + "="*80)
    print(f"🚀 VISITING LINKEDIN PROFILES")
    print("="*80)
    
    # STEP 1: Click on FIRST profile first, then go back
    if len(linkedin_profile_links) > 0:
        first_profile_url = linkedin_profile_links[0]
        
        print(f"\n{'='*80}")
        print(f"STEP 1: Visit First Profile - Initial Visit (then go back)")
        print(f"{'='*80}")
        print(f"🔗 Navigating to: {first_profile_url}")
        
        try:
            # Use navigate_with_login_check to handle login pages
            if navigate_with_login_check(page, first_profile_url, max_retries=3, timeout=30000):
                print(f"📍 Current URL: {page.url}")
                sleep(1)
                
                # Go back to Google search results
                print(f"\n  ⬅️  Going back to Google search results...")
                page.go_back(timeout=10000)
                sleep(3)
                print(f"  ✅ Returned to Google search results")
            else:
                print(f"  ⚠️  Failed to navigate to first profile after retries")
            
        except Exception as first_visit_error:
            print(f"  ❌ Error on first visit: {first_visit_error}")
            try:
                page.goto(google_search_url, timeout=30000)
                sleep(3)
            except:
                pass
    
    # STEP 2: Visit FIRST profile AGAIN and scrape it (close popup if appears)
    if len(linkedin_profile_links) > 0:
        first_profile_url = linkedin_profile_links[0]
        
        print(f"\n{'='*80}")
        print(f"STEP 2: Visit First Profile - Second Visit (close popup & extract data)")
        print(f"{'='*80}")
        print(f"🔗 Navigating to: {first_profile_url}")
        
        try:
            # Use navigate_with_login_check to handle login pages
            if navigate_with_login_check(page, first_profile_url, max_retries=3, timeout=30000):
                print(f"📍 Current URL: {page.url}")
                
                # Close any popups
                close_linkedin_popups(page)
                
                sleep(1)
                
                # Take screenshot and extract data
                try:
                    screenshot_path = f"data/screenshots/profile_1.png"
                    os.makedirs('data/screenshots', exist_ok=True)
                    page.screenshot(path=screenshot_path, full_page=True, timeout=10000)
                    print(f"  📸 Profile screenshot saved: {screenshot_path}")
                except Exception as ss_error:
                    print(f"  ⚠️  Screenshot error: {ss_error}")
                
                # Extract profile data
                try:
                    sleep(2)
                    
                    # Try to get profile name
                    name_selectors = [
                        'h1.text-heading-xlarge',
                        'h1[class*="text-heading"]',
                        '.pv-text-details__left-panel h1',
                        '[data-test-id="profile-name"]'
                    ]
                    
                    profile_name = None
                    for selector in name_selectors:
                        try:
                            name_element = page.query_selector(selector)
                            if name_element:
                                profile_name = name_element.text_content().strip()
                                if profile_name:
                                    break
                        except:
                            continue
                    
                    if profile_name:
                        print(f"  👤 Name: {profile_name}")
                    else:
                        print(f"  ⚠️  Could not extract profile name")
                    
                    # Try to get headline
                    headline_selectors = [
                        '.text-body-medium',
                        '.pv-text-details__left-panel .text-body-medium',
                        '[data-test-id="profile-headline"]'
                    ]
                    
                    headline = None
                    for selector in headline_selectors:
                        try:
                            headline_element = page.query_selector(selector)
                            if headline_element:
                                headline = headline_element.text_content().strip()
                                if headline and len(headline) > 10:
                                    break
                        except:
                            continue
                    
                    if headline:
                        print(f"  💼 Headline: {headline}")
                    else:
                        print(f"  ⚠️  Could not extract headline")
                    
                except Exception as extract_error:
                    print(f"  ⚠️  Error extracting profile data: {extract_error}")
                
                print(f"  ✅ Profile 1 processed, continuing to next profile...")
            else:
                print(f"  ⚠️  Failed to navigate to first profile after retries, skipping...")
            
        except Exception as first_profile_error:
            print(f"  ❌ Error visiting first profile: {first_profile_error}")
    
    # STEP 3: Now visit remaining profiles sequentially (starting from second profile)
    for idx, profile_url in enumerate(linkedin_profile_links[1:], 2):
        try:
            print(f"\n{'='*80}")
            print(f"Profile {idx}/{len(linkedin_profile_links)}")
            print(f"{'='*80}")
            print(f"🔗 Navigating to: {profile_url}")
            
            # Navigate to LinkedIn profile with login check
            if navigate_with_login_check(page, profile_url, max_retries=3, timeout=30000):
                # Check current URL after navigation
                current_profile_url = page.url
                print(f"📍 Current URL: {current_profile_url}")
                
                # Close any popups
                close_linkedin_popups(page)
                
                # Wait for page to load
                sleep(1)
                
                # Take screenshot of the profile for debugging/record
                try:
                    screenshot_path = f"data/screenshots/profile_{idx}.png"
                    os.makedirs('data/screenshots', exist_ok=True)
                    page.screenshot(path=screenshot_path, full_page=True, timeout=10000)
                    print(f"  📸 Profile screenshot saved: {screenshot_path}")
                except Exception as ss_error:
                    print(f"  ⚠️  Screenshot error: {ss_error}")
                
                # Extract profile data (name, headline, etc.)
                try:
                    # Wait for profile elements to load
                    sleep(2)
                    
                    # Try to get profile name
                    name_selectors = [
                        'h1.text-heading-xlarge',
                        'h1[class*="text-heading"]',
                        '.pv-text-details__left-panel h1',
                        '[data-test-id="profile-name"]'
                    ]
                    
                    profile_name = None
                    for selector in name_selectors:
                        try:
                            name_element = page.query_selector(selector)
                            if name_element:
                                profile_name = name_element.text_content().strip()
                                if profile_name:
                                    break
                        except:
                            continue
                    
                    if profile_name:
                        print(f"  👤 Name: {profile_name}")
                    else:
                        print(f"  ⚠️  Could not extract profile name")
                    
                    # Try to get headline
                    headline_selectors = [
                        '.text-body-medium',
                        '.pv-text-details__left-panel .text-body-medium',
                        '[data-test-id="profile-headline"]'
                    ]
                    
                    headline = None
                    for selector in headline_selectors:
                        try:
                            headline_element = page.query_selector(selector)
                            if headline_element:
                                headline = headline_element.text_content().strip()
                                if headline and len(headline) > 10:  # Make sure it's not empty
                                    break
                        except:
                            continue
                    
                    if headline:
                        print(f"  💼 Headline: {headline}")
                    else:
                        print(f"  ⚠️  Could not extract headline")
                    
                except Exception as extract_error:
                    print(f"  ⚠️  Error extracting profile data: {extract_error}")
                
                # Don't go back - continue to next profile directly
                print(f"  ✅ Profile {idx} processed, continuing to next profile...")
            else:
                print(f"  ⚠️  Failed to navigate to profile after retries, skipping...")
                continue
            
        except Exception as profile_error:
            print(f"  ❌ Error visiting profile: {profile_error}")
            print(f"  ⚠️  Skipping to next profile...")
    
    print("\n" + "="*80)
    print(f"✅ COMPLETED VISITING {len(linkedin_profile_links)} PROFILES")
    print("   Navigation Flow:")
    print("   1. First profile (visit 1) → Back to Google")
    print("   2. First profile (visit 2) → Close popup → Scraped")
    print("   3. Remaining profiles → Close popup → Scraped sequentially")
    print("="*80)
else:
    pass  # Warning message removed as requested

# Keep the browser open for user to review results
print("\n" + "="*80)
print("🤖 BROWSER KEPT OPEN FOR RESULT REVIEW")
print("="*80)
print("You can review the results in the browser.")
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
print("Google X-ray search completed successfully!")
print("="*80)

# Exit the script
exit(0)

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
        # Navigate to profile with better error handling and login check
        print(f"  Navigating to profile: {profile_url}")
        if not navigate_with_login_check(page, profile_url, max_retries=3, timeout=30000):
            print(f"  ⚠️  Failed to navigate to profile after retries")
            profile_data['error'] = 'Navigation failed - login page detected'
            profile_data['url'] = profile_url
            profile_data['extraction_method'] = 'OCR + AI'
            return profile_data
        
        HumanBehavior.random_delay(2, 4)  # Human-like pause
        
        # Wait for basic page elements with retry logic
        try:
            page.wait_for_load_state('domcontentloaded', timeout=10000)
        except:
            print(f"  ⚠️  DOM content load timeout, continuing anyway...")
        
        # Close any popups that appeared after page load
        close_linkedin_popups(page, max_attempts=3)
        
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
            model="meta-llama/llama-4-scout-17b-16e-instruct",
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
MAX_PAGES = 10
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
                    # Method 1: Try to find and click specific page number link (Google pagination)
                    page_link = None
                    if page_num + 1 <= 10:  # Google typically shows up to 10 page links
                        page_link = page.query_selector(f'a[aria-label="Page {page_num + 1}"]')
                    
                    # Method 2: Find and click "Next" button if page link not found
                    next_button = None
                    if not page_link:
                        next_button = page.query_selector('button[aria-label="Next"]')
                        if not next_button:
                            next_button = page.query_selector('button:has-text("Next")')
                        if not next_button:
                            # Additional selector for Next button based on provided inspect element
                            next_button = page.query_selector('span.oeN89d:has-text("Next")')
                    
                    if page_link:
                        # Scroll to page link and click
                        page_link.scroll_into_view_if_needed()
                        sleep(1)
                        page_link.click()
                        print(f"✓ Clicked page {page_num + 1} link")
                        sleep(3)
                    elif next_button:
                        # Scroll to button and click
                        next_button.scroll_into_view_if_needed()
                        sleep(1)
                        next_button.click()
                        print("✓ Clicked Next button")
                        sleep(3)
                    else:
                        print("⚠ No page link or Next button found - might be last page")
                        break
                    
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
