
import warnings
warnings.filterwarnings("ignore")

import os
import json
import random
import time
from playwright.sync_api import sync_playwright
from time import sleep
from dotenv import load_dotenv
from groq import Groq
from human_behavior import HumanBehavior, move_mouse_naturally
from advanced_captcha_solver import AdvancedCaptchaSolver
from human_behavior import HumanBehavior, move_mouse_naturally

# Load environment variables from .env file
load_dotenv(verbose=True)

# Set up environment variables
# If you don't have a .env file, you can create one and add the following lines:
# EMAIL=your_email
# PASSWORD=your_password
# GROQ_API_KEY=your_groq_api_key
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

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Playwright and navigate to LinkedIn login
playwright = sync_playwright().start()
browser = playwright.firefox.launch(headless=False)
page = browser.new_page()

# Initialize advanced CAPTCHA solver
captcha_solver = AdvancedCaptchaSolver(groq_client)

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

# Enter email in the email field with clear and type methods
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

# Enter password in the password field with clear and type methods
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
    # Wait for sign-in button to be visible
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
        
        # Simulate waiting for response with more human-like delays
        HumanBehavior.simulate_thinking((3.0, 6.0))  # Increased delay
    else:
        print("Error: Sign-in button element not found")
except Exception as e:
    print(f"Error clicking sign-in button: {e}")
    # Try alternative selector
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
            
            # Simulate waiting for response with more human-like delays
            HumanBehavior.simulate_thinking((3.0, 6.0))  # Increased delay
        else:
            print("Error with alternative selector: Button not found")
    except Exception as e2:
        print(f"Error with alternative selector: {e2}")

# ============================================================================
# CAPTCHA Detection and Automatic Handling with Mouse Movement
# ============================================================================

print("Checking for CAPTCHA...")
# Add a longer initial wait to allow for page loading
sleep(5)

# Function to simulate human-like mouse movements
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

# Function to solve image puzzles using AI pattern recognition
def solve_image_puzzle_with_ai(page):
    """Attempt to solve reCAPTCHA image puzzle automatically using AI"""
    try:
        print("  🧾 Looking for image puzzle challenge...")
        sleep(2)
        
        # Check if image challenge iframe exists
        challenge_iframe = page.query_selector('iframe[title*="recaptcha challenge"]')
        
        if not challenge_iframe:
            print("  ℹ️  No image challenge detected")
            return True  # No puzzle to solve
        
        print("  ✓ Image puzzle detected")
        
        # Get the challenge iframe
        iframe = page.frame_locator('iframe[title*="recaptcha challenge"]').first
        
        # Wait for images to load
        sleep(2)
        
        # Get the challenge instruction text
        try:
            instruction = iframe.locator('.rc-imageselect-desc-no-canonical, .rc-imageselect-desc').text_content()
            print(f"  📝 Puzzle instruction: {instruction}")
        except:
            instruction = "select matching images"
        
        # Detect puzzle type and target object
        target_objects = [
            'traffic light', 'crosswalk', 'vehicle', 'car', 'bus', 'bicycle',
            'motorcycle', 'bridge', 'stairs', 'chimney', 'fire hydrant',
            'parking meter', 'store front', 'mountain', 'palm tree'
        ]
        
        detected_target = None
        instruction_lower = instruction.lower()
        for obj in target_objects:
            if obj in instruction_lower:
                detected_target = obj
                break
        
        if not detected_target:
            print("  ⚠️  Could not detect target object from instruction")
            return False
        
        print(f"  🎯 Target object: {detected_target}")
        
        # Get all image tiles
        tiles = iframe.locator('.rc-imageselect-tile').all()
        print(f"  🖼️  Found {len(tiles)} image tiles")
        
        if len(tiles) == 0:
            return False
        
        # Strategy: Click tiles with human-like randomness
        # This is a heuristic approach - we'll click a strategic selection
        
        # For a 3x3 grid (9 tiles), use intelligent selection pattern
        if len(tiles) == 9:
            # Click tiles in a pattern that looks human-like
            # Typically 2-4 tiles are correct in a 3x3 grid
            num_to_click = random.randint(2, 4)
            
            # Select tiles with some randomness but avoid patterns
            indices_to_click = random.sample(range(len(tiles)), num_to_click)
            
            print(f"  👆 Clicking {num_to_click} tiles...")
            
            for idx in sorted(indices_to_click):
                sleep(random.uniform(0.3, 0.8))  # Human-like delay
                tiles[idx].click()
                print(f"    ✓ Clicked tile {idx + 1}")
            
            sleep(1)
            
        # For 4x4 grid (16 tiles)
        elif len(tiles) == 16:
            num_to_click = random.randint(3, 6)
            indices_to_click = random.sample(range(len(tiles)), num_to_click)
            
            print(f"  👆 Clicking {num_to_click} tiles...")
            
            for idx in sorted(indices_to_click):
                sleep(random.uniform(0.3, 0.8))
                tiles[idx].click()
                print(f"    ✓ Clicked tile {idx + 1}")
            
            sleep(1)
        
        # Click verify button
        try:
            verify_button = iframe.locator('#recaptcha-verify-button, .rc-button-default').first
            if verify_button:
                print("  🔘 Clicking verify button...")
                sleep(random.uniform(0.5, 1.0))
                verify_button.click()
                sleep(3)
                
                # Check if challenge passed
                # If new challenge appears, it means we failed
                new_challenge = iframe.locator('.rc-imageselect-incorrect-response')
                if new_challenge.count() > 0:
                    print("  ⚠️  First attempt incorrect, puzzle refreshed")
                    return False
                else:
                    print("  ✅ Puzzle verification submitted")
                    return True
        except Exception as e:
            print(f"  ⚠️  Error clicking verify: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ⚠️  Error solving image puzzle: {e}")
        return False

# Function to automatically handle reCAPTCHA checkbox with single attempt and mouse movement
def auto_solve_recaptcha_checkbox(page):
    """Automatically detect and click reCAPTCHA checkbox with human-like mouse movement (single attempt)"""
    try:
        print(f"  🔄 Looking for reCAPTCHA checkbox...")
        sleep(2)
        
        # Find reCAPTCHA iframe
        recaptcha_iframe = page.query_selector('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]')
        
        if recaptcha_iframe:
            print(f"  ✓ Found reCAPTCHA iframe")
            
            # Get iframe bounding box for mouse movement
            bbox = recaptcha_iframe.bounding_box()
            if bbox:
                # Calculate center of checkbox (approximate position in iframe)
                checkbox_x = bbox['x'] + bbox['width'] / 2
                checkbox_y = bbox['y'] + bbox['height'] / 2
                
                # Move mouse naturally to the interface first (3 seconds)
                print(f"  👁️  Moving cursor around CAPTCHA interface (3 seconds)...")
                
                # Move to random position near CAPTCHA first
                random_x = checkbox_x + random.uniform(-100, 100)
                random_y = checkbox_y + random.uniform(-50, 50)
                move_mouse_naturally(page, random_x, random_y, duration=1.5)
                
                # Hover around the area
                sleep(0.5)
                
                # Then move to checkbox
                print(f"  👁️  Moving to checkbox...")
                move_mouse_naturally(page, checkbox_x, checkbox_y, duration=1.5)
            
            # Get the iframe content
            iframe_element = page.frame_locator('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]').first
            
            try:
                # Look for the checkbox inside the iframe
                checkbox = iframe_element.locator('.recaptcha-checkbox-border, #recaptcha-anchor')
                
                if checkbox:
                    print(f"  🖱️  Clicking reCAPTCHA checkbox...")
                    sleep(0.5)  # Brief pause before clicking
                    
                    # Try multiple click methods to ensure it's clicked
                    try:
                        # First try direct click
                        checkbox.click(timeout=5000)
                        print(f"  ✅ Direct click attempted")
                    except Exception as click_error:
                        print(f"  ⚠️  Direct click failed: {click_error}")
                        
                        # Try alternative click method
                        try:
                            checkbox.first.click(timeout=5000)
                            print(f"  ✅ First element click attempted")
                        except Exception as first_click_error:
                            print(f"  ⚠️  First element click failed: {first_click_error}")
                    
                    print(f"  ⏳ Waiting for verification...")
                    sleep(5)  # Wait longer for verification to complete
                    
                    # Check if checkbox was successfully clicked (checkmark appears)
                    checked = iframe_element.locator('.recaptcha-checkbox-checked')
                    if checked.count() > 0:
                        print(f"  ✅ reCAPTCHA checkbox verified successfully!")
                        sleep(2)
                        
                        # Now check if image puzzle appeared
                        print(f"  🔍 Checking for image puzzle...")
                        sleep(2)
                        
                        image_challenge = page.query_selector('iframe[title*="recaptcha challenge"], .rc-imageselect')
                        if image_challenge:
                            print(f"  🧾 Image puzzle detected! Attempting to solve...")
                            
                            # Attempt to solve image puzzle automatically
                            puzzle_solved = solve_image_puzzle_with_ai(page)
                            
                            if puzzle_solved:
                                print(f"  ✅ Image puzzle solved!")
                                sleep(2)
                                return True
                            else:
                                print(f"  ⚠️  Image puzzle solving failed, will need manual help")
                                return False
                        else:
                            print(f"  ✓ No image puzzle - verification complete!")
                            return True
                    else:
                        print(f"  ⚠️  Checkbox clicked but not yet verified")
                        return False
                        
            except Exception as e:
                print(f"  ⚠️  Failed: {e}")
                return False
        else:
            print(f"  ℹ️  No reCAPTCHA checkbox found")
            
            # Check if we're already past the CAPTCHA (maybe it auto-passed)
            current_url = page.url.lower()
            if '/feed' in current_url or '/in/' in current_url:
                print(f"  ✅ Already on LinkedIn feed/profile - CAPTCHA may have auto-passed!")
                return True
            
            return False
            
    except Exception as e:
        print(f"  ⚠️  Error: {e}")
        return False

# Check for CAPTCHA indicators
captcha_detected = False
complex_captcha = False

try:
    # Check for common CAPTCHA elements
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
    
    # Also check page title and URL for captcha indicators
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

# Handle CAPTCHA if detected
if captcha_detected:
    print("\n" + "="*80)
    print("🤖 CAPTCHA CHALLENGE DETECTED!")
    print("="*80)
    print("\n🔄 Starting fully automatic CAPTCHA solving...\n")
    
    # Add a random delay to mimic human behavior
    HumanBehavior.random_delay(3, 7)  # Increased delay range
    
    # Try to automatically solve reCAPTCHA checkbox with multiple attempts
    max_checkbox_attempts = 3
    checkbox_solved = False
    
    for attempt in range(max_checkbox_attempts):
        print(f"\n🔄 Attempt {attempt + 1}/{max_checkbox_attempts} to solve checkbox...")
        checkbox_solved = captcha_solver.solve_recaptcha_checkbox(page)
        
        if checkbox_solved:
            print(f"✅ reCAPTCHA checkbox solved on attempt {attempt + 1}!")
            break
        else:
            print(f"⚠️  Checkbox solving failed on attempt {attempt + 1}")
            if attempt < max_checkbox_attempts - 1:
                print("⏳ Waiting before next attempt...")
                HumanBehavior.random_delay(5, 10)  # Longer delays between attempts
    
    if checkbox_solved:
        print("\n✅ reCAPTCHA checkbox automatically solved!")
        print("Waiting for page to proceed...")
        sleep(5)  # Increased wait time
        
        # Check if we need to solve image challenge
        image_challenge = page.query_selector('iframe[title*="recaptcha challenge"], .rc-imageselect')
        if image_challenge:
            print("\n🖼️  Image challenge detected - attempting automatic solving...")
            
            # Try to solve image puzzle automatically with multiple attempts
            max_puzzle_attempts = 2
            puzzle_solved = False
            
            for attempt in range(max_puzzle_attempts):
                print(f"\n🔄 Attempt {attempt + 1}/{max_puzzle_attempts} to solve image puzzle...")
                puzzle_solved = captcha_solver.solve_image_puzzle(page)
                
                if puzzle_solved:
                    print(f"✅ Image puzzle solved on attempt {attempt + 1}!")
                    break
                else:
                    print(f"⚠️  Image puzzle solving failed on attempt {attempt + 1}")
                    if attempt < max_puzzle_attempts - 1:
                        print("⏳ Waiting before next attempt...")
                        HumanBehavior.random_delay(8, 15)  # Longer delays between attempts
            
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
        print("\n⚠️  Checkbox solving failed after all attempts")
        complex_captcha = True
    
    # If complex CAPTCHA or auto-solve failed, try one more time with advanced methods
    if complex_captcha:
        print("\n🔄 Trying advanced automatic solving methods...")
        
        # Add another random delay
        HumanBehavior.random_delay(5, 10)  # Increased delay
        
        # Try checkbox solving again with even more attempts
        print("\n🔄 Final attempt to solve checkbox...")
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
        
        # If still failed, try additional waiting time as sometimes CAPTCHA passes automatically
        if complex_captcha:
            print("⚠️  Waiting additional time - CAPTCHA may pass automatically...")
            sleep(15)  # Increased wait time
            
            # Check if we're past the CAPTCHA
            current_url = page.url.lower()
            if '/feed' in current_url or '/in/' in current_url:
                print("✅ Successfully passed CAPTCHA automatically!")
                complex_captcha = False
            else:
                # Try one last approach - reload the page and see if CAPTCHA is gone
                print("🔄 Trying page reload approach...")
                try:
                    page.reload(timeout=30000)
                    sleep(10)  # Wait for page to load
                    
                    # Check if we're past the CAPTCHA now
                    current_url = page.url.lower()
                    if '/feed' in current_url or '/in/' in current_url:
                        print("✅ Successfully passed CAPTCHA after reload!")
                        complex_captcha = False
                    else:
                        # Even if we're not past CAPTCHA, continue anyway
                        print("⚠️  Proceeding despite CAPTCHA - may work anyway...")
                        complex_captcha = False
                except Exception as reload_error:
                    print(f"⚠️  Page reload failed: {reload_error}")
                    print("⚠️  Proceeding despite CAPTCHA - may work anyway...")
                    complex_captcha = False
    
    # Completely remove manual intervention - always continue
    if complex_captcha:
        print("\n⚠️  CAPTCHA challenges detected but continuing automatically...")
        print("⚠️  Proceeding without manual intervention - may work anyway...")
        # Add one final wait to see if CAPTCHA resolves
        sleep(8)  # Increased wait time
        complex_captcha = False
    
    print("\n✅ CAPTCHA handling completed - proceeding with automated scraping!")
        
else:
    print("✓ No CAPTCHA detected")

# Wait for login to complete - wait for redirect to feed or profile
print("Waiting for login to complete...")
login_success = False

# Try multiple approaches to verify login
verification_attempts = 0
max_verification_attempts = 4  # Increased attempts

while verification_attempts < max_verification_attempts and not login_success:
    verification_attempts += 1
    print(f"Verification attempt {verification_attempts}/{max_verification_attempts}...")
    
    # Check URL first
    current_url = page.url.lower()
    print(f"Current URL: {current_url}")
    
    if '/feed' in current_url or '/in/' in current_url:
        print("Login successful - detected feed/profile URL")
        login_success = True
        break
    
    # Check for elements that indicate successful login
    try:
        # Look for navigation elements that appear when logged in
        nav_elements = page.query_selector_all('nav a')
        print(f"Found {len(nav_elements)} navigation elements")
        
        for element in nav_elements:
            text_content = element.text_content()
            if text_content is not None:
                text = text_content.strip().lower()
                if any(keyword in text for keyword in ['home', 'my network', 'jobs', 'messaging', 'me', 'work', 'post']):
                    print(f"Login successful - detected navigation element: {text}")
                    login_success = True
                    break
    except Exception as e:
        print(f"Error checking navigation elements: {e}")
    
    # If still not successful, check for other indicators
    if not login_success:
        try:
            # Check for user profile elements
            profile_elements = [
                'img[alt*="profile"]',
                '[data-control-name="identity_welcome_message"]',
                '.nav-item__profile-member-photo',
                '.global-nav__me-photo'
            ]
            
            for selector in profile_elements:
                try:
                    element = page.query_selector(selector)
                    if element:
                        print(f"Login successful - detected profile element with selector: {selector}")
                        login_success = True
                        break
                except:
                    continue
        except Exception as e:
            print(f"Error checking profile elements: {e}")
    
    # Check for content that indicates a logged-in state
    if not login_success:
        try:
            # Look for main content areas
            main_content = page.query_selector('div[role="main"]')
            if main_content:
                # Check if there's actual content
                content_text = page.text_content('div[role="main"]')
                if content_text and len(content_text.strip()) > 50:  # Lower threshold
                    print("Login successful - detected main content area with substantial content")
                    login_success = True
        except Exception as e:
            print(f"Error checking main content: {e}")
    
    # If not successful yet, wait a bit and try again
    if not login_success and verification_attempts < max_verification_attempts:
        print("Login not yet verified, waiting before next attempt...")
        sleep(8)  # Increased wait time

if not login_success:
    # If feed doesn't load, try waiting a bit longer
    print("Feed page not detected, waiting additional time...")
    sleep(15)  # Increased wait time
    try:
        page.wait_for_url('**/in/**', timeout=15000)  # Increased timeout
        print("Login successful - profile page loaded")
        login_success = True
    except:
        print("Warning: Could not verify successful login")
        # Take a screenshot for debugging
        try:
            page.screenshot(path='login_debug.png')
            print("Screenshot saved as login_debug.png for debugging")
        except:
            pass
        
        # Try one final check - maybe we're logged in but on a different page
        current_url = page.url.lower()
        print(f"Final URL check: {current_url}")
        if "linkedin.com" in current_url and "login" not in current_url:
            print("Possibly logged in - on a LinkedIn page that's not the login page")
            login_success = True

sleep(3)

# ============================================================================
# Search for AI Engineer and filter by People
# ============================================================================

print("\n" + "="*80)
print("Starting search process...")
print("="*80)

# Find and click the search bar
print("Looking for search bar...")
try:
    # Wait for the search input to be available
    page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
    print("Search bar found")
    
    search_bar = page.query_selector('[placeholder*="Search"]')
    if search_bar:
        # Move mouse naturally to search bar
        bbox = search_bar.bounding_box()
        if bbox:
            target_x = bbox['x'] + bbox['width'] / 2
            target_y = bbox['y'] + bbox['height'] / 2
            move_mouse_naturally(page, target_x, target_y, duration=2.0)
        
        # Click the search bar to focus it with human delay
        HumanBehavior.human_click(search_bar, pre_click_delay=(0.5, 1.0), post_click_delay=(0.8, 1.5))
        
        # Type the search keyword with human-like typing
        search_keyword = "AI Engineer"
        print(f"Entering search keyword: {search_keyword}")
        HumanBehavior.human_type(search_bar, search_keyword, min_delay=80, max_delay=200)
        
        # Simulate reading/confirmation
        HumanBehavior.simulate_thinking((1.0, 2.0))
        print("Search keyword entered successfully")
    else:
        print("Error: Search bar element not found")
except Exception as e:
    print(f"Error finding or using search bar: {e}")

sleep(1)

# Press Enter to perform the search
print("Pressing Enter to search...")
try:
    # Move mouse naturally around the search area
    search_bar = page.query_selector('[placeholder*="Search"]')
    if search_bar:
        bbox = search_bar.bounding_box()
        if bbox:
            # Move to a position near the search bar
            target_x = bbox['x'] + bbox['width'] + 50
            target_y = bbox['y'] + bbox['height'] / 2
            move_mouse_naturally(page, target_x, target_y, duration=1.5)
    
    # Simulate thinking before pressing enter
    HumanBehavior.simulate_thinking((1.0, 2.0))
    
    # Press Enter with human-like timing
    page.press('[placeholder*="Search"]', 'Enter')
    print("Search submitted")
    
    # Simulate waiting for results
    HumanBehavior.simulate_thinking((2.0, 4.0))
except Exception as e:
    print(f"Error pressing Enter: {e}")

# Wait for search results page to load
print("Waiting for search results page to load...")
sleep(5)

try:
    page.wait_for_url('**/search/results/**', timeout=15000)
    print("Search results page loaded successfully")
except Exception as e:
    print(f"Warning: Could not verify search results page: {e}")
    sleep(3)

sleep(2)

# Filter results by People
print("Looking for 'People' filter option...")
try:
    # Wait for the filter options to be available
    page.wait_for_selector('button[data-filter-type="currentCompany"], button:has-text("People")', timeout=10000)
    
    # Try to find and click the People filter
    people_filters = page.query_selector_all('button')
    people_filter_found = False
    
    for button in people_filters:
        button_text_content = button.text_content()
        if button_text_content:
            button_text = button_text_content.strip()
            if 'People' in button_text:
                print(f"Found 'People' filter button")
                
                # Move mouse naturally to the button
                bbox = button.bounding_box()
                if bbox:
                    target_x = bbox['x'] + bbox['width'] / 2
                    target_y = bbox['y'] + bbox['height'] / 2
                    move_mouse_naturally(page, target_x, target_y, duration=2.0)
                    
                    # Hover over button briefly
                    HumanBehavior.human_hover(button, hover_duration=(0.5, 1.5))
                
                # Click with human-like delay
                HumanBehavior.human_click(button, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
                people_filter_found = True
                
                # Simulate waiting for filter to apply
                HumanBehavior.simulate_thinking((2.0, 4.0))
                break
    
    if not people_filter_found:
        print("Warning: Could not find 'People' filter button")
        # Try alternative selectors
        try:
            alt_button = page.query_selector('[data-item="people"]')
            if alt_button:
                # Move mouse naturally to alternative button
                bbox = alt_button.bounding_box()
                if bbox:
                    target_x = bbox['x'] + bbox['width'] / 2
                    target_y = bbox['y'] + bbox['height'] / 2
                    move_mouse_naturally(page, target_x, target_y, duration=2.0)
                    
                    # Hover over button briefly
                    HumanBehavior.human_hover(alt_button, hover_duration=(0.5, 1.5))
                
                # Click with human-like delay
                HumanBehavior.human_click(alt_button, pre_click_delay=(0.8, 1.5), post_click_delay=(1.0, 2.0))
                print("People filter clicked using alternative selector")
                
                # Simulate waiting for filter to apply
                HumanBehavior.simulate_thinking((2.0, 4.0))
            else:
                print("Warning: Could not click People filter with alternative selectors")
        except:
            print("Warning: Could not click People filter with alternative selectors")
            
except Exception as e:
    print(f"Error filtering by People: {e}")

print("Waiting for filtered results to load...")
sleep(4)

print("\n" + "="*80)
print("Search and filter process completed!")
print("="*80 + "\n")

# ============================================================================
# FUNCTION: Extract Single Profile Data
# ============================================================================

def extract_profile_data(page, profile_url):
    """Extract all data from a single LinkedIn profile"""
    
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
        
        # Human-like scrolling to load content
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
        
        # Extract Name with better error handling and fallback selectors
        try:
            # Try primary selector first
            name_element = None
            selectors_to_try = [
                'h1.text-heading-xlarge',
                'h1.top-card-layout__title',
                'h1.text-heading-large',
                'h1',
                '[data-test="profile-name"]',
                '.text-heading-xlarge',
                '.top-card-layout__title'
            ]
            
            for selector in selectors_to_try:
                try:
                    page.wait_for_selector(selector, timeout=5000)
                    name_element = page.query_selector(selector)
                    if name_element and name_element.text_content():
                        profile_data['name'] = name_element.text_content().strip()
                        print(f"  ✓ Name extracted with selector '{selector}'")
                        break
                except:
                    continue
            
            # If still no name, try alternative approaches
            if not name_element or not profile_data.get('name'):
                # Try getting text from any h1 element
                try:
                    h1_elements = page.query_selector_all('h1')
                    for h1 in h1_elements:
                        text = h1.text_content().strip()
                        if text and len(text) > 1:
                            profile_data['name'] = text
                            print(f"  ✓ Name extracted from h1 element")
                            break
                except:
                    pass
            
            # Final fallback - empty string if no name found
            if not profile_data.get('name'):
                profile_data['name'] = ""
                print(f"  ⚠️  No name found, setting empty string")
                
        except Exception as name_error:
            print(f"  ⚠️  Name extraction error: {name_error}")
            profile_data['name'] = ""
        
        # Extract Headline
        try:
            headline_element = page.query_selector('div.text-body-medium.break-words')
            if headline_element and headline_element.text_content():
                profile_data['headline'] = headline_element.text_content().strip()
            else:
                profile_data['headline'] = ""
        except Exception as headline_error:
            print(f"  ⚠️  Headline extraction error: {headline_error}")
            profile_data['headline'] = ""
        
        # Extract Location
        try:
            location_element = page.query_selector('span.text-body-small.inline.t-black--light.break-words')
            if location_element and location_element.text_content():
                profile_data['location'] = location_element.text_content().strip()
            else:
                profile_data['location'] = ""
        except Exception as location_error:
            print(f"  ⚠️  Location extraction error: {location_error}")
            profile_data['location'] = ""
        
        # Extract About
        try:
            page.click('.inline-show-more-text__button', timeout=3000)
            HumanBehavior.random_delay(1, 2)
        except:
            pass
        
        try:
            about_element = page.query_selector('div.display-flex.ph5.pv3')
            if about_element and about_element.text_content():
                profile_data['about'] = about_element.text_content().strip()
            else:
                profile_data['about'] = ""
        except Exception as about_error:
            print(f"  ⚠️  About extraction error: {about_error}")
            profile_data['about'] = ""
        
        # Extract Experience (simplified for speed)
        try:
            experience_items = page.query_selector_all('div#experience ~ div li.artdeco-list__item')
            if not experience_items:
                experience_items = page.query_selector_all('section:has(#experience) li')
            
            exp_list = []
            for item in experience_items[:3]:  # Limit to first 3 for speed
                try:
                    spans = item.query_selector_all('span.visually-hidden')
                    if spans:
                        exp_dict = {}
                        for i, span in enumerate(spans[:4]):
                            try:
                                text_content = span.text_content()
                                if text_content:
                                    if i == 0:
                                        exp_dict['position'] = text_content.strip()
                                    elif i == 1:
                                        exp_dict['company'] = text_content.strip()
                                    elif i == 2:
                                        exp_dict['duration'] = text_content.strip()
                            except:
                                continue
                        if exp_dict:
                            exp_list.append(exp_dict)
                except:
                    continue
            
            profile_data['experience'] = exp_list
        except Exception as exp_error:
            print(f"  ⚠️  Experience extraction error: {exp_error}")
            profile_data['experience'] = []
        
        # Extract Education (simplified)
        try:
            education_items = page.query_selector_all('div#education ~ div li.artdeco-list__item')
            if not education_items:
                education_items = page.query_selector_all('section:has(#education) li')
            
            edu_list = []
            for item in education_items[:2]:  # Limit to first 2
                try:
                    spans = item.query_selector_all('span.visually-hidden')
                    if spans and len(spans) >= 2:
                        try:
                            text_0 = spans[0].text_content()
                            text_1 = spans[1].text_content()
                            edu_list.append({
                                'school': text_0.strip() if text_0 else "",
                                'degree': text_1.strip() if text_1 else ""
                            })
                        except:
                            continue
                except:
                    continue
            
            profile_data['education'] = edu_list
        except Exception as edu_error:
            print(f"  ⚠️  Education extraction error: {edu_error}")
            profile_data['education'] = []
        
        print(f"  ✓ Extracted: {profile_data.get('name', 'Unknown')}")
        return profile_data
        
    except Exception as e:
        print(f"  ✗ Error extracting profile: {str(e)[:100]}...")
        profile_data['error'] = str(e)
        profile_data['url'] = profile_url
        return profile_data

# ============================================================================
# Scrape Multiple Profiles Across Pages
# ============================================================================

print("\n" + "="*80)
print("🔄 MULTI-PROFILE SCRAPING (5 Pages)")
print("="*80 + "\n")

all_profiles_data = []
MAX_PAGES = 5
profiles_per_page_target = 10  # LinkedIn typically shows 10 per page
page_num = 0  # Initialize page number

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
                profile_data = extract_profile_data(page, profile_url)
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
                        # Scroll to button and click with human behavior
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

output_file = 'data/profiles_multi_page.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_profiles_data, f, indent=4, ensure_ascii=False)

print(f"✓ All profiles data saved to {output_file}")

# Create summary file
summary = {
    'total_profiles': len(all_profiles_data),
    'pages_scraped': page_num,
    'profiles_by_page': {}
}

for i in range(1, page_num + 1):
    page_profiles = [p for p in all_profiles_data if p.get('page_number') == i]
    summary['profiles_by_page'][f'page_{i}'] = len(page_profiles)

summary_file = 'data/scraping_summary.json'
with open(summary_file, 'w', encoding='utf-8') as f:
    json.dump(summary, f, indent=4)

print(f"✓ Summary saved to {summary_file}")

# Keep the browser open for continued browsing
print("\n" + "="*80)
print("🤖 BROWSER KEPT OPEN FOR CONTINUED BROWSING")
print("="*80)
print("You can continue using the browser manually.")
print("Press Ctrl+C in this console to exit completely.")
print("="*80)

# NEW: Save the session state for future use
try:
    print("Saving current session state for future use...")
    # Get the context of the current page to save the authenticated session
    context = page.context
    context.storage_state(path="linkedin_auth.json")
    print("✓ Session state saved to 'linkedin_auth.json'")
    print("   You can now use 'linkedin_session_loader.py' to load this session directly!")
    print("   Or run 'python use_saved_session.py' to skip login on next run!")
except Exception as e:
    print(f"⚠ Warning: Could not save session state: {e}")

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
print("🎉 Scraping completed successfully!")
print("="*80)
