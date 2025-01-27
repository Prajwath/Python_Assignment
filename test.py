import re
from opencage.geocoder import OpenCageGeocode

# OpenCage API Key (get your free API key from https://opencagedata.com/)
API_KEY = '18011e925f334c51874c61662e19ea03'
geocoder = OpenCageGeocode(API_KEY)


def extract_country(address):
    # Step 1: Check for "India" explicitly in the address
    if re.search(r'\b(?:India)\b', address, re.IGNORECASE):
        return "India"

    # Step 2: Extract the postal code from the address
    postal_code_match = re.search(r'\b\d{5,6}\b', address)  # Matches 5- or 6-digit postal codes
    if postal_code_match:
        postal_code = postal_code_match.group(0)
        # Use OpenCage Geocoder to find country based on postal code
        postal_result = geocoder.geocode(postal_code)
        if postal_result and 'components' in postal_result[0]:
            return postal_result[0]['components'].get('country', 'Unknown')

    # Step 3: Use the full address with OpenCage Geocoder if no postal code is found
    result = geocoder.geocode(address)
    if result and 'components' in result[0]:
        return result[0]['components'].get('country', 'Unknown')

    return 'Unknown'


# Sample addresses
sample1 = "having it’s registered office at A207 , Eastern Business District , Bhandup W , Mumbai 400078"
sample2 = "registered office at Grant House , 2nd Floor , Uppal Hyderabad 500013 India ."

# Extract country
print(extract_country(sample1))  # Output: India (based on postal code 400078)
print(extract_country(sample2))  # Output: India (explicitly mentioned in the address)
