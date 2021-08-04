import datetime
import glob
import pickle
import re
import time
from collections import Counter
from typing import List

from article import Article
from download_emails import DOWNLOAD_DIRECTORY_RELATIVE
from email_parser import parse_html
from entity_extractor import EntityExtractor


# Globals for easy access when running with `python -i`
articles: List[Article] = []
entity_counters: List[Counter] = []

def main():
    run_timestamp = int(time.time())
    paths = sorted(glob.glob(f"{DOWNLOAD_DIRECTORY_RELATIVE}*"))

    for file_path in paths:
        print(f"Parsing {file_path} ...")
        with open(file_path, "r") as f:
            html_doc = f.read()
        title = (
            re.sub(".*-Money-Stuff-", "", file_path)
            .replace(".html", "")
            .replace("-", " ")
        )
        date = datetime.date.fromisoformat(file_path[12:22])
        articles.append(parse_html(title, date, html_doc))

    extractor = EntityExtractor()
    for article in articles:
        print(f"Extracting entities from '{article.title}' ... ", end="", flush=True)
        counter = extractor.extract_entities(article, clean=False)
        entity_counters.append(counter)
        print("Done.")

    pickle_file_name = f"articles-and-entities-{run_timestamp}.pickle"
    print(f"Pickling articles and entity counters to {pickle_file_name} ... ", end="", flush=True)
    with open(pickle_file_name, "wb") as f:
        pickle.dump({"articles": articles, "entity_counters": entity_counters}, f)
    print("Done.")


if __name__ == "__main__":
    main()
