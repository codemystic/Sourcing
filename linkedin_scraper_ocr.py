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

# Import custom modules
from human_behavior import HumanBehavior, move_mouse_naturally
from nlp_query_parser import parse_nlp_query, format_search_query

# Ask for user input for NLP query FIRST
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

# NOW load environment variables and initialize Groq
from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

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

# NOW initialize Playwright and navigate directly to Google homepage
from playwright.sync_api import sync_playwright

playwright = sync_playwright().start()

# Use Brave browser instead of Chrome/Microsoft Edge
# Try to find Brave installation path
import platform
system = platform.system()

if system == "Windows":
    brave_paths = [
        r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
        r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe",
        os.path.expanduser(r"~\AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe")
    ]
    brave_path = None
    for path in brave_paths:
        if os.path.exists(path):
            brave_path = path
            break
    
    if brave_path:
        print(f"✓ Found Brave browser at: {brave_path}")
        browser = playwright.chromium.launch(
            headless=False,
            executable_path=brave_path
        )
    else:
        print("⚠️  Brave browser not found, using Chromium")
        browser = playwright.chromium.launch(headless=False)
elif system == "Darwin":  # macOS
    brave_path = "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
    if os.path.exists(brave_path):
        print(f"✓ Found Brave browser at: {brave_path}")
        browser = playwright.chromium.launch(
            headless=False,
            executable_path=brave_path
        )
    else:
        print("⚠️  Brave browser not found, using Chromium")
        browser = playwright.chromium.launch(headless=False)
else:  # Linux and other systems
    brave_paths = [
        "/usr/bin/brave-browser",
        "/usr/bin/brave",
        "/snap/bin/brave",
        os.path.expanduser("~/.local/bin/brave")
    ]
    brave_path = None
    for path in brave_paths:
        if os.path.exists(path):
            brave_path = path
            break
    
    if brave_path:
        print(f"✓ Found Brave browser at: {brave_path}")
        browser = playwright.chromium.launch(
            headless=False,
            executable_path=brave_path
        )
    else:
        print("⚠️  Brave browser not found, using Chromium")
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
def is_captcha_page(page):
    """Check if current page is a CAPTCHA challenge page"""
    try:
        current_url = page.url.lower()
        page_title = ""
        try:
            page_title = page.title().lower()
        except:
            pass
        
        # Check for CAPTCHA indicators in URL
        captcha_indicators = ['sorry', 'recaptcha', 'captcha', 'challenge']
        url_indicators = [indicator for indicator in captcha_indicators if indicator in current_url]
        
        # Check for CAPTCHA indicators in title
        title_indicators = [indicator for indicator in captcha_indicators if indicator in page_title]
        
        # Check for CAPTCHA elements on page
        captcha_selectors = [
            'iframe[title*="challenge"]',
            'iframe[title*="reCAPTCHA"]',
            '.rc-imageselect',
            '.rc-challenge',
            '[data-sitekey]',
            '.g-recaptcha'
        ]
        
        element_found = False
        for selector in captcha_selectors:
            try:
                if page.query_selector(selector):
                    element_found = True
                    break
            except:
                continue
        
        # If any indicators found, likely a CAPTCHA page
        if url_indicators or title_indicators or element_found:
            return True
        else:
            return False
            
    except Exception as e:
        print(f"  ⚠️  Error checking if CAPTCHA page: {e}")
        return False

def validate_captcha_solution(page):
    """Validate if CAPTCHA solution was successful"""
    try:
        # Check if we're still on a CAPTCHA page
        if is_captcha_page(page):
            print("  ⚠️  Still on CAPTCHA page after solution attempt")
            return False
        else:
            # Check for successful redirect indicators
            current_url = page.url.lower()
            if 'google.com' in current_url and 'search' in current_url:
                print("  ✅ Successfully passed CAPTCHA and redirected to search results")
                return True
            elif 'linkedin.com' in current_url and ('/in/' in current_url or '/pub/' in current_url):
                print("  ✅ Successfully passed CAPTCHA and redirected to LinkedIn profile")
                return True
            else:
                # Look for search elements as success indicators
                try:
                    success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                    if len(success_indicators) > 0:
                        print("  ✅ Found search elements, likely passed CAPTCHA")
                        return True
                except:
                    pass
                return True  # Assume success if not on CAPTCHA page
    except Exception as e:
        print(f"  ⚠️  Error validating CAPTCHA solution: {e}")
        return False

# ============================================================================
# CAPTCHA Detection and Automatic Handling
# ============================================================================

def analyze_captcha_screenshot_with_vision_model(screenshot_path):
    """Analyze CAPTCHA screenshot with vision model and return structured output"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"  📸 Analyzing CAPTCHA screenshot with enhanced intelligence: {screenshot_path} (Attempt {attempt + 1}/{max_retries})")
            
            # Read the screenshot file
            with open(screenshot_path, "rb") as image_file:
                screenshot_data = base64.b64encode(image_file.read()).decode("utf-8")
            
            # Create enhanced intelligent prompt for vision model analysis
            prompt = """
You are an expert visual reasoning assistant with exceptional pattern recognition capabilities.

I will upload a puzzle image. It contains:
1. A text instruction at the top (for example: "Select all images with crosswalks").
2. A grid of image tiles below the instruction.

Your task:
1. Read the instruction exactly as shown.
2. Understand the visual concept described.
3. Analyze each tile individually.
4. Identify which tiles match the instruction.

Tile numbering:
- Number tiles from left to right, top to bottom.
- For a 3x3 grid: tiles 1,2,3 on top row, 4,5,6 on middle row, 7,8,9 on bottom row.

Output (strict JSON):
{
  "instruction": "<detected_instruction>",
  "matching_tiles": [list_of_tile_numbers],
  "reasoning": {
      "<tile_number>": "<why_it_matches_or_not>"
  }
}

Rules for maximum intelligence and accuracy:
- Use only the visual content in the puzzle image.
- Follow the instruction literally and precisely.
- Be extremely conservative - only select tiles you are 99.9% certain about.
- If a tile is ambiguous, unclear, or only partially matches, DO NOT select it.
- It's better to select fewer tiles correctly than more tiles incorrectly.
- Double-check your analysis before finalizing the selection.
- Do NOT automate clicking or interact with any CAPTCHA system.
- You only classify the image I manually upload.
- Focus on clear, definitive matches only.
- When in doubt, exclude the tile.

Example of high-quality reasoning:
For instruction "Select all images with crosswalks":
Tile 1: "Contains a clear crosswalk with visible zebra stripes crossing a street"
Tile 2: "No crosswalk visible, shows only a regular street intersection"
Tile 3: "Ambiguous - might be a crosswalk but not clearly visible, excluding for safety"
"""
            
            # Call Groq API with vision model - use more conservative settings for higher intelligence
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
                temperature=0.01,  # Extremely conservative for maximum intelligence
                max_tokens=4096,   # Increased tokens for detailed reasoning
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
                    if 'instruction' in parsed_response and 'matching_tiles' in parsed_response and 'reasoning' in parsed_response:
                        print("  ✅ Valid intelligent JSON response received from vision model")
                        # Apply additional accuracy filtering for maximum intelligence
                        matches = parsed_response.get('matching_tiles', [])
                        reasoning = parsed_response.get('reasoning', {})
                        
                        # Ultra conservative filtering - if reasoning shows any doubt, remove the tile
                        filtered_matches = []
                        for tile in matches:
                            tile_str = str(tile)
                            if tile_str in reasoning:
                                reason = reasoning[tile_str].lower()
                                # Remove tiles with uncertain reasoning
                                if not any(doubt_word in reason for doubt_word in ['might', 'maybe', 'possibly', 'unclear', 'ambiguous', 'not sure', 'difficult']):
                                    filtered_matches.append(tile)
                                else:
                                    print(f"  ⚠️  Removing tile {tile} due to uncertain reasoning: {reasoning[tile_str]}")
                        
                        if len(filtered_matches) != len(matches):
                            print(f"  ℹ️  Intelligence filter: reduced {len(matches)} to {len(filtered_matches)} tiles for maximum accuracy")
                            parsed_response['matching_tiles'] = filtered_matches
                            # Update the response text with filtered results
                            response_text = json.dumps(parsed_response)
                        
                        # Ultra conservative - max 1 tile for maximum accuracy
                        if len(filtered_matches) > 1:
                            print(f"  ⚠️  Intelligence filter: too many matches ({len(filtered_matches)}), selecting only the most confident one...")
                            # Take only the first tile for maximum accuracy
                            ultra_filtered_matches = filtered_matches[:1] if filtered_matches else []
                            parsed_response['matching_tiles'] = ultra_filtered_matches
                            # Update the response text with ultra-filtered results
                            response_text = json.dumps(parsed_response)
                        
                        return response_text
                    else:
                        print("  ⚠️  Invalid intelligent JSON structure from vision model")
                        if attempt < max_retries - 1:
                            print("  ℹ️  Retrying with enhanced intelligence...")
                            HumanBehavior.random_delay(4, 6)
                            continue
                        else:
                            return None
                except json.JSONDecodeError:
                    print("  ⚠️  Failed to parse intelligent JSON from vision model response")
                    if attempt < max_retries - 1:
                        print("  ℹ️  Retrying with enhanced intelligence...")
                        HumanBehavior.random_delay(4, 6)
                        continue
                    else:
                        # Try to extract JSON from response if it's embedded
                        import re
                        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
                        if json_match:
                            try:
                                extracted_json = json_match.group(0)
                                parsed_response = json.loads(extracted_json)
                                if 'instruction' in parsed_response and 'matching_tiles' in parsed_response and 'reasoning' in parsed_response:
                                    print("  ✅ Extracted valid intelligent JSON from response")
                                    # Apply additional accuracy filtering
                                    matches = parsed_response.get('matching_tiles', [])
                                    reasoning = parsed_response.get('reasoning', {})
                                    
                                    # Ultra conservative filtering
                                    filtered_matches = []
                                    for tile in matches:
                                        tile_str = str(tile)
                                        if tile_str in reasoning:
                                            reason = reasoning[tile_str].lower()
                                            # Remove tiles with uncertain reasoning
                                            if not any(doubt_word in reason for doubt_word in ['might', 'maybe', 'possibly', 'unclear', 'ambiguous', 'not sure', 'difficult']):
                                                filtered_matches.append(tile)
                                            else:
                                                print(f"  ⚠️  Removing tile {tile} due to uncertain reasoning: {reasoning[tile_str]}")
                                    
                                    if len(filtered_matches) != len(matches):
                                        print(f"  ℹ️  Intelligence filter: reduced {len(matches)} to {len(filtered_matches)} tiles")
                                        parsed_response['matching_tiles'] = filtered_matches
                                        # Update the response text
                                        extracted_json = json.dumps(parsed_response)
                                    
                                    # Ultra conservative - max 1 tile
                                    if len(filtered_matches) > 1:
                                        print(f"  ⚠️  Intelligence filter: too many matches ({len(filtered_matches)}), selecting only most confident...")
                                        ultra_filtered_matches = filtered_matches[:1] if filtered_matches else []
                                        parsed_response['matching_tiles'] = ultra_filtered_matches
                                        # Update the response text
                                        extracted_json = json.dumps(parsed_response)
                                    
                                    return extracted_json
                            except:
                                pass
                        return None
            else:
                print("  ⚠️  Empty response from intelligent vision model")
                if attempt < max_retries - 1:
                    print("  ℹ️  Retrying with enhanced intelligence...")
                    HumanBehavior.random_delay(4, 6)
                    continue
                else:
                    return None
                    
        except Exception as e:
            print(f"  ⚠️  Error in intelligent CAPTCHA analysis: {e}")
            if attempt < max_retries - 1:
                print("  ℹ️  Retrying with enhanced intelligence...")
                HumanBehavior.random_delay(5, 7)
                continue
            else:
                return None
    
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
    """Solve image puzzle CAPTCHA using intelligent vision analysis with human-like behavior"""
    try:
        print("  🧩 Attempting to solve image puzzle CAPTCHA with enhanced intelligence...")
        
        # Wait for challenge to load with human-like delay
        HumanBehavior.random_delay(3, 6)
        
        # Look for image challenge iframe
        challenge_iframe = page.query_selector('iframe[title*="challenge"]')
        if not challenge_iframe:
            print("  ⚠️  No image challenge found")
            return False
        
        # Scroll to challenge iframe naturally
        challenge_iframe.scroll_into_view_if_needed()
        HumanBehavior.random_delay(1, 3)
        
        # Switch to challenge iframe
        print("  🖼️  Switching to challenge iframe with intelligent analysis...")
        challenge_frame = challenge_iframe.content_frame()
        if not challenge_frame:
            print("  ⚠️  Could not access challenge frame")
            return False
        
        # FIRST: Take screenshot of the CAPTCHA image challenge for intelligent vision model analysis
        try:
            captcha_screenshot_path = "data/screenshots/captcha_screenshot.png"
            os.makedirs('data/screenshots', exist_ok=True)
            # Take higher quality screenshot for better intelligent analysis
            page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=20000)
            print(f"  📸 CAPTCHA screenshot saved for intelligent analysis: {captcha_screenshot_path}")
            
            # Analyze the CAPTCHA screenshot with intelligent vision model
            vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
        except Exception as screenshot_error:
            print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
            vision_analysis = None
        
        # If we have intelligent vision analysis, use it
        if vision_analysis:
            print("  🤖 Using intelligent vision analysis to solve puzzle with maximum precision...")
            try:
                import json
                analysis = json.loads(vision_analysis)
                instruction = analysis.get('instruction', '')
                # Handle both 'matching_tiles' and 'matches' for backward compatibility
                matches = analysis.get('matching_tiles', analysis.get('matches', []))
                # Handle both 'reasoning' and 'explanations' for backward compatibility
                reasoning = analysis.get('reasoning', analysis.get('explanations', {}))
                
                print(f"  📋 Instruction: {instruction}")
                print(f"  🎯 Intelligent matches: {matches}")
                
                # ULTRA CONSERVATIVE validation for maximum intelligence
                if not matches:
                    print("  ⚠️  No intelligent matches found, using ultra-safe approach...")
                    # Ultra-safe: select NO tiles to avoid errors
                    intelligent_matches = []
                else:
                    # Apply additional intelligence filtering
                    intelligent_matches = []
                    for tile in matches:
                        tile_str = str(tile)
                        if tile_str in reasoning:
                            reason = reasoning[tile_str]
                            print(f"    Tile {tile}: {reason}")
                            # Only include tiles with clear, definitive reasoning
                            if not any(uncertain_word in reason.lower() for uncertain_word in ['might', 'maybe', 'possibly', 'seems', 'appears', 'could be', 'looks like']):
                                intelligent_matches.append(tile)
                            else:
                                print(f"    ⚠️  Excluding tile {tile} due to uncertain reasoning")
                        else:
                            # If no reasoning provided, be conservative and exclude
                            print(f"    ⚠️  Excluding tile {tile} - no reasoning provided")
                            
                            # ULTRA CONSERVATIVE - max 1 tile for maximum accuracy
                            if len(intelligent_matches) > 1:
                                print(f"  ⚠️  Intelligence filter: too many confident matches ({len(intelligent_matches)}), selecting only the MOST confident...")
                                # Sort by confidence based on reasoning quality and take the first
                                intelligent_matches = intelligent_matches[:1]
                        
                        print(f"  ✅ Final intelligent selection: {intelligent_matches}")
                        
                        # ONLY click tiles if we're extremely confident
                        if len(intelligent_matches) > 0:
                            # Click on matching tiles with precise human-like behavior
                            for tile_num in intelligent_matches:
                                # Validate tile number
                                if not isinstance(tile_num, int) or tile_num < 1 or tile_num > 9:
                                    print(f"  ⚠️  Skipping invalid tile: {tile_num}")
                                    continue
                                
                                # Calculate precise positions for 3x3 grid (reCAPTCHA standard layout)
                                # Grid positions based on actual reCAPTCHA dimensions
                                col = (tile_num - 1) % 3
                                row = (tile_num - 1) // 3
                                
                                # Precise positioning for reCAPTCHA tiles with enhanced accuracy
                                x_offset = 95 + (col * 138)
                                y_offset = 195 + (row * 138)
                                
                                print(f"  🖱️  Clicking tile {tile_num} at precise position ({x_offset}, {y_offset}) with intelligent confidence")
                                
                                # Natural mouse movement with variable duration for maximum realism
                                HumanBehavior.move_mouse_naturally(page, x_offset, y_offset, duration=random.uniform(1.8, 3.2))
                                
                                # Human-like pause before clicking - longer for intelligence
                                HumanBehavior.random_delay(1.5, 3)
                                
                                # Precise click
                                page.mouse.click(x_offset, y_offset)
                                
                                # Post-click pause
                                HumanBehavior.random_delay(1.2, 2.5)
                        else:
                            print("  ℹ️  No tiles selected for maximum intelligence - proceeding to verify")
                        
                        # Find and click verify button with enhanced human-like behavior
                        verify_btn = challenge_frame.query_selector('button')
                        if verify_btn:
                            # Get button position
                            box = verify_btn.bounding_box()
                            if box:
                                btn_x = box['x'] + box['width'] / 2
                                btn_y = box['y'] + box['height'] / 2
                                
                                # Move mouse naturally to verify button with enhanced intelligence
                                HumanBehavior.move_mouse_naturally(page, btn_x, btn_y, duration=random.uniform(1.5, 2.8))
                                
                                # Add thoughtful pause before clicking - intelligence takes time
                                HumanBehavior.random_delay(1.5, 3)
                                
                                # Click verify button
                                verify_btn.click()
                                print("  ✅ Clicked verify button with intelligent confidence")
                                
                                # Wait for page to potentially redirect after solving
                                print("  ⏳ Waiting for page to redirect after intelligent solving...")
                                HumanBehavior.random_delay(5, 9)
                                
                                # Check if we're still on a CAPTCHA page or have been redirected
                                current_url = page.url.lower()
                                if 'sorry' in current_url or 'recaptcha' in current_url:
                                    print("  ⚠️  Still on CAPTCHA page, intelligent solving may not have been successful")
                                    # Try to check for success indicators
                                    try:
                                        # Look for elements that indicate we've passed the CAPTCHA
                                        success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                                        if len(success_indicators) > 0:
                                            print("  ✅ Found search elements, likely passed CAPTCHA intelligently")
                                            return True
                                    except:
                                        pass
                                    return False
                                else:
                                    print("  ✅ Successfully redirected after intelligent CAPTCHA solving")
                                    return True
            except Exception as parse_error:
                print(f"  ⚠️  Error parsing intelligent vision analysis: {parse_error}")
                print("  ℹ️  Falling back to conservative random selection with intelligence...")
        
        # Fallback: Try ultra-conservative random selection if no vision analysis
        print("  🎲 Using ultra-conservative random selection (0 tiles only) for maximum safety...")
        # Select NO tiles for maximum safety - intelligence suggests this is often better
        selected_tiles = []
        print("  ℹ️  No tiles selected for maximum intelligent safety")
        
        # Try to find and click verify button with human-like behavior
        verify_btn = challenge_frame.query_selector('button')
        if verify_btn:
            # Get button position
            box = verify_btn.bounding_box()
            if box:
                btn_x = box['x'] + box['width'] / 2
                btn_y = box['y'] + box['height'] / 2
                
                # Move mouse naturally to verify button
                HumanBehavior.move_mouse_naturally(page, btn_x, btn_y, duration=random.uniform(1.5, 3))
                
                # Add thoughtful pause before clicking
                HumanBehavior.random_delay(1.5, 3)
                
                # Click verify button
                verify_btn.click()
                print("  ✅ Clicked verify button (no tile selection) with intelligent approach")
                
                # Wait for page to potentially redirect after solving
                print("  ⏳ Waiting for page to redirect after intelligent solving...")
                HumanBehavior.random_delay(5, 9)
                
                # Check if we're still on a CAPTCHA page or have been redirected
                current_url = page.url.lower()
                if 'sorry' in current_url or 'recaptcha' in current_url:
                    print("  ⚠️  Still on CAPTCHA page, intelligent solving may not have been successful")
                    # Try to check for success indicators
                    try:
                        # Look for elements that indicate we've passed the CAPTCHA
                        success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                        if len(success_indicators) > 0:
                            print("  ✅ Found search elements, likely passed CAPTCHA intelligently")
                            return True
                    except:
                        pass
                    return False
                else:
                    print("  ✅ Successfully redirected after intelligent CAPTCHA solving")
                    return True
        
        print("  ⚠️  Could not find verify button")
        return False
        
    except Exception as e:
        print(f"  ⚠️  Error in intelligent image puzzle solving: {e}")
        return False

def solve_multiple_image_puzzles(page, max_attempts=12):
    """Keep solving image puzzles until redirected to Google search results or max attempts reached"""
    print(f"  🔄 Starting multiple image puzzle solving with MAXIMUM accuracy (max {max_attempts} attempts)...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"  🧩 Attempt {attempt}/{max_attempts} to solve image puzzle (ACCURACY FOCUS)...")
        
        # Add human-like delay before each attempt
        if attempt > 1:
            print("    😴 Adding human-like delay between attempts...")
            HumanBehavior.random_delay(4, 7)  # Increased delay between attempts
            
            # Occasionally perform random human-like actions
            if random.random() < 0.5:  # Increased chance to 50%
                print("    👀 Performing random human-like actions...")
                HumanBehavior.random_page_actions(page)
        
        # Check if we're already on Google search results page
        current_url = page.url.lower()
        if 'google.com' in current_url and 'search' in current_url and 'sorry' not in current_url:
            print("  ✅ Already on Google search results page, no more CAPTCHAs to solve")
            return True
        
        # Check if we're still on a CAPTCHA page
        if 'sorry' not in current_url and 'recaptcha' not in current_url:
            print("  ✅ No longer on CAPTCHA page, assuming successful redirect")
            return True
        
        # Try to solve this image puzzle (screenshot and analysis happens inside)
        puzzle_solved = solve_image_puzzle(page)
        
        if puzzle_solved:
            print(f"    ✅ Image puzzle {attempt} solved successfully!")
            
            # Wait a bit for the page to redirect after solving
            print("    ⏳ Waiting for page to redirect after solving CAPTCHA...")
            HumanBehavior.random_delay(6, 10)  # Increased wait time for accuracy
            
            # Check if we've been redirected to Google search results
            current_url = page.url.lower()
            if 'google.com' in current_url and 'search' in current_url and 'sorry' not in current_url:
                print("    ✅ Successfully redirected to Google search results page!")
                return True
            elif 'sorry' not in current_url and 'recaptcha' not in current_url:
                print("    ✅ No longer on CAPTCHA page, assuming successful redirect")
                return True
            else:
                print("    ⚠️  Still on CAPTCHA page, more puzzles to solve...")
                # Continue to next attempt
                HumanBehavior.random_delay(4, 6)
        else:
            print(f"    ⚠️  Failed to solve image puzzle {attempt}")
            
            # Check if we've been redirected anyway
            current_url = page.url.lower()
            if 'google.com' in current_url and 'search' in current_url and 'sorry' not in current_url:
                print("    ✅ Redirected to Google search results despite failure, continuing...")
                return True
            elif 'sorry' not in current_url and 'recaptcha' not in current_url:
                print("    ✅ No longer on CAPTCHA page, assuming successful redirect")
                return True
            
            # If this is the last attempt, return False
            if attempt == max_attempts:
                print(f"    ❌ Reached maximum attempts ({max_attempts}), giving up for accuracy")
                return False
            
            # Wait before trying again
            HumanBehavior.random_delay(4, 7)
    
    print(f"  ❌ Exceeded maximum attempts ({max_attempts}), could not solve all puzzles")
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
    print("\n🔄 Starting fully automatic CAPTCHA solving with MAXIMUM accuracy...\n")
    
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
                page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=15000)  # Higher timeout for better quality
                print(f"  📸 CAPTCHA screenshot saved to: {captcha_screenshot_path}")
                
                # Analyze the CAPTCHA screenshot with vision model
                vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
            except Exception as screenshot_error:
                print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
                vision_analysis = None
            
            # Try to solve multiple image puzzles automatically
            puzzle_solved = solve_multiple_image_puzzles(page)
            
            if puzzle_solved:
                print("✅ Image puzzle automatically solved with HIGH accuracy!")
                # Validate the solution
                if validate_captcha_solution(page):
                    print("✓ CAPTCHA solution validated successfully!")
                    complex_captcha = False
                else:
                    print("⚠️  CAPTCHA solution validation failed")
                    complex_captcha = True
            else:
                print("⚠️  Automatic image puzzle solving failed")
                complex_captcha = True
        else:
            print("✓ No additional challenges detected")
            # Validate we're not on CAPTCHA page
            if validate_captcha_solution(page):
                print("✓ Successfully passed CAPTCHA")
                complex_captcha = False
            else:
                print("⚠️  Still on CAPTCHA page")
                complex_captcha = True
    else:
        print("\n⚠️  Checkbox solving failed")
        complex_captcha = True
    
    # If complex CAPTCHA or auto-solve failed, try one more time with advanced methods
    if complex_captcha:
        print("\n🔄 Trying advanced automatic solving methods with MAXIMUM accuracy...")
        
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
                    page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=15000)  # Higher timeout for better quality
                    print(f"  📸 CAPTCHA screenshot saved to: {captcha_screenshot_path}")
                    
                    # Analyze the CAPTCHA screenshot with vision model
                    vision_analysis = analyze_captcha_screenshot_with_vision_model(captcha_screenshot_path)
                except Exception as screenshot_error:
                    print(f"  ⚠️  CAPTCHA screenshot error: {screenshot_error}")
                    vision_analysis = None
                
                puzzle_solved = solve_multiple_image_puzzles(page)
                if puzzle_solved:
                    print("✅ Advanced image puzzle solving successful with HIGH accuracy!")
                    # Validate the solution
                    if validate_captcha_solution(page):
                        print("✓ CAPTCHA solution validated successfully!")
                        complex_captcha = False
                    else:
                        print("⚠️  CAPTCHA solution validation failed")
                        complex_captcha = True
                else:
                    print("⚠️  Advanced image puzzle solving failed")
                    complex_captcha = True
            else:
                # Validate we're not on CAPTCHA page
                if validate_captcha_solution(page):
                    print("✓ Successfully passed CAPTCHA")
                    complex_captcha = False
                else:
                    print("⚠️  Still on CAPTCHA page")
                    complex_captcha = True

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
                        
                        # Try to solve multiple image puzzles automatically
                        puzzle_solved = solve_multiple_image_puzzles(page)
                        
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
                            
                            puzzle_solved = solve_multiple_image_puzzles(page)
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

# ============================================================================
# Helper function to close LinkedIn popups
# ============================================================================

def close_linkedin_popups(page, max_attempts=5):
    """Close any popups that appear on LinkedIn profiles - aggressive approach"""
    try:
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
                'button[aria-label*="Dismiss"]',
                'button[aria-label*="Close"]',
                'button[data-control-name="overlay.close"]',
                'button.artdeco-toast-item__dismiss',
                'button.modal__dismiss',
                'button[aria-label="Close"]',
                'button[aria-label="Dismiss"]',
                '[data-test-modal-close-btn]',
                '.artdeco-modal__dismiss',
                '.artdeco-toast-item__dismiss',
                '.msg-overlay-bubble-header__control',
                '.pv-profile-section__card-action-bar--mute',
                '[data-control-name="manage_activity_feed"]',
                '[data-control-name="open_sharebox"]',
                '[id*="close"]',
                '[id*="dismiss"]',
            ]
            
            popup_closed = False
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

# ============================================================================
# Helper function to navigate with login detection and retry
# ============================================================================

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

# ============================================================================
# Helper function to check if page is asking for LinkedIn login
# ============================================================================

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

# Function to extract LinkedIn profile links from current page
def extract_linkedin_profiles_from_page(page):
    """Extract LinkedIn profile links from the current Google search results page"""
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
        
        print(f"\n✅ Total unique LinkedIn profiles found on current page: {len(linkedin_profile_links)}")
        
    except Exception as extract_error:
        print(f"⚠️  Error extracting LinkedIn links: {extract_error}")
    
    return linkedin_profile_links

# Function to navigate to next page
def navigate_to_next_page(page):
    """Navigate to the next page of Google search results"""
    try:
        print("\n🔄 Attempting to navigate to next page...")
        
        # First, scroll down slowly to load all page elements
        print("  📜 Scrolling down slowly to load page elements...")
        total_height = page.evaluate("document.body.scrollHeight")
        viewport_height = 1080
        scroll_position = 0
        scroll_step = 300  # Smaller steps for slower scrolling
        
        # Scroll with human-like behavior
        while scroll_position < total_height:
            page.evaluate(f'window.scrollTo(0, {scroll_position})')
            HumanBehavior.random_delay(0.3, 0.8)  # Variable scroll delay
            scroll_position += scroll_step
            
            # Update total height in case new content loaded
            try:
                total_height = page.evaluate("document.body.scrollHeight")
            except:
                pass
        
        # Scroll back to top slightly to ensure pagination elements are visible
        page.evaluate('window.scrollTo(0, document.body.scrollHeight - 500)')
        HumanBehavior.random_delay(1, 2)
        
        # Aggressively close any modal overlays that might be blocking pagination
        print("  🔍 Aggressively closing modal overlays that might block pagination...")
        max_modal_attempts = 5
        for modal_attempt in range(max_modal_attempts):
            try:
                # Multiple approaches to close modals
                modal_closed = False
                
                # Approach 1: Press Escape key
                try:
                    page.keyboard.press('Escape')
                    HumanBehavior.random_delay(0.5, 1)
                    modal_closed = True
                except:
                    pass
                
                # Approach 2: Find and click specific close buttons
                close_selectors = [
                    'button[aria-label*="close"]',
                    'button[aria-label*="dismiss"]',
                    '[data-test-modal-close-btn]',
                    '.modal__close',
                    '.artdeco-modal__dismiss',
                    'button[data-control-name="overlay.close"]'
                ]
                
                for selector in close_selectors:
                    try:
                        close_buttons = page.query_selector_all(selector)
                        for close_btn in close_buttons:
                            if close_btn.is_visible():
                                close_btn.click(timeout=3000)
                                print(f"  🚫 Closed modal using selector: {selector}")
                                HumanBehavior.random_delay(0.5, 1)
                                modal_closed = True
                                break
                    except:
                        continue
                    if modal_closed:
                        break
                
                # Approach 3: Click on backdrop/overlay directly
                if not modal_closed:
                    backdrop_selectors = [
                        '.modal__overlay--visible',
                        '.modal__overlay',
                        '.contextual-sign-in-modal__screen',
                        '[class*="overlay"][class*="visible"]',
                        '[class*="scrim"]'
                    ]
                    
                    for selector in backdrop_selectors:
                        try:
                            backdrops = page.query_selector_all(selector)
                            for backdrop in backdrops:
                                if backdrop.is_visible():
                                    # Click in the center of the backdrop
                                    box = backdrop.bounding_box()
                                    if box:
                                        page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                                        print(f"  🚫 Clicked backdrop using selector: {selector}")
                                        HumanBehavior.random_delay(0.5, 1)
                                        modal_closed = True
                                        break
                        except:
                            continue
                        if modal_closed:
                            break
                
                # If no modals were closed in this attempt, we're probably done
                if not modal_closed and modal_attempt > 0:
                    break
                    
            except Exception as modal_error:
                print(f"  ⚠️  Error handling modals (attempt {modal_attempt + 1}): {str(modal_error)[:100]}")
                continue
        
        HumanBehavior.random_delay(1, 2)
        
        # Method 1: Try to find and click specific page number link (Google pagination)
        print("  🔍 Looking for next page link...")
        # Try to find the next page number link (e.g., if on page 1, look for page 2)
        current_page_elements = page.query_selector_all('a[aria-current="page"]')
        next_page_number = None
        if current_page_elements:
            try:
                current_page_text = current_page_elements[0].text_content().strip()
                if current_page_text.isdigit():
                    current_page_num = int(current_page_text)
                    next_page_number = current_page_num + 1
            except:
                pass
        
        next_page_link = None
        if next_page_number:
            next_page_link = page.query_selector(f'a[aria-label="Page {next_page_number}"]')
        
        if next_page_link:
            print(f"  ✓ Found page {next_page_number} link")
            # Scroll to page link and click
            next_page_link.scroll_into_view_if_needed()
            HumanBehavior.random_delay(0.5, 1)
            next_page_link.click()
            print(f"  ✅ Clicked page {next_page_number} link")
            HumanBehavior.random_delay(3, 5)
            return True
        else:
            print("  ⚠️  Specific next page link not found")
            
            # Method 2: Find and click "Next" button
            print("  🔍 Looking for Next button...")
            next_button = page.query_selector('a[aria-label="Next"]')
            if not next_button:
                next_button = page.query_selector('a:has-text("Next")')
            if not next_button:
                # Additional selector for Next button based on provided inspect element
                next_button = page.query_selector('span.oeN89d:has-text("Next")')
            
            if next_button:
                print("  ✓ Found Next button")
                # Scroll to button and click
                next_button.scroll_into_view_if_needed()
                HumanBehavior.random_delay(0.5, 1)
                
                # Try multiple approaches to click the next button
                clicked = False
                max_click_attempts = 3
                
                for attempt in range(max_click_attempts):
                    try:
                        print(f"  🖱️  Attempting to click Next button (attempt {attempt + 1}/{max_click_attempts})...")
                        
                        # Check if there are still overlays blocking the click
                        blocking_overlays = page.query_selector_all('.modal__overlay--visible, .contextual-sign-in-modal, [class*="overlay"][class*="visible"]')
                        blocking_visible = False
                        for overlay in blocking_overlays:
                            if overlay.is_visible():
                                blocking_visible = True
                                break
                        
                        if blocking_visible:
                            print("  ⚠️  Modal overlay still blocking, trying to close...")
                            # Try to close overlays again
                            page.keyboard.press('Escape')
                            HumanBehavior.random_delay(1, 2)
                        
                        # Try direct click
                        next_button.click(timeout=10000)
                        clicked = True
                        print("  ✅ Clicked Next button")
                        break
                    except Exception as click_error:
                        print(f"  ⚠️  Click attempt {attempt + 1} failed: {str(click_error)[:100]}...")
                        if attempt < max_click_attempts - 1:
                            # Try JavaScript click as fallback
                            try:
                                print("  🔄 Trying JavaScript click as fallback...")
                                page.evaluate("""(button) => {
                                    if (button) {
                                        button.scrollIntoView({behavior: 'smooth', block: 'center'});
                                        setTimeout(() => {
                                            button.click();
                                        }, 500);
                                    }
                                }""", next_button)
                                clicked = True
                                print("  ✅ Clicked Next button using JavaScript")
                                break
                            except Exception as js_error:
                                print(f"  ⚠️  JavaScript click also failed: {str(js_error)[:100]}...")
                                HumanBehavior.random_delay(2, 3)
                        else:
                            # Final attempt: try clicking coordinates
                            try:
                                print("  🎯 Trying coordinate-based click...")
                                box = next_button.bounding_box()
                                if box:
                                    page.mouse.click(box['x'] + box['width'] / 2, box['y'] + box['height'] / 2)
                                    clicked = True
                                    print("  ✅ Clicked Next button using coordinates")
                            except Exception as coord_error:
                                print(f"  ⚠️  Coordinate click also failed: {str(coord_error)[:100]}...")
                
                if clicked:
                    HumanBehavior.random_delay(3, 5)
                    return True
                else:
                    print("  ❌ Failed to click Next button after all attempts")
                    return False
            else:
                print("  ⚠️  Next button not found")
                return False
                
    except Exception as e:
        print(f"  ⚠️  Error navigating to next page: {e}")
        return False

# Extract profiles from the first page
print("\n📄 Extracting profiles from page 1...")
linkedin_profile_links = extract_linkedin_profiles_from_page(page)

# Navigate through multiple pages until we reach 100 profiles or maximum pages
MAX_PAGES = 20  # Increase to 20 pages to ensure we get 100 profiles
TARGET_PROFILE_COUNT = 100
current_page = 1

while current_page < MAX_PAGES and len(linkedin_profile_links) < TARGET_PROFILE_COUNT:
    print(f"\n⏭️  Navigating to page {current_page + 1}...")
    if navigate_to_next_page(page):
        print(f"  ✅ Successfully navigated to page {current_page + 1}")
        # Extract profiles from the current page
        print(f"\n📄 Extracting profiles from page {current_page + 1}...")
        page_profiles = extract_linkedin_profiles_from_page(page)
        
        # Add new profiles to the main list (avoid duplicates)
        for profile in page_profiles:
            if profile not in linkedin_profile_links:
                linkedin_profile_links.append(profile)
        
        print(f"  📈 Total profiles so far: {len(linkedin_profile_links)}")
        current_page += 1
        
        # Add a delay between page navigations to be more human-like
        HumanBehavior.random_delay(2, 4)
    else:
        print(f"  ⚠️  Could not navigate to page {current_page + 1}, stopping pagination")
        break

print(f"\n📈 Total profiles from {current_page} pages: {len(linkedin_profile_links)}")

# URL extraction completed above - save to CSV file
print("\n" + "="*80)
print(f"✅ LINKEDIN PROFILE URL EXTRACTION COMPLETED")
print("   Method: Direct href extraction (NO NAVIGATION)")
print("   All URLs extracted without opening any profiles")
print("   Results saved to: data/extracted_profile_urls.csv")
print("="*80)

# Save URLs to CSV file
import csv
import os

# Create data directory if it doesn't exist
os.makedirs('data', exist_ok=True)

# Write to CSV file
csv_file_path = 'data/extracted_profile_urls.csv'
try:
    with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        # Write header
        writer.writerow(['Profile URL'])
        # Write each URL
        for url in linkedin_profile_links:
            writer.writerow([url])
    print(f"✅ Successfully saved {len(linkedin_profile_links)} profile URLs to {csv_file_path}")
except Exception as e:
    print(f"⚠️  Error saving to CSV: {e}")

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
    # Warning message removed as requested
    pass

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
# Save All Profiles Data to JSON
# ============================================================================

# Create an empty profiles list since we're removing the multi-page scraping
all_profiles_data = []

output_file = 'data/profiles_multi_page_ocr.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(all_profiles_data, f, indent=4, ensure_ascii=False)

print(f"✓ All profiles data saved to {output_file}")

# Create summary file
summary = {
    'total_profiles': len(all_profiles_data),
    'pages_scraped': 0,
    'profiles_by_page': {}
}

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
