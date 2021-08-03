import datetime
import glob
import pickle
import re
import time
from typing import List

from article import Article
from email_parser import parse_html
from download_emails import DOWNLOAD_DIRECTORY_RELATIVE

articles: List[Article] = []


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
    
    pickle_file_name = f"articles-{run_timestamp}.pickle"
    print(f"Picking articles to {pickle_file_name} ... ", end='')
    with open(pickle_file_name, 'wb') as f:
        pickle.dump(articles, f)
    print('Done.')


if __name__ == "__main__":
    main()
