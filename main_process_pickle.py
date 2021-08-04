import pickle
import pprint
import time
from collections import Counter, defaultdict
from datetime import date
from glob import glob
from typing import Dict, List

import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from article import Article
from entity_extractor import EntityExtractor

SKIP_ENTITIES = [
    "U.S.", # Obvious, so not particularly interesting .
    "Bloomberg", # Mostly referencing other articles?
    "Adam Neumann", # Mostly corresponds to WeWork.
    "Twitter", # Not very interesting as a topic.
]


def main():
    run_timestamp = int(time.time())
    latest_pickle = sorted(glob("articles-and-entities-*.pickle"))[-1]
    print(f"Using {latest_pickle} ...")
    with open(latest_pickle, "rb") as f:
        data = pickle.load(f)

    counters: List[Counter] = data["entity_counters"]
    articles: List[Article] = data["articles"]
    articles = [article for article in articles if article.date < date(2021, 8, 1)]

    for counter in counters:
        EntityExtractor.clean_entity_counter(counter)

    for counter in counters:
        total = sum(counter.values())
        for key in counter:
            # normalize as percent of total entity count
            val = counter[key]
            counter[key] = int(val * 100 / total)

    global total_counter
    total_counter = sum(counters, Counter())
    pprint.pprint(total_counter.most_common(50))

    heatmap = generate_heatmap(articles, counters, total_counter)
    save_plot_heatmap(heatmap, f"heatmap-{run_timestamp}.png")


def generate_heatmap(
    articles: List[Article],
    counters: List[Counter],
    total_counter: Counter,
    num_entities=23,
) -> dict:
    heatmap = {}
    for key, _ in total_counter.most_common(50):
        if len(heatmap) >= num_entities:
            break
        if key in SKIP_ENTITIES:
            continue
        counts_by_month = defaultdict(int)
        date_and_count = [
            (article.date, counter[key]) for article, counter in zip(articles, counters)
        ]
        for date, count in date_and_count:
            counts_by_month[date.replace(day=1)] += count
        heatmap[key] = counts_by_month
    return heatmap


def save_plot_heatmap(heatmap: Dict, filename):
    df = pd.DataFrame(heatmap).T
    sns.heatmap(
        df,
        cmap="Blues",
        robust=True,
        yticklabels=1,
        xticklabels=[date.strftime("%b '%y") for date in list(df)],
        # Hide the colorbar values, they don't really mean anything.
        cbar_kws={'format': ''},
    )
    plt.gcf().set_size_inches(12, 6.75)
    plt.tight_layout()
    print(f"Saving to {filename} ...")
    plt.savefig(filename)


if __name__ == "__main__":
    main()
