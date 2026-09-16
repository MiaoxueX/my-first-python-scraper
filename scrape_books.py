import csv
from pathlib import Path

import requests
from bs4 import BeautifulSoup


URL = "http://books.toscrape.com/"


def scrape_books():
    response = requests.get(URL, timeout=10)
    response.raise_for_status()
    response.encoding = "utf-8"

    soup = BeautifulSoup(response.text, "html.parser")
    books = []

    for book in soup.select("article.product_pod"):
        title = book.select_one("h3 a")["title"]
        price = book.select_one("p.price_color").get_text(strip=True).replace("Â£", "£")
        books.append({"title": title, "price": price})

    return books


def save_to_csv(books):
    output_path = Path("data/books.csv")
    output_path.parent.mkdir(exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["title", "price"])
        writer.writeheader()
        writer.writerows(books)

    return output_path


def main():
    books = scrape_books()
    output_path = save_to_csv(books)
    print(f"成功抓取 {len(books)} 本图书。")
    print(f"CSV 文件已保存到：{output_path}")


if __name__ == "__main__":
    main()



