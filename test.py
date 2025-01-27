import re

# Sample text
text = "some text ... INDIAN OIL CORPORATION LIMITED , Auckland Garden , Mumbai , 400010:... some text"

# Regular expression pattern to match the address with a capturing group
pattern = r"(?:[A-Za-z\s]+,\s)?([A-Za-z\s]+,\s[A-Za-z\s]+,\s\d{6})"

# Search for the pattern in the text
match = re.search(pattern, text)

# Print the result if a match is found
if match:
    print("Extracted Address:", match.group(1))
else:
    print("No address found.")