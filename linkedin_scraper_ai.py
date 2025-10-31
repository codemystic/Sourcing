import warnings
warnings.filterwarnings("ignore")

import os
import json
from playwright.sync_api import sync_playwright
from time import sleep
from dotenv import load_dotenv
from groq import Groq

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

# Initialize Groq client
groq_client = Groq(api_key=GROQ_API_KEY)

# Initialize Playwright
playwright = sync_playwright().start()
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
        email_field.click()
        sleep(1)
        email_field.fill('')
        sleep(0.5)
        email_field.type(EMAIL, delay=50)
        print("Email entered successfully")
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
        password_field.click()
        sleep(1)
        password_field.fill('')
        sleep(0.5)
        password_field.type(PASSWORD, delay=50)
        print("Password entered successfully")
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
        sign_in_button.click()
        print("Sign-in button clicked successfully")
    else:
        print("Error: Sign-in button element not found")
except Exception as e:
    print(f"Error clicking sign-in button: {e}")
    try:
        page.click('button:has-text("Sign in")')
        print("Sign-in button clicked using alternative selector")
    except Exception as e2:
        print(f"Error with alternative selector: {e2}")

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

# Find and click the search bar
print("Looking for search bar...")
try:
    page.wait_for_selector('[placeholder*="Search"]', timeout=10000)
    print("Search bar found")
    
    search_bar = page.query_selector('[placeholder*="Search"]')
    if search_bar:
        search_bar.click()
        sleep(1)
        
        search_keyword = "AI Engineer"
        print(f"Entering search keyword: {search_keyword}")
        search_bar.type(search_keyword, delay=50)
        sleep(2)
        
        print("Search keyword entered successfully")
    else:
        print("Error: Search bar element not found")
except Exception as e:
    print(f"Error finding or using search bar: {e}")

sleep(1)

# Press Enter to perform the search
print("Pressing Enter to search...")
try:
    page.press('[placeholder*="Search"]', 'Enter')
    print("Search submitted")
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
    page.wait_for_selector('button[data-filter-type="currentCompany"], button:has-text("People")', timeout=10000)
    
    people_filters = page.query_selector_all('button')
    people_filter_found = False
    
    for button in people_filters:
        button_text = button.text_content()
        if button_text and 'People' in button_text.strip():
            print(f"Found 'People' filter button")
            button.click()
            people_filter_found = True
            sleep(2)
            break
    
    if not people_filter_found:
        print("Warning: Could not find 'People' filter button")
        try:
            page.click('[data-item="people"]')
            print("People filter clicked using alternative selector")
            sleep(2)
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
        print(f"Found {len(profile_links)} candidate profiles")
        
        first_profile = profile_links[0]
        profile_url = first_profile.get_attribute('href')
        print(f"First candidate profile URL: {profile_url}")
        print("Clicking on first candidate...")
        
        first_profile.click()
        sleep(2)
        
        print("Profile clicked, waiting for page to load...")
        page.wait_for_load_state('networkidle', timeout=15000)
        sleep(3)
        
    else:
        print("Error: No candidate profiles found")
        profile_url = None
        
except Exception as e:
    print(f"Error selecting first candidate: {e}")
    profile_url = None

# Get the actual profile URL
url = page.url
print(f"Current profile URL: {url}")

# ============================================================================
# Human-like Scrolling Behavior
# ============================================================================

print("\n" + "="*80)
print("Starting AI-powered profile data extraction...")
print("Mimicking human-like browsing behavior (scrolling and waiting)")
print("="*80 + "\n")

# Scroll down to load all content
print("Scrolling down to load profile content...")
for i in range(5):
    try:
        page.evaluate('window.scrollBy(0, 800)')
        sleep(2)
        print(f"Scroll {i+1}/5 completed")
    except:
        print(f"Warning: Could not complete scroll {i+1}")

# Scroll back to top
print("Scrolling back to top...")
try:
    page.evaluate('window.scrollTo(0, 0)')
    sleep(2)
    print("Scrolled to top")
except:
    print("Warning: Could not scroll to top")

sleep(2)

# ============================================================================
# Get Page Source and Extract with AI
# ============================================================================

print("\n" + "="*80)
print("Extracting page source...")
print("="*80 + "\n")

# Get the full page HTML
page_html = page.content()
print(f"Page HTML extracted (length: {len(page_html)} characters)")

# Function to extract data using Groq AI
def extract_profile_data_with_ai(html_content, data_type="basic_info"):
    """
    Extract profile data using Groq AI
    
    Args:
        html_content: The HTML content of the page
        data_type: Type of data to extract (basic_info, experience, education, etc.)
    """
    
    prompts = {
        "basic_info": """
        Extract the following basic information from this LinkedIn profile HTML:
        - name
        - headline
        - location
        - about (if available)
        
        Return the data as a valid JSON object with these exact keys.
        If a field is not found, use an empty string.
        Only return the JSON, no additional text.
        """,
        
        "experience": """
        Extract all work experience entries from this LinkedIn profile HTML.
        For each experience, extract:
        - company_name
        - designations (array of objects with: designation, duration, location, description)
        - total_duration
        
        Return the data as a valid JSON array of experience objects.
        If no experience is found, return an empty array.
        Only return the JSON, no additional text.
        """,
        
        "education": """
        Extract all education entries from this LinkedIn profile HTML.
        For each education entry, extract:
        - college/school name
        - degree
        - duration
        - description/activities (if available)
        
        Return the data as a valid JSON array of education objects.
        If no education is found, return an empty array.
        Only return the JSON, no additional text.
        """,
        
        "skills_certs": """
        Extract the following from this LinkedIn profile HTML:
        - skills (array of skill names)
        - certifications (array of objects with: name, issuer, date)
        - licenses (array of objects with: name, institute, issued_date)
        
        Return the data as a valid JSON object.
        If a field is not found, use an empty array.
        Only return the JSON, no additional text.
        """
    }
    
    prompt = prompts.get(data_type, prompts["basic_info"])
    
    # Truncate HTML if too long (keep first 30000 chars)
    truncated_html = html_content[:30000] if len(html_content) > 30000 else html_content
    
    print(f"Sending request to Groq for {data_type}...")
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are a data extraction expert. Extract structured data from HTML and return only valid JSON."
                },
                {
                    "role": "user",
                    "content": f"{prompt}\n\nHTML:\n{truncated_html}"
                }
            ],
            model="llama-3.3-70b-versatile",
            temperature=0.1,
            max_tokens=4000,
        )
        
        response_text = chat_completion.choices[0].message.content
        print(f"Groq response received for {data_type}")
        
        # Parse JSON response
        try:
            # Remove markdown code blocks if present
            if "```json" in response_text:
                response_text = response_text.split("```json")[1].split("```")[0].strip()
            elif "```" in response_text:
                response_text = response_text.split("```")[1].split("```")[0].strip()
            
            data = json.loads(response_text)
            return data
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Response text: {response_text[:500]}")
            return None
            
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return None

# Extract different sections using AI
print("\n" + "="*80)
print("Extracting profile data with AI...")
print("="*80 + "\n")

profile_data = {"url": url}

# Extract basic info
print("1. Extracting basic information...")
basic_info = extract_profile_data_with_ai(page_html, "basic_info")
if basic_info:
    profile_data.update(basic_info)
    print(f"✓ Basic info extracted: {json.dumps(basic_info, indent=2)}")
else:
    print("✗ Failed to extract basic info")

sleep(1)

# Extract experience
print("\n2. Extracting work experience...")
experience = extract_profile_data_with_ai(page_html, "experience")
if experience:
    profile_data['experience'] = experience
    print(f"✓ Extracted {len(experience)} experience entries")
else:
    print("✗ Failed to extract experience")
    profile_data['experience'] = []

sleep(1)

# Extract education
print("\n3. Extracting education...")
education = extract_profile_data_with_ai(page_html, "education")
if education:
    profile_data['education'] = education
    print(f"✓ Extracted {len(education)} education entries")
else:
    print("✗ Failed to extract education")
    profile_data['education'] = []

sleep(1)

# Extract skills and certifications
print("\n4. Extracting skills and certifications...")
skills_certs = extract_profile_data_with_ai(page_html, "skills_certs")
if skills_certs:
    profile_data.update(skills_certs)
    print(f"✓ Skills and certifications extracted")
else:
    print("✗ Failed to extract skills and certifications")

# ============================================================================
# Save Profile Data to JSON
# ============================================================================

print("\n" + "="*80)
print("Saving extracted data...")
print("="*80 + "\n")

output_file = 'data/profile_data_ai.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(profile_data, f, indent=4, ensure_ascii=False)

print(f"✓ Profile data saved to {output_file}")
print(f"\nExtracted profile data:")
print(json.dumps(profile_data, indent=2, ensure_ascii=False))

# Close the browser
browser.close()
playwright.stop()

print("\n" + "="*80)
print("AI-powered scraping completed successfully!")
print("="*80)
