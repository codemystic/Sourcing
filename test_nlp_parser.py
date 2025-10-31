"""
Test script for NLP query parser
"""

from nlp_query_parser import parse_nlp_query, format_search_query


def test_parser():
    """Test the NLP query parser with various inputs"""
    
    test_queries = [
        "5+ year experienced Python developer in Hyderabad",
        "Looking for Java developer with 3 years experience in Bangalore",
        "Find senior software engineer 7+ years exp from Pune",
        "Data scientist 4 years experience Mumbai",
        "Machine learning engineer with 6+ years experience in Delhi",
        "Python developer Hyderabad",
        "10 years experienced frontend developer in Chennai"
    ]
    
    print("="*80)
    print("TESTING NLP QUERY PARSER")
    print("="*80)
    
    for query in test_queries:
        print(f"\nQuery: '{query}'")
        parsed = parse_nlp_query(query)
        print(f"Parsed: {parsed}")
        search_query = format_search_query(parsed)
        print(f"Search Query: '{search_query}'")
        print("-" * 50)


if __name__ == "__main__":
    test_parser()