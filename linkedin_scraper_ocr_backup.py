if captcha_detected:
    print("\n" + "="*80)
    print("🤖 CAPTCHA CHALLENGE DETECTED!")
    print("="*80)
    print("\n🔄 Starting fully automatic CAPTCHA solving...\n")
    
    # Keep solving CAPTCHAs until we're redirected to the search results page
    max_captcha_attempts = 10  # Maximum number of CAPTCHA attempts
    captcha_attempt = 0
    
    while captcha_attempt < max_captcha_attempts:
        captcha_attempt += 1
        print(f"\n🔄 CAPTCHA solving attempt {captcha_attempt}/{max_captcha_attempts}...")
        
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
                    # Wait a bit for the page to redirect after solving CAPTCHA
                    print("⏳ Waiting for page to redirect after CAPTCHA solving...")
                    sleep(5)
                    
                    # Check if we're still on a CAPTCHA page or have been redirected
                    current_url = page.url.lower()
                    if 'sorry' in current_url or 'recaptcha' in current_url:
                        print("⚠️  Still on CAPTCHA page, solving may not have been successful")
                        # Try to check for success indicators
                        try:
                            # Look for elements that indicate we've passed the CAPTCHA
                            success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                            if len(success_indicators) > 0:
                                print("✅ Found search elements, likely passed CAPTCHA")
                                # Check if we're on the search results page
                                if 'search' in current_url and 'google.com' in current_url:
                                    print("✅ Successfully redirected to Google search results page")
                                    break  # Exit the loop as we've successfully passed CAPTCHA
                        except:
                            pass
                        # Continue to next iteration to try solving again
                    else:
                        print("✅ Successfully redirected after solving CAPTCHA")
                        # Check if we're on the search results page
                        if 'search' in current_url and 'google.com' in current_url:
                            print("✅ Successfully redirected to Google search results page")
                            break  # Exit the loop as we've successfully passed CAPTCHA
                else:
                    print("⚠️  Automatic image puzzle solving failed")
                    # Continue to next iteration to try solving again
            else:
                print("✓ No additional challenges detected")
                # Check if we're on the search results page
                current_url = page.url.lower()
                if 'search' in current_url and 'google.com' in current_url:
                    print("✅ Successfully on Google search results page")
                    break  # Exit the loop as we're on the search results page
                print("✓ Proceeding with scraping...")
        else:
            print("\n⚠️  Checkbox solving failed")
        
        # If we reach here, it means we're still facing CAPTCHA challenges
        # Wait a bit before trying again
        print(f"⏳ Waiting before next CAPTCHA solving attempt ({captcha_attempt + 1})...")
        sleep(3)
        
        # Re-check for CAPTCHA indicators
        captcha_detected = False
        for selector in image_challenge_selectors:
            try:
                if page.query_selector(selector):
                    captcha_detected = True
                    break
            except:
                pass
        
        # Also check for reCAPTCHA elements directly
        recaptcha_elements = page.query_selector_all('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"], .g-recaptcha')
        if len(recaptcha_elements) > 0:
            captcha_detected = True
    
    if captcha_attempt >= max_captcha_attempts:
        print(f"\n⚠️  Maximum CAPTCHA solving attempts ({max_captcha_attempts}) reached")
        print("⚠️  Continuing anyway - CAPTCHA may pass automatically...")
        sleep(5)
        
        # Check if we're past the CAPTCHA
        current_url = page.url.lower()
        if '/feed' in current_url or '/in/' in current_url or ('search' in current_url and 'google.com' in current_url):
            print("✅ Successfully passed CAPTCHA automatically!")
        else:
            # Even if we're not past CAPTCHA, continue anyway
            print("⚠️  Proceeding despite CAPTCHA - may work anyway...")
    
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
                
                # Keep solving CAPTCHAs until we're redirected to the search results page
                max_captcha_attempts = 10  # Maximum number of CAPTCHA attempts
                captcha_attempt = 0
                
                while captcha_attempt < max_captcha_attempts:
                    captcha_attempt += 1
                    print(f"\n🔄 CAPTCHA solving attempt {captcha_attempt}/{max_captcha_attempts}...")
                    
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
                                
                                # Check if we're still on a CAPTCHA page or have been redirected
                                current_url = page.url.lower()
                                if 'sorry' in current_url or 'recaptcha' in current_url:
                                    print("⚠️  Still on CAPTCHA page, solving may not have been successful")
                                    # Try to check for success indicators
                                    try:
                                        # Look for elements that indicate we've passed the CAPTCHA
                                        success_indicators = page.query_selector_all('input[name="q"], #search, #searchbox, [aria-label*="Search"]')
                                        if len(success_indicators) > 0:
                                            print("✅ Found search elements, likely passed CAPTCHA")
                                            # Check if we're on the search results page
                                            if 'search' in current_url and 'google.com' in current_url:
                                                print("✅ Successfully redirected to Google search results page")
                                                break  # Exit the loop as we've successfully passed CAPTCHA
                                    except:
                                        pass
                                    # Continue to next iteration to try solving again
                                else:
                                    print("✅ Successfully redirected after solving CAPTCHA")
                                    # Check if we're on the search results page
                                    if 'search' in current_url and 'google.com' in current_url:
                                        print("✅ Successfully redirected to Google search results page")
                                        break  # Exit the loop as we've successfully passed CAPTCHA
                            else:
                                print("⚠️  Advanced image puzzle solving failed")
                                # Continue to next iteration to try solving again
                        else:
                            print("✓ No additional challenges detected")
                            # Check if we're on the search results page
                            current_url = page.url.lower()
                            if 'search' in current_url and 'google.com' in current_url:
                                print("✅ Successfully on Google search results page")
                                break  # Exit the loop as we're on the search results page
                            print("✓ Proceeding with scraping...")
                    else:
                        print("\n⚠️  Checkbox solving failed")
                    
                    # If we reach here, it means we're still facing CAPTCHA challenges
                    # Wait a bit before trying again
                    print(f"⏳ Waiting before next CAPTCHA solving attempt ({captcha_attempt + 1})...")
                    sleep(3)
                    
                    # Re-check for CAPTCHA indicators
                    captcha_detected = False
                    for selector in image_challenge_selectors:
                        try:
                            if page.query_selector(selector):
                                captcha_detected = True
                                break
                        except:
                            pass
                    
                    # Also check for reCAPTCHA elements directly
                    recaptcha_elements = page.query_selector_all('iframe[src*="recaptcha"], iframe[title*="reCAPTCHA"], .g-recaptcha')
                    if len(recaptcha_elements) > 0:
                        captcha_detected = True
                
                if captcha_attempt >= max_captcha_attempts:
                    print(f"\n⚠️  Maximum CAPTCHA solving attempts ({max_captcha_attempts}) reached")
                    print("⚠️  Continuing anyway - CAPTCHA may pass automatically...")
                    sleep(5)
                    
                    # Check if we're past the CAPTCHA
                    current_url = page.url.lower()
                    if '/feed' in current_url or '/in/' in current_url or ('search' in current_url and 'google.com' in current_url):
                        print("✅ Successfully passed CAPTCHA automatically!")
                    else:
                        # Even if we're not past CAPTCHA, continue anyway
                        print("⚠️  Proceeding despite CAPTCHA - may work anyway...")
                
                print("\n✅ CAPTCHA handling completed - proceeding with automated scraping!")
    except Exception as e:
        print(f"⚠️  Error checking for Google CAPTCHA: {e}")