"""
NLP Query Parser for LinkedIn Scraper
Parses natural language queries to extract job title, experience, and location
"""

import re


def parse_nlp_query(query):
    """
    Parse natural language query to extract job title, years of experience, and location.
    
    Args:
        query (str): Natural language query like "5+ year experienced Python developer in Hyderabad"
        
    Returns:
        dict: Dictionary with parsed information
    """
    result = {
        'job_title': '',
        'years_experience': '',
        'location': '',
        'keywords': []
    }
    
    # Convert to lowercase for easier matching
    query_lower = query.lower().strip()
    
    # Extract years of experience
    experience_patterns = [
        r'(\d+\+?)\s*year[s]?\s*(?:of\s*)?experience',
        r'(\d+\+?)\s*year[s]?\s*(?:of\s*)?exp',
        r'(\d+\+?)\s*\+\s*year[s]?\s*(?:of\s*)?experience',
        r'(\d+\+?)\s*year[s]?\s*(?:of\s*)?exp',
        r'experience\s*(?:of\s*)?(\d+\+?)\s*year[s]?',
        r'exp\s*(?:of\s*)?(\d+\+?)\s*year[s]?',
        r'(\d+)\s*year[s]?\s*(?:of\s*)?experience',
        r'(\d+)\s*year[s]?\s*(?:of\s*)?exp',
        r'experience\s*(?:of\s*)?(\d+)\s*year[s]?'
    ]
    
    for pattern in experience_patterns:
        match = re.search(pattern, query_lower)
        if match:
            result['years_experience'] = match.group(1)
            # Remove matched part from query
            query_lower = re.sub(pattern, '', query_lower, 1)
            break
    
    # Extract location patterns
    # Common location names
    common_locations = [
        'hyderabad', 'bangalore', 'bengaluru', 'chennai', 'pune', 'mumbai', 'delhi', 'kolkata',
        'ahmedabad', 'jaipur', 'chandigarh', 'lucknow', 'patna', 'bhopal', 'indore',
        'nagpur', 'surat', 'kanpur', 'noida', 'ghaziabad', 'faridabad', 'gurgaon', 'gurugram',
        'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia',
        'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville',
        'san francisco', 'columbus', 'indianapolis', 'fort worth', 'charlotte',
        'seattle', 'denver', 'washington', 'boston', 'el paso', 'nashville', 'detroit',
        'oklahoma city', 'portland', 'las vegas', 'memphis', 'louisville', 'baltimore'
    ]
    
    # Check for locations in the query
    for location in common_locations:
        if location in query_lower:
            result['location'] = location.title()
            query_lower = query_lower.replace(location, ' ')
            break
    
    # Extract location with prepositions
    location_patterns = [
        r'\b(?:in|at|from)\s+([a-zA-Z\s]+?)(?:\s+(?:with|having|and)\b|$)',
        r'\b([a-zA-Z\s]+?)\s+(?:with|having|and)\b',
        r'\b(?:location|city)\s*[:\-]?\s*([a-zA-Z\s]+?)(?:\s+(?:with|having|and)\b|$)'
    ]
    
    if not result['location']:  # Only if location not already found
        for pattern in location_patterns:
            match = re.search(pattern, query_lower)
            if match:
                location = match.group(1).strip()
                # Filter out common non-location words
                if location.lower() not in ['with', 'having', 'and', 'for', 'the', 'of', 
                                          'years', 'year', 'experience', 'exp', 'experienced']:
                    result['location'] = location.title()
                    # Remove matched part from query
                    query_lower = re.sub(pattern, '', query_lower, 1)
                    break
    
    # Common job titles and patterns
    job_title_patterns = [
        (r'python\s*developer', 'Python Developer'),
        (r'java\s*developer', 'Java Developer'),
        (r'javascript\s*developer', 'JavaScript Developer'),
        (r'web\s*developer', 'Web Developer'),
        (r'frontend\s*developer', 'Frontend Developer'),
        (r'backend\s*developer', 'Backend Developer'),
        (r'full\s*stack\s*developer', 'Full Stack Developer'),
        (r'software\s*developer', 'Software Developer'),
        (r'software\s*engineer', 'Software Engineer'),
        (r'data\s*scientist', 'Data Scientist'),
        (r'machine\s*learning\s*engineer', 'Machine Learning Engineer'),
        (r'ai\s*engineer', 'AI Engineer'),
        (r'data\s*engineer', 'Data Engineer'),
        (r'devops\s*engineer', 'DevOps Engineer'),
        (r'cloud\s*engineer', 'Cloud Engineer'),
        (r'frontend\s*engineer', 'Frontend Engineer'),
        (r'backend\s*engineer', 'Backend Engineer'),
        (r'full\s*stack\s*engineer', 'Full Stack Engineer'),
        (r'senior\s*developer', 'Senior Developer'),
        (r'junior\s*developer', 'Junior Developer'),
        (r'lead\s*developer', 'Lead Developer'),
        (r'principal\s*engineer', 'Principal Engineer')
    ]
    
    # Extract job title
    job_title_found = False
    for pattern, title in job_title_patterns:
        if re.search(pattern, query_lower):
            result['job_title'] = title
            query_lower = re.sub(pattern, ' ', query_lower, 1)
            job_title_found = True
            break
    
    # Remove common stop words and patterns
    stop_words = ['looking', 'for', 'want', 'need', 'find', 'search', 'get', 'show', 'me', 
                  'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 
                  'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 
                  'might', 'must', 'can', 'able', 'to', 'of', 'in', 'on', 'at', 'by', 'with', 
                  'from', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 
                  'up', 'down', 'out', 'off', 'over', 'under', 'again', 'further', 'then', 
                  'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 
                  'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 
                  'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just', 'now',
                  'experienced', 'experience', 'exp', 'years', 'year', 'looking', 'find', 'want',
                  'd', 'D']  # Add common artifacts
    
    # Split query into words
    words = [word.strip('.,!?;:') for word in query_lower.split() if word.strip()]
    
    # Filter out stop words and empty strings
    keywords = [word for word in words if word and word not in stop_words]
    
    # If no job title found, try to construct one from keywords
    if not job_title_found and keywords:
        # Look for job title indicators
        job_title_indicators = ['developer', 'engineer', 'manager', 'analyst', 'consultant', 
                               'specialist', 'lead', 'senior', 'junior', 'intern', 'associate',
                               'director', 'head', 'chief', 'officer', 'architect', 'designer',
                               'scientist', 'researcher', 'technician', 'coordinator', 'supervisor']
        
        # Find job title
        job_title_words = []
        for i, word in enumerate(keywords):
            job_title_words.append(word)
            # If we hit a job title indicator, we likely have our title
            if any(indicator in word.lower() for indicator in job_title_indicators):
                break
            # If we have 3 words, stop (likely too long for a title)
            if len(job_title_words) >= 3:
                break
                
        if job_title_words:
            result['job_title'] = ' '.join(job_title_words).title()
            # Remove used keywords
            remaining_keywords = [word for word in keywords if word not in job_title_words]
        else:
            # Use first keyword as job title
            result['job_title'] = keywords[0].title()
            remaining_keywords = keywords[1:]
    else:
        remaining_keywords = keywords
    
    result['keywords'] = [word.title() for word in remaining_keywords if word]
    
    # Clean up empty fields
    if not result['job_title']:
        # Use remaining keywords as job title or default fallback
        if result['keywords']:
            result['job_title'] = result['keywords'][0]
            result['keywords'] = result['keywords'][1:]
        else:
            result['job_title'] = 'Developer'  # Default fallback
    
    return result


def format_search_query(parsed_query):
    """
    Format the parsed query into a LinkedIn search query.
    
    Args:
        parsed_query (dict): Parsed query from parse_nlp_query
        
    Returns:
        str: Formatted search query
    """
    job_title = parsed_query.get('job_title', '')
    years_exp = parsed_query.get('years_experience', '')
    keywords = parsed_query.get('keywords', [])
    
    # Build search query
    search_parts = []
    
    if job_title:
        search_parts.append(job_title)
        
    if years_exp:
        search_parts.append(f"{years_exp} years experience")
        
    if keywords:
        search_parts.extend(keywords)
        
    return ' '.join(search_parts)


# Example usage
if __name__ == "__main__":
    # Test the parser
    test_queries = [
        "5+ year experienced Python developer in Hyderabad",
        "Looking for Java developer with 3 years experience in Bangalore",
        "Find senior software engineer 7+ years exp from Pune",
        "Data scientist 4 years experience Mumbai",
        "Machine learning engineer with 6+ years experience in Delhi",
        "Python developer Hyderabad",
        "10 years experienced frontend developer in Chennai"
    ]
    
    for query in test_queries:
        print(f"\nQuery: {query}")
        parsed = parse_nlp_query(query)
        print(f"Parsed: {parsed}")
        search_query = format_search_query(parsed)
        print(f"Search Query: {search_query}")