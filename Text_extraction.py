import re

# Sample texts
sample1 = "Issuance Date 16-1-2025"
sample2 = "Issuance Date: 30-11-2022"

# Regular expression pattern to match the issuance date
pattern = r'Issuance Date[: ]+(\d{1,2}-\d{1,2}-\d{4})'

# Function to extract issuance date
def extract_issuance_date(text):
    match = re.search(pattern, text)
    if match:
        return match.group(1).strip()
    return None

# Extracting issuance dates from the samples
issuance_date1 = extract_issuance_date(sample1)
issuance_date2 = extract_issuance_date(sample2)

print("Issuance Date in sample1:", issuance_date1)
print("Issuance Date in sample2:", issuance_date2)