"""
Advanced CAPTCHA Solver with Automatic Image Puzzle Recognition
Provides fully automated CAPTCHA solving without manual intervention
"""

import base64
import io
import json
import random
import time
from typing import List, Dict, Any, Optional

from groq import Groq
from PIL import Image

class AdvancedCaptchaSolver:
    """Advanced CAPTCHA solver with automatic image puzzle recognition"""
    
    def __init__(self, groq_client: Groq):
        self.groq_client = groq_client
        self.target_objects = [
            'traffic light', 'crosswalk', 'vehicle', 'car', 'bus', 'bicycle',
            'motorcycle', 'bridge', 'stairs', 'chimney', 'fire hydrant',
            'parking meter', 'store front', 'mountain', 'palm tree',
            'boat', 'bicycle', 'airplane', 'train', 'truck', 'motorcycle',
            'bus', 'fire truck', 'ambulance', 'bicycle', 'scooter',
            'stop sign', 'yield sign', 'street sign', 'mailbox',
            'telephone booth', 'bench', 'fountain', 'statue', 'monument',
            'building', 'house', 'apartment', 'skyscraper', 'church',
            'castle', 'tent', 'windmill', 'water tower', 'lighthouse',
            'person', 'man', 'woman', 'child', 'people', 'group',
            'animal', 'dog', 'cat', 'bird', 'horse', 'cow', 'sheep',
            'elephant', 'bear', 'lion', 'tiger', 'zebra', 'giraffe'
        ]
    
    def solve_recaptcha_checkbox(self, page) -> bool:
        """Solve reCAPTCHA checkbox automatically with human-like behavior"""
        try:
            print("  🔄 Looking for reCAPTCHA checkbox...")
            time.sleep(2)
            
            # Find reCAPTCHA iframe
            recaptcha_iframe = page.query_selector('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]')
            
            if recaptcha_iframe:
                print("  ✓ Found reCAPTCHA iframe")
                
                # Get iframe bounding box for mouse movement
                bbox = recaptcha_iframe.bounding_box()
                if bbox:
                    # Calculate center of checkbox (approximate position in iframe)
                    checkbox_x = bbox['x'] + bbox['width'] / 2
                    checkbox_y = bbox['y'] + bbox['height'] / 2
                    
                    # Move mouse naturally to the interface first (3 seconds)
                    print("  👁️  Moving cursor around CAPTCHA interface (3 seconds)...")
                    
                    # Move to random position near CAPTCHA first
                    random_x = checkbox_x + random.uniform(-100, 100)
                    random_y = checkbox_y + random.uniform(-50, 50)
                    self._move_mouse_naturally(page, random_x, random_y, duration=1.5)
                    
                    # Hover around the area
                    time.sleep(0.5)
                    
                    # Then move to checkbox
                    print("  👁️  Moving to checkbox...")
                    self._move_mouse_naturally(page, checkbox_x, checkbox_y, duration=1.5)
                
                # Try a different approach - work directly with the iframe element
                try:
                    # Get iframe element handle
                    iframe_handle = recaptcha_iframe.element_handle()
                    if iframe_handle:
                        print("  ✓ Got iframe element handle")
                        
                        # Try to click the center of the iframe (where the checkbox typically is)
                        bbox = recaptcha_iframe.bounding_box()
                        if bbox:
                            # Calculate center position
                            center_x = bbox['x'] + bbox['width'] / 2
                            center_y = bbox['y'] + bbox['height'] / 2
                            
                            print(f"  🎯 Attempting click at iframe center ({center_x}, {center_y})")
                            page.mouse.click(center_x, center_y)
                            time.sleep(5)  # Wait for response
                            
                            # Check if click was successful by looking for changes
                            print("  ⏳ Waiting for verification...")
                            time.sleep(7)
                            
                            # Try to verify if checkbox was clicked
                            try:
                                # Check if we can find any elements that indicate success
                                page.wait_for_selector('iframe[title*="recaptcha challenge"]', timeout=5000)
                                print("  ✅ Detected image challenge - checkbox click successful!")
                                return True
                            except:
                                # If no image challenge, check for other indicators
                                current_url = page.url.lower()
                                if "checkpoint" in current_url or "challenge" in current_url:
                                    print("  ✅ Detected challenge page - checkbox click successful!")
                                    return True
                                
                                # Try JavaScript verification
                                try:
                                    js_verified = page.evaluate("""() => {
                                        // Look for elements that appear after successful checkbox click
                                        const challengeIframes = document.querySelectorAll('iframe[title*="challenge"]');
                                        const checkedBoxes = document.querySelectorAll('.recaptcha-checkbox-checked');
                                        return challengeIframes.length > 0 || checkedBoxes.length > 0;
                                    }""")
                                    
                                    if js_verified:
                                        print("  ✅ JavaScript verification indicates success!")
                                        return True
                                except:
                                    pass
                                
                                print("  ⚠️  Could not verify checkbox click success")
                                
                except Exception as iframe_error:
                    print(f"  ⚠️  Error working with iframe directly: {iframe_error}")
                
                # If direct iframe approach failed, try the frame locator approach with better error handling
                print("  🔄 Trying frame locator approach...")
                try:
                    # Use a more permissive approach to get the iframe content
                    iframe_element = page.frame_locator('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]').first
                    
                    # Try to find any clickable element within the iframe
                    potential_elements = [
                        '.recaptcha-checkbox-border',
                        '#recaptcha-anchor',
                        '[role="checkbox"]',
                        '.rc-anchor-checkbox-holder',
                        '.recaptcha-checkbox',
                        '[class*="checkbox"]',
                        'div',
                        'span'
                    ]
                    
                    element_found = False
                    for selector in potential_elements:
                        try:
                            elements = iframe_element.locator(selector).all()
                            if elements and len(elements) > 0:
                                print(f"  ✓ Found {len(elements)} elements with selector '{selector}'")
                                
                                # Try clicking the first element
                                try:
                                    elements[0].click(timeout=10000)
                                    print("  ✅ Clicked first element successfully")
                                    element_found = True
                                    break
                                except Exception as click_error:
                                    print(f"  ⚠️  Failed to click element with selector '{selector}': {click_error}")
                                    # Try alternative click methods
                                    try:
                                        bbox = elements[0].bounding_box(timeout=10000)
                                        if bbox:
                                            x = bbox['x'] + bbox['width'] / 2
                                            y = bbox['y'] + bbox['height'] / 2
                                            page.mouse.click(x, y)
                                            print("  ✅ Clicked via bounding box successfully")
                                            element_found = True
                                            break
                                    except Exception as bbox_error:
                                        print(f"  ⚠️  Failed to click via bounding box: {bbox_error}")
                        except Exception as selector_error:
                            # This is expected for many selectors, continue to next
                            continue
                    
                    if element_found:
                        print("  ⏳ Waiting for verification after element click...")
                        time.sleep(7)
                        
                        # Verify success
                        try:
                            page.wait_for_selector('iframe[title*="recaptcha challenge"]', timeout=5000)
                            print("  ✅ Detected image challenge - click successful!")
                            return True
                        except:
                            # Check URL for challenge
                            current_url = page.url.lower()
                            if "checkpoint" in current_url or "challenge" in current_url:
                                print("  ✅ Detected challenge page - click successful!")
                                return True
                            print("  ⚠️  Could not verify click success")
                    else:
                        print("  ⚠️  Could not find any clickable elements in iframe")
                        
                except Exception as frame_error:
                    print(f"  ⚠️  Error with frame locator approach: {frame_error}")
                
                # Last resort: Try to evaluate JavaScript directly on the iframe
                print("  🔄 Trying direct JavaScript evaluation on iframe...")
                try:
                    js_result = page.evaluate("""() => {
                        const iframes = document.querySelectorAll('iframe[title*="reCAPTCHA"], iframe[src*="recaptcha"]');
                        if (iframes.length > 0) {
                            const iframe = iframes[0];
                            try {
                                // Try to get the content document
                                const doc = iframe.contentDocument || (iframe.contentWindow && iframe.contentWindow.document);
                                if (doc) {
                                    // Look for checkbox elements
                                    const checkboxes = doc.querySelectorAll('.recaptcha-checkbox-border, #recaptcha-anchor, [role="checkbox"]');
                                    if (checkboxes.length > 0) {
                                        const checkbox = checkboxes[0];
                                        const rect = checkbox.getBoundingClientRect();
                                        const absRect = {
                                            x: rect.left + window.pageXOffset,
                                            y: rect.top + window.pageYOffset,
                                            width: rect.width,
                                            height: rect.height
                                        };
                                        return {
                                            element: 'checkbox',
                                            x: absRect.x + absRect.width / 2,
                                            y: absRect.y + absRect.height / 2
                                        };
                                    }
                                    // If no checkbox found, try clicking center of iframe
                                    const iframeRect = iframe.getBoundingClientRect();
                                    return {
                                        element: 'iframe_center',
                                        x: iframeRect.left + iframeRect.width / 2 + window.pageXOffset,
                                        y: iframeRect.top + iframeRect.height / 2 + window.pageYOffset
                                    };
                                }
                            } catch (e) {
                                // Cross-origin error, try clicking center of iframe
                                const iframeRect = iframe.getBoundingClientRect();
                                return {
                                    element: 'iframe_center',
                                    x: iframeRect.left + iframeRect.width / 2 + window.pageXOffset,
                                    y: iframeRect.top + iframeRect.height / 2 + window.pageYOffset
                                };
                            }
                        }
                        return null;
                    }""")
                    
                    if js_result:
                        print(f"  ✓ Found element via JavaScript: {js_result['element']} at ({js_result['x']}, {js_result['y']})")
                        # Click at the coordinates
                        page.mouse.click(js_result['x'], js_result['y'])
                        time.sleep(5)
                        print("  ✅ Clicked element via JavaScript coordinates")
                        
                        # Verify success
                        time.sleep(7)
                        try:
                            page.wait_for_selector('iframe[title*="recaptcha challenge"]', timeout=5000)
                            print("  ✅ Detected image challenge - JavaScript click successful!")
                            return True
                        except:
                            current_url = page.url.lower()
                            if "checkpoint" in current_url or "challenge" in current_url:
                                print("  ✅ Detected challenge page - JavaScript click successful!")
                                return True
                            print("  ⚠️  Could not verify JavaScript click success")
                    else:
                        print("  ⚠️  Could not find element via JavaScript")
                        
                except Exception as js_error:
                    print(f"  ⚠️  JavaScript evaluation failed: {js_error}")
                
                return False
            else:
                print("  ℹ️  No reCAPTCHA checkbox found")
                
                # Check if we're already past the CAPTCHA (maybe it auto-passed)
                current_url = page.url.lower()
                if '/feed' in current_url or '/in/' in current_url:
                    print("  ✅ Already on LinkedIn feed/profile - CAPTCHA may have auto-passed!")
                    return True
                
                return False
                
        except Exception as e:
            print(f"  ⚠️  Error solving reCAPTCHA checkbox: {e}")
            return False
        return False  # Default return
    
    def solve_image_puzzle(self, page) -> bool:
        """Solve reCAPTCHA image puzzle automatically using AI vision"""
        try:
            print("  🧾 Looking for image puzzle challenge...")
            time.sleep(2)
            
            # Check if image challenge iframe exists with retry logic
            max_retries = 3
            challenge_iframe = None
            for retry in range(max_retries):
                challenge_iframe = page.query_selector('iframe[title*="recaptcha challenge"]')
                if challenge_iframe:
                    break
                print(f"  ⚠️  Challenge iframe not found (attempt {retry + 1}/{max_retries})")
                if retry < max_retries - 1:
                    time.sleep(2)
            
            if not challenge_iframe:
                print("  ℹ️  No image challenge detected")
                return True  # No puzzle to solve
            
            print("  ✓ Image puzzle detected")
            
            # Get the challenge iframe with retry logic
            iframe = None
            for retry in range(max_retries):
                try:
                    iframe = page.frame_locator('iframe[title*="recaptcha challenge"]').first
                    if iframe:
                        break
                except Exception as e:
                    print(f"  ⚠️  Failed to get challenge iframe (attempt {retry + 1}/{max_retries}): {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)
            
            if not iframe:
                print("  ⚠️  Could not access challenge iframe after retries")
                return False
            
            # Wait for images to load
            time.sleep(2)
            
            # Get the challenge instruction text with retry logic
            instruction = "select matching images"
            for retry in range(max_retries):
                try:
                    instruction_element = iframe.locator('.rc-imageselect-desc-no-canonical, .rc-imageselect-desc')
                    if instruction_element.count() > 0:
                        instruction = instruction_element.text_content()
                        break
                except:
                    if retry < max_retries - 1:
                        time.sleep(1)
            
            print(f"  📝 Puzzle instruction: {instruction}")
            
            # Detect puzzle type and target object
            detected_target = self._detect_target_object(instruction)
            print(f"  🎯 Target object: {detected_target}")
            
            # Get all image tiles with retry logic
            tiles = []
            for retry in range(max_retries):
                try:
                    tiles = iframe.locator('.rc-imageselect-tile').all()
                    if len(tiles) > 0:
                        break
                except Exception as e:
                    print(f"  ⚠️  Failed to get image tiles (attempt {retry + 1}/{max_retries}): {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)
            
            print(f"  🖼️  Found {len(tiles)} image tiles")
            
            if len(tiles) == 0:
                return False
            
            # Analyze each tile using AI vision
            selected_indices = self._analyze_tiles_with_ai(tiles, detected_target, page, iframe)
            
            # If AI analysis fails, fall back to heuristic selection
            if not selected_indices:
                print("  ⚠️  AI analysis produced no results, using heuristic selection...")
                return self._heuristic_tile_selection(tiles, iframe)
            
            print(f"  👆 Clicking {len(selected_indices)} tiles identified by AI...")
            
            # Click selected tiles with human-like delays
            for idx in sorted(selected_indices):
                time.sleep(random.uniform(0.3, 0.8))  # Human-like delay
                try:
                    tiles[idx].click()
                    print(f"    ✓ Clicked tile {idx + 1}")
                except Exception as click_error:
                    print(f"    ⚠️  Error clicking tile {idx + 1}: {click_error}")
            
            time.sleep(1)
            
            # Click verify button with retry logic
            verify_clicked = False
            for retry in range(max_retries):
                try:
                    verify_button = iframe.locator('#recaptcha-verify-button, .rc-button-default').first
                    if verify_button:
                        print("  🔘 Clicking verify button...")
                        time.sleep(random.uniform(0.5, 1.0))
                        verify_button.click()
                        verify_clicked = True
                        break
                except Exception as e:
                    print(f"  ⚠️  Error clicking verify button (attempt {retry + 1}/{max_retries}): {e}")
                    if retry < max_retries - 1:
                        time.sleep(2)
            
            if not verify_clicked:
                print("  ⚠️  Could not click verify button after retries")
                return False
            
            time.sleep(3)
            
            # Check if challenge passed
            new_challenge = iframe.locator('.rc-imageselect-incorrect-response')
            if new_challenge.count() > 0:
                print("  ⚠️  AI selection incorrect, puzzle refreshed")
                return False
            else:
                print("  ✅ Puzzle verification submitted successfully!")
                return True
        except Exception as e:
            print(f"  ⚠️  Error solving image puzzle: {e}")
            return False

    def _detect_target_object(self, instruction: str) -> str:
        """Detect target object from instruction text"""
        instruction_lower = instruction.lower()
        for obj in self.target_objects:
            if obj in instruction_lower:
                return obj
        return "unknown object"
    
    def _analyze_tiles_with_ai(self, tiles, target_object: str, page, iframe) -> List[int]:
        """Analyze image tiles using AI vision to identify matching objects"""
        try:
            selected_indices = []
            
            # Process each tile
            for i, tile in enumerate(tiles):
                try:
                    # Take screenshot of the tile
                    screenshot_bytes = tile.screenshot()
                    
                    # Convert to PIL Image for analysis
                    image = Image.open(io.BytesIO(screenshot_bytes))
                    
                    # Analyze image with AI
                    is_match = self._analyze_single_tile(image, target_object)
                    
                    if is_match:
                        selected_indices.append(i)
                        print(f"    🎯 Tile {i + 1}: MATCH ({target_object})")
                    else:
                        print(f"    ❌ Tile {i + 1}: No match")
                        
                except Exception as e:
                    print(f"    ⚠️  Error analyzing tile {i + 1}: {e}")
                    # Use heuristic as fallback
                    if random.random() < 0.3:  # 30% chance to select if uncertain
                        selected_indices.append(i)
            
            return selected_indices
            
        except Exception as e:
            print(f"  ⚠️  Error in AI tile analysis: {e}")
            return []
    
    def _analyze_single_tile(self, image: Image.Image, target_object: str) -> bool:
        """Analyze a single tile image using AI vision"""
        try:
            # Convert image to base64 for API
            buffered = io.BytesIO()
            image.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            # Create prompt for AI analysis
            prompt = f"""
            Analyze this image and determine if it contains a {target_object}.
            Respond with ONLY 'YES' if it contains the object, or 'NO' if it does not.
            Be conservative in your assessment - only say YES if you're confident.
            """
            
            # Call Groq Vision API
            chat_completion = self.groq_client.chat.completions.create(
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_str}"
                                }
                            }
                        ]
                    }
                ],
                model="llama-3.2-11b-vision-preview",
                temperature=0.1,
                max_tokens=10,
            )
            
            # Check if we got a response
            if chat_completion and chat_completion.choices and chat_completion.choices[0].message.content:
                response = chat_completion.choices[0].message.content.strip().upper()
                return response == "YES"
            else:
                print("  ⚠️  No response from AI vision API")
                return False
            
        except Exception as e:
            print(f"  ⚠️  Error in single tile analysis: {e}")
            return False
    
    def _heuristic_tile_selection(self, tiles, iframe) -> bool:
        """Fallback heuristic tile selection when AI fails"""
        try:
            # Strategy: Click tiles with human-like randomness
            # This is a heuristic approach - we'll click a strategic selection
            
            # For a 3x3 grid (9 tiles), use intelligent selection pattern
            if len(tiles) == 9:
                # Click tiles in a pattern that looks human-like
                # Typically 2-4 tiles are correct in a 3x3 grid
                num_to_click = random.randint(2, 4)
                
                # Select tiles with some randomness but avoid patterns
                indices_to_click = random.sample(range(len(tiles)), num_to_click)
                
                print(f"  👆 Clicking {num_to_click} tiles (heuristic)...")
                
                for idx in sorted(indices_to_click):
                    time.sleep(random.uniform(0.3, 0.8))  # Human-like delay
                    tiles[idx].click()
                    print(f"    ✓ Clicked tile {idx + 1}")
                
                time.sleep(1)
                
            # For 4x4 grid (16 tiles)
            elif len(tiles) == 16:
                num_to_click = random.randint(3, 6)
                indices_to_click = random.sample(range(len(tiles)), num_to_click)
                
                print(f"  👆 Clicking {num_to_click} tiles (heuristic)...")
                
                for idx in sorted(indices_to_click):
                    time.sleep(random.uniform(0.3, 0.8))
                    tiles[idx].click()
                    print(f"    ✓ Clicked tile {idx + 1}")
                
                time.sleep(1)
            
            # Click verify button
            try:
                verify_button = iframe.locator('#recaptcha-verify-button, .rc-button-default').first
                if verify_button:
                    print("  🔘 Clicking verify button...")
                    time.sleep(random.uniform(0.5, 1.0))
                    verify_button.click()
                    time.sleep(3)
                    
                    # Check if challenge passed
                    new_challenge = iframe.locator('.rc-imageselect-incorrect-response')
                    if new_challenge.count() > 0:
                        print("  ⚠️  Heuristic selection incorrect, puzzle refreshed")
                        return False
                    else:
                        print("  ✅ Puzzle verification submitted")
                        return True
            except Exception as e:
                print(f"  ⚠️  Error clicking verify: {e}")
                return False
            
            return True
            
        except Exception as e:
            print(f"  ⚠️  Error in heuristic selection: {e}")
            return False
    
    def _move_mouse_naturally(self, page, target_x: float, target_y: float, duration: float = 3.0):
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
                time.sleep(duration / steps)
            
            # Final precise movement to target
            page.mouse.move(target_x, target_y)
            print("  ✓ Mouse moved to target position")
            time.sleep(random.uniform(0.05, 0.15))
            
        except Exception as e:
            print(f"  ⚠️  Error moving mouse: {e}")

    def _click_bounding_box(self, page, locator):
        """Click element using bounding box coordinates"""
        # Add longer timeout for bounding box retrieval
        bbox = locator.bounding_box(timeout=10000)
        if bbox:
            x = bbox['x'] + bbox['width'] / 2
            y = bbox['y'] + bbox['height'] / 2
            page.mouse.click(x, y)
            return True
        raise Exception("Could not get bounding box")

    def _js_click(self, page, locator):
        """Click element using JavaScript"""
        # Add longer timeout for element handle retrieval
        element = locator.element_handle(timeout=10000)
        page.evaluate("""el => {
            if (el) {
                el.click();
                return true;
            }
            return false;
        }""", element)

# Export the solver
def create_captcha_solver(groq_client: Groq) -> AdvancedCaptchaSolver:
    """Create an instance of the advanced CAPTCHA solver"""
    return AdvancedCaptchaSolver(groq_client)