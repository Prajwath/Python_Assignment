import re

def extract_amount(text):
    """Extract the amount using a regular expression."""
    # Regex pattern to capture the amount after "Rs" or "INR"
    match = re.search(r"(?:Rs \. ?|INR|Rs )\s*([\d,]+(?:\s*,\s*\d{2,3})*)\s*(?:/-)?", text, re.IGNORECASE)
    if match:
        return match.group(1).strip().replace(' ', '')  # Remove any spaces in the amount
    else:
        return None

# Test samples
sample1 = "Nominated Authority an amount of Rs . 25 ,05 ,000"
sample2 = "aggregate a sum of INR 22 ,000/-"
sample3 = "another sum of Rs 45,000"  # No trailing /-

# Extract amount
amount1 = extract_amount(sample1)
amount2 = extract_amount(sample2)
amount3 = extract_amount(sample3)

print(f"Extracted Amount from sample1: {amount1}")
print(f"Extracted Amount from sample2: {amount2}")
print(f"Extracted Amount from sample3: {amount3}")