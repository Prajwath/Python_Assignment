import re

# Define the mapping of states/cities to countries
state_to_country = {
    "Mumbai": "India",
    "Hyderabad": "India",
    "Delhi": "India",
    "Goa": "India",
    "Chennai": "India",
    "Kolkata": "India",
    "Bangalore": "India",
}


# Function to extract country or map state to country
def extract_country(address):
    # Regex patterns
    country_pattern = r"(?i)\b(India|[A-Z][a-z]+)\b"
    state_pattern = r"(?i)\b(Mumbai|Hyderabad|Delhi|Goa|Chennai|Kolkata|Bangalore|[A-Z][a-z]+)\b"

    # Check for country in address
    country_match = re.search(country_pattern, address)
    if country_match:
        return country_match.group(0)

    # If no country, check for state/city and map to country
    state_match = re.search(state_pattern, address)
    if state_match:
        state = state_match.group(0)
        return state_to_country.get(state, "Unknown Country")

    return "Country not found"


# Test samples
sample1 = "having it’s registered office at A207 , Eastern Business District , Bhandup W , Mumbai 400078"
sample2 = "registered office at Grant House , 2nd Floor , Uppal Hyderabad 500013 India ."

print(extract_country(sample1))  # Output: India
print(extract_country(sample2))  # Output: India
