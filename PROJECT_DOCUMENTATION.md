# LinkedIn Profile Scraper with OCR and CAPTCHA Solving

## Table of Contents
1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [File Structure](#file-structure)
4. [Core Components](#core-components)
   - [check_session.py](#check_sessionpy)
   - [advanced_captcha_solver.py](#advanced_captcha_solverpy)
   - [linkedin_scraper_ocr.py](#linkedin_scraper_ocrpy)
5. [Screenshot Approach](#screenshot-approach)
6. [CAPTCHA Solving Mechanism](#captcha-solving-mechanism)
7. [Installation and Setup](#installation-and-setup)
8. [Usage](#usage)
9. [Technical Details](#technical-details)

## Project Overview

This project is an advanced LinkedIn profile scraper that uses OCR (Optical Character Recognition) techniques combined with AI-powered data extraction to gather professional information from LinkedIn profiles. The scraper performs Google X-ray searches to find profiles matching specific criteria and then extracts structured data from each profile.

The system is designed to be human-like in its behavior, implementing natural mouse movements, random delays, and other techniques to avoid detection. It also features an advanced CAPTCHA solving system that can automatically handle both checkbox and image-based reCAPTCHA challenges.

## Key Features

- **Google X-ray Search**: Performs targeted searches on Google to find LinkedIn profiles matching specific job titles and locations
- **Human-like Behavior Simulation**: Implements natural mouse movements, typing delays, and scrolling patterns
- **OCR-based Profile Extraction**: Takes screenshots of LinkedIn profiles and extracts text content for processing
- **AI-powered Data Structuring**: Uses Groq's LLM API to convert extracted text into structured JSON data
- **Advanced CAPTCHA Solving**: Automatically handles reCAPTCHA challenges using a combination of computer vision and AI analysis
- **Session Management**: Can load and use saved LinkedIn sessions to bypass login requirements
- **Multi-page Scraping**: Automatically navigates through multiple pages of search results
- **Error Handling**: Robust error handling and retry mechanisms for network issues and page loading problems

## File Structure

```
.
├── linkedin_scraper_ocr.py     # Main scraper application
├── advanced_captcha_solver.py  # CAPTCHA solving module
├── check_session.py           # Session validation utility
├── human_behavior.py          # Human-like behavior simulation
├── nlp_query_parser.py        # Natural language query parsing
├── linkedin_session_loader.py # LinkedIn session loading (optional)
├── .env                       # Environment variables (API keys)
├── data/
│   ├── screenshots/           # Profile and CAPTCHA screenshots
│   ├── profiles_multi_page_ocr.json  # Extracted profile data
│   └── scraping_summary_ocr.json     # Scraping summary
└── linkedin_auth.json         # Saved LinkedIn session (if available)
```

## Core Components

### check_session.py

This utility script validates the LinkedIn session file (`linkedin_auth.json`) to ensure it exists and contains valid session data. It checks for:

1. File existence
2. Non-zero file size
3. Valid JSON structure
4. Presence of cookies array
5. Valid cookie entries with name and value fields

The script provides clear feedback on the session file status and offers guidance on how to create a valid session if one is not found.

### advanced_captcha_solver.py

This module provides a comprehensive CAPTCHA solving system with the following capabilities:

#### Key Features:
- **reCAPTCHA Checkbox Solving**: Automatically detects and solves reCAPTCHA checkboxes using multiple approaches:
  - Direct iframe interaction
  - Frame locator techniques
  - JavaScript-based clicking
  - Mouse movement simulation
- **Image Puzzle Solving**: Handles image-based CAPTCHA challenges using:
  - AI-powered image analysis
  - Heuristic-based selection
  - Conservative selection strategies
- **Multi-layered Approach**: Uses a combination of computer vision, AI analysis, and heuristic methods
- **Human-like Behavior**: Implements natural delays and mouse movements during CAPTCHA solving

#### Methods:
- `solve_recaptcha_checkbox()`: Handles checkbox-based CAPTCHAs
- `solve_image_puzzle()`: Solves image selection challenges
- `_analyze_single_tile()`: Analyzes individual CAPTCHA tiles using AI
- `_heuristic_tile_selection()`: Fallback method using heuristic selection
- `_move_mouse_naturally()`: Simulates human-like mouse movements

### linkedin_scraper_ocr.py

This is the main application file that orchestrates the entire scraping process:

#### Workflow:
1. **Environment Setup**: Loads API keys and initializes required modules
2. **Query Processing**: Parses natural language search queries into structured search terms
3. **Google X-ray Search**: Executes targeted searches on Google
4. **CAPTCHA Detection and Handling**: Automatically detects and solves CAPTCHA challenges
5. **Profile Extraction**: Navigates to individual LinkedIn profiles and extracts data
6. **Data Structuring**: Uses AI to convert raw text into structured JSON data
7. **Result Storage**: Saves extracted data to JSON files

#### Key Functions:
- `extract_profile_with_ocr()`: Takes screenshots of profiles and extracts text content
- `extract_profile_with_ai()`: Uses Groq's LLM to structure profile data
- `analyze_captcha_screenshot_with_vision_model()`: Analyzes CAPTCHA screenshots with vision model
- `move_mouse_naturally()`: Simulates human-like mouse movements

## Screenshot Approach

The screenshot approach is a core component of this scraper, used for both profile data extraction and CAPTCHA solving:

### Profile Screenshots

1. **Full-page Screenshots**: For each LinkedIn profile, the system takes a full-page screenshot and saves it to `data/screenshots/` with a unique filename
2. **Text Extraction**: The system extracts text content from the profile page using Playwright's evaluation capabilities
3. **AI Processing**: The extracted text is sent to Groq's LLM API for structuring into JSON format
4. **Data Storage**: Both the screenshot and structured data are saved for future reference

### CAPTCHA Screenshots

1. **Challenge Detection**: When a CAPTCHA is detected, the system takes a screenshot of the challenge
2. **Vision Model Analysis**: The screenshot is analyzed using Groq's vision model (`meta-llama/llama-4-scout-17b-16e-instruct`)
3. **Response Formatting**: The vision model's output is formatted according to specific requirements:
   ```
   The images with [object] are:
   
   [Position description 1]
   [Position description 2]
   [Position description 3]
   [Position description 4]
   ```
4. **Automatic Solving**: The system uses this analysis to automatically select the correct images in CAPTCHA challenges

### Screenshot Implementation Details

```python
# Profile screenshot
screenshot_filename = f'profile_screenshot_{hash(profile_url) % 10000}.png'
screenshot_path = f'data/screenshots/{screenshot_filename}'
page.screenshot(path=screenshot_path, full_page=True, timeout=10000)

# CAPTCHA screenshot
captcha_screenshot_path = "data/screenshots/captcha_screenshot.png"
page.screenshot(path=captcha_screenshot_path, full_page=False, timeout=10000)
```

The screenshots are saved in PNG format and organized in the `data/screenshots/` directory. The system creates this directory automatically if it doesn't exist.

## CAPTCHA Solving Mechanism

The CAPTCHA solving system is designed to handle both checkbox and image-based reCAPTCHA challenges automatically:

### Checkbox CAPTCHA Solving

1. **Detection**: The system identifies reCAPTCHA checkboxes using multiple CSS selectors
2. **Mouse Simulation**: Natural mouse movements are simulated to approach the checkbox
3. **Clicking**: Multiple approaches are used to click the checkbox:
   - Direct iframe interaction
   - Frame locator techniques
   - JavaScript-based clicking
4. **Verification**: The system checks if the click was successful by looking for challenge iframes

### Image CAPTCHA Solving

1. **Challenge Analysis**: The system reads the CAPTCHA instruction to determine what objects to look for
2. **Tile Processing**: Each image tile is analyzed individually:
   - Screenshot capture of each tile
   - Computer vision analysis (edge detection, corner detection)
   - AI-powered object recognition using Groq's text model
3. **Selection Strategy**: A conservative approach is used to select tiles:
   - Never selects more than 1/3 of available tiles
   - Uses both AI analysis and heuristic fallbacks
4. **Verification**: The system submits selections and checks for success indicators

### Vision Model Integration

The CAPTCHA solving system integrates with Groq's vision model (`meta-llama/llama-4-scout-17b-16e-instruct`) to analyze CAPTCHA screenshots:

1. **Image Encoding**: Screenshots are encoded in base64 format
2. **Prompt Engineering**: Specific prompts guide the model to identify relevant objects
3. **Response Parsing**: The model's output is parsed to extract object locations
4. **Decision Making**: The parsed information is used to make selections in image challenges

## Installation and Setup

### Prerequisites

- Python 3.8+
- Playwright browser dependencies
- Groq API key

### Required Packages

```bash
pip install playwright groq python-dotenv pillow
playwright install chromium
```

### Environment Variables

Create a `.env` file with your Groq API key:

```env
GROQ_API_KEY=your_groq_api_key_here
```

## Usage

1. **Run the scraper**:
   ```bash
   python linkedin_scraper_ocr.py
   ```

2. **Enter search query**: When prompted, enter a natural language query like:
   - "5+ year experienced Python developer in Hyderabad"
   - "AI Engineer in Bangalore"

3. **Monitor progress**: The system will display progress information in the console

4. **Check results**: Extracted profile data will be saved to:
   - `data/profiles_multi_page_ocr.json`
   - `data/scraping_summary_ocr.json`

5. **Session checking**: Use the session checker utility:
   ```bash
   python check_session.py
   ```

## Technical Details

### Technologies Used

- **Playwright**: Browser automation for scraping
- **Groq API**: AI-powered text and vision processing
- **Python**: Core programming language
- **Pillow**: Image processing for CAPTCHA analysis

### AI Models

- **Text Processing**: `meta-llama/llama-4-scout-17b-16e-instruct`
- **Vision Processing**: `meta-llama/llama-4-scout-17b-16e-instruct`

### Data Flow

1. **Input**: Natural language query from user
2. **Processing**: Query parsing and Google X-ray search
3. **Collection**: Profile URL gathering from search results
4. **Extraction**: Screenshot-based OCR and text extraction
5. **Structuring**: AI-powered conversion to structured JSON
6. **Storage**: Data saved to JSON files

### Error Handling

The system implements comprehensive error handling:

- **Network Issues**: Retry mechanisms for failed requests
- **Page Loading**: Timeout handling and fallback strategies
- **Element Detection**: Multiple selectors and approaches for finding elements
- **CAPTCHA Failures**: Multiple solving attempts with different strategies
- **Data Extraction**: Graceful handling of missing or malformed data

### Privacy and Ethics

This tool is designed for educational and research purposes. Users should:

- Comply with LinkedIn's Terms of Service
- Respect rate limits and avoid excessive scraping
- Only scrape publicly available information
- Obtain proper authorization when required