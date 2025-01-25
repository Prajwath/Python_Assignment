import re

# Sample texts
sample1 = "Applicant Name: M/s ACME Limited and having its registered office at Grant House, 2nd Floor, Uppal Hyderabad"
sample2 = "Applicant Name: M/s Tango Textiles, having its registered office at Hiranandani, Lake Road, Powai, Mumbai"

# Updated regex for Applicant Name
pattern = r"(?:Applicant|Bidder|M/s)\.?\s*([\w\s&'-]+?(?=,|having|and|with|$))"

# Extracting applicant names
applicant1 = re.search(pattern, sample1).group(1).strip()
applicant2 = re.search(pattern, sample2).group(1).strip()

print("Sample 1 Applicant Name:", applicant1)
print("Sample 2 Applicant Name:", applicant2)
