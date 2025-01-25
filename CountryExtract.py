import spacy

def get_country_from_address_nlp(address):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(address)
    for ent in doc.ents:
        if ent.label_ == "GPE":  # GPE = Geopolitical Entity
            return ent.text
    return "Country not found"

# Example address
address = "8 Shroff Chambers, Girgaon, M.G. Road, Mumbai-400092, India"
country = get_country_from_address_nlp(address)
print("Country:", country)
