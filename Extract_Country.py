import re
from opencage.geocoder import OpenCageGeocode

# OpenCage API Key (get your free API key from https://opencagedata.com/)
API_KEY = '18011e925f334c51874c61662e19ea03'
geocoder = OpenCageGeocode(API_KEY)


def extract_country(address):
    # Regex pattern to match 5 or 6 digit postal codes
    postal_code_pattern = r'\b\d{5,6}\b'

    # Step 1: Try to find a postal code in the address
    match = re.search(postal_code_pattern, address)

    if match:
        postal_code = match.group(0)
        # Use OpenCage Geocoder to find the country based on postal code
        postal_result = geocoder.geocode(postal_code)
        if postal_result and 'components' in postal_result[0]:
            country = postal_result[0]['components'].get('country', 'Unknown')
            return country

    # Step 2: If no postal code is found, use the full address to extract the country
    result = geocoder.geocode(address)
    if result and 'components' in result[0]:
        return result[0]['components'].get('country', 'Unknown')

    return 'Unknown'


# Sample addresses
sample1 = "having it’s registered office at A207 , Eastern Business District , Bhandup W , Mumbai 400078"
sample2 = "registered office at Grant House , 2nd Floor , Uppal Hyderabad 500013 India ."

# Extract country
print(extract_country(sample1))  # Expected output: India (based on postal code 400078)
print(extract_country(sample2))  # Expected output: India (based on postal code 500013 or explicit mention)
