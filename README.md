\# My First Python Scraper



A beginner-friendly Python web scraping project.



\## What it does



This script scrapes the public practice website \[Books to Scrape](http://books.toscrape.com/).



It collects the title and price of the books shown on the home page, then saves the results to a CSV file.



\## Technologies



\- Python

\- requests

\- Beautiful Soup 4

\- csv (Python standard library)



\## Setup



Create and activate a virtual environment, then install the dependencies:



```powershell

python -m pip install -r requirements.txt

```



\## Run



```powershell

python scrape\_books.py

```



\## Output



The scraper creates this file:



```text

data/books.csv

```



The CSV file contains these columns:



\- `title`

\- `price`



\## Project structure



```text

.

├── .gitignore

├── README.md

├── requirements.txt

└── scrape\_books.py

```



\## Responsible scraping



This project uses Books to Scrape, a public website made for scraping practice. Always review a website's terms, robots.txt file, and rate limits before scraping a real website.

