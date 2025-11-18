"""
Advanced CAPTCHA Solver Module
Handles various types of CAPTCHAs using AI/ML techniques
"""

import base64
import time
import random
from typing import Optional
from playwright.sync_api import Page

class AdvancedCaptchaSolver:
    """Handles advanced CAPTCHA solving using AI/ML techniques"""
    
    def __init__(self, groq_client=None):
        self.groq_client = groq_client
        print("🔄 Advanced CAPTCHA Solver initialized")
    
    def solve_recaptcha_checkbox(self, page: Page) -> bool:
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
    
    def solve_image_puzzle(self, page: Page, vision_analysis: Optional[str] = None) -> bool:
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
                            
                            # Try to manually navigate to the search results page
                            try:
                                # Extract the continue URL from the CAPTCHA page
                                continue_url = None
                                # Look for the continue parameter in the URL
                                if 'continue=' in current_url:
                                    import urllib.parse
                                    parsed_url = urllib.parse.urlparse(current_url)
                                    query_params = urllib.parse.parse_qs(parsed_url.query)
                                    if 'continue' in query_params:
                                        continue_url = query_params['continue'][0]
                                        # Decode the URL if it's encoded
                                        continue_url = urllib.parse.unquote(continue_url)
                                
                                if continue_url:
                                    print(f"  🔄 Manually navigating to continue URL: {continue_url}")
                                    page.goto(continue_url)
                                    time.sleep(3)
                                    return True
                                else:
                                    print("  ⚠️  Could not find continue URL in CAPTCHA page")
                            except Exception as nav_error:
                                print(f"  ⚠️  Error navigating to continue URL: {nav_error}")
                            
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
                    
                    # Try to manually navigate to the search results page
                    try:
                        # Extract the continue URL from the CAPTCHA page
                        continue_url = None
                        # Look for the continue parameter in the URL
                        if 'continue=' in current_url:
                            import urllib.parse
                            parsed_url = urllib.parse.urlparse(current_url)
                            query_params = urllib.parse.parse_qs(parsed_url.query)
                            if 'continue' in query_params:
                                continue_url = query_params['continue'][0]
                                # Decode the URL if it's encoded
                                continue_url = urllib.parse.unquote(continue_url)
                        
                        if continue_url:
                            print(f"  🔄 Manually navigating to continue URL: {continue_url}")
                            page.goto(continue_url)
                            time.sleep(3)
                            return True
                        else:
                            print("  ⚠️  Could not find continue URL in CAPTCHA page")
                    except Exception as nav_error:
                        print(f"  ⚠️  Error navigating to continue URL: {nav_error}")
                    
                    return False
                else:
                    print("  ✅ Successfully redirected after solving CAPTCHA")
                    return True
            
            print("  ⚠️  Could not find verify button")
            return False
            
        except Exception as e:
            print(f"  ⚠️  Error solving image puzzle: {e}")
            return False