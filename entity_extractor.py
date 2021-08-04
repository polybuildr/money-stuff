from collections import Counter, defaultdict
import re

import spacy

from article import Article

RELEVANT_ENT_LABELS = [
    "FAC",
    "GPE",
    "LOC",
    "NORP",
    "ORG",
    "PERSON",
    "PRODUCT",
    "EVENT",
    "WORK_OF_ART",
]

ENT_REPLACEMENTS = {
    "Adam Neumann": ["Neumann"],
    "Bill Ackman": ["Ackman"],
    "Bitcoin": ["Bitcoins"],
    "BlackRock": ["BlackRock Inc."],
    "China": ["Chinese"],
    "Citi": ["Citibank"],
    "Deutsche Bank": ["Deutsche Bank AG"],
    "Donald Trump": ["Trump"],
    "Elon Musk": ["Elon", "Musk"],
    "Facebook": ["Facebook Inc."],
    "Federal Reserve": ["Fed"],
    "GameStop": ["GameStop Corp."],
    "Goldman Sachs": ["Goldman", "Goldman Sachs Group Inc."],
    "Greensill": ["Greensill Capital"],
    "JPMorgan": ["JPMorgan Chase & Co."],
    "Jack Dorsey": ["Dorsey"],
    "Kodak": ["Eastman Kodak Co."],
    "SEC": [
        "Securities and Exchange Commission",
        "U.S. Securities and Exchange Commission",
    ],
    "Softbank": ["SoftBank Group Corp."],
    "Tesla": ["Tesla Inc."],
    "U.S.": ["US", "America", "American"],
    "U.S. Treasury": ["Treasury"],
    "Warren Buffet": ["Buffet"],
}


class EntityExtractor:
    def __init__(self):
        print("Loading NLP model...")
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            print(
                "Failed to load spacy model, try installing with `python -m spacy download "
                "en_core_web_sm`."
            )

    def extract_entities(self, article: Article, clean: bool) -> Counter:
        doc = self.nlp(str(article))
        counter = Counter(
            (ent.text) for ent in doc.ents if ent.label_ in RELEVANT_ENT_LABELS
        )
        if clean:
            EntityExtractor.clean_entity_counter(counter)
        return counter

    @staticmethod
    def clean_entity_counter(counter):
        # Remove whitespace from outside of all keys.
        for key in list(counter.keys()):
            if key.strip() != key:
                root = key.strip()
                counter[root] += counter[key]
                del counter[key]

        # Replace possessive "'s" with root.
        for key in list(counter.keys()):
            if key[-2:] == "’s" or key[-2:] == "'s":
                root = key[:-2]
                counter[root] += counter[key]
                del counter[key]

        # Remove all unexpected special characters.
        for key in list(counter.keys()):
            root = re.sub('[^a-zA-Z0-9. -]+', '', key)
            if key != root:
                counter[root] += counter[key]
                del counter[key]

        # Remove prefix "the" if there are spaces.
        for key in list(counter.keys()):
            if " " in key and key[:4].lower() == "the ":
                root = key[4:]
                counter[root] += counter[key]
                del counter[key]

        # Replace all "UPPER CASE" with "Title Case".
        for key in list(counter.keys()):
            if " " in key and key.isupper():
                title_key = key.title()
                counter[title_key] += counter[key]
                del counter[key]

        # Apply custom replacements.
        inverted_replacements = defaultdict(list)
        for correction in ENT_REPLACEMENTS:
            for bad in ENT_REPLACEMENTS[correction]:
                inverted_replacements[bad] = correction
        for bad in inverted_replacements:
            count = counter[bad]
            counter[inverted_replacements[bad]] += count
            del counter[bad]
