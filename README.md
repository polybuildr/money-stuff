# Analysing topics from Matt Levine's "Money Stuff"

There exists a fantastic newsletter called Money Stuff which can be found at https://www.bloomberg.com/opinion/authors/ARbTQlRLRjE/matthew-s-levine and the author can be found on Twitter at https://twitter.com/matt_levine.

Recently, I was idly wondering about the topics that Matt Levine writes about in Money Stuff and how they reflect trends in Finance news, in some way. I had some free time on my hands, hence this exploratory respository.

The code in this repository downloads Money Stuff emails from your Gmail account using the [Gmail API](https://developers.google.com/gmail/api/quickstart/python), runs the [Spacy NLP library](https://spacy.io/) on it and then plots a heatmap using [Seaborn](https://seaborn.pydata.org/)/[Matplotlib](https://matplotlib.org/).

There will (eventually) be a longer blog post about this project on my blog at https://blog.vghaisas.com.

## Setup

I was using Python 3.8.10 in a virtualenv while developing this project.

All the required packages can be installed using pip and the included `requirements.txt` file:

```
$ pip install -r requirements.txt
```

In order to download Money Stuff emails from Gmail, this project uses the Gmail API (see the [Python Quickstart](https://developers.google.com/gmail/api/quickstart/python)). In order to use the API, there are some additional setup steps mentioned in the quickstart: you'll need to [create a Google Cloud Platform project with the API enabled](https://developers.google.com/workspace/guides/create-project) and then [create authorization credentials for a desktop application](https://developers.google.com/workspace/guides/create-credentials). Download your client secret and save it as `credentials.json` in this repository.

## Usage

1. First up, download your Money Stuff emails using the Gmail API.

```
$ python download_emails.py
```

2. Then parse the downloads, extract entities from them, and pickle the results.

```
$ python main_pickle_data.py
```

3. Finally, read the pickled data and generate a heatmap plot.

```
$ python main_process_pickle.py
```
