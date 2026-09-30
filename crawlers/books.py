"""Crawler for the public Books to Scrape practice website."""

from urllib.parse import urljoin

from bs4 import BeautifulSoup

from crawlers.base import BaseCrawler, CrawlError


class BookCrawler(BaseCrawler):
    """Collect book titles and prices from Books to Scrape, following pages as needed."""

    start_url = "https://books.toscrape.com/"
    supported_fields = ("title", "price")

    def collect(self, count: int, fields: list[str]) -> list[dict[str, str]]:
        """Return up to count books, following the site's next-page links."""
        books: list[dict[str, str]] = []
        next_url: str | None = self.start_url

        while next_url and len(books) < count:
            page_html = self.get_page(next_url)
            soup = BeautifulSoup(page_html, "html.parser")
            book_nodes = soup.select("article.product_pod")
            if not book_nodes:
                raise CrawlError("Could not find book data on the page. The website layout may have changed.")

            for book_node in book_nodes:
                if len(books) >= count:
                    break
                books.append(self._parse_book(book_node, fields))

            next_link = soup.select_one("li.next > a")
            next_url = urljoin(next_url, next_link["href"]) if next_link else None

        return books

    @staticmethod
    def _parse_book(book_node, fields: list[str]) -> dict[str, str]:
        """Turn one book HTML node into a dictionary containing requested fields."""
        title_link = book_node.select_one("h3 a")
        price_node = book_node.select_one("p.price_color")
        if title_link is None or price_node is None or not title_link.get("title"):
            raise CrawlError("Could not parse a book title or price. The website layout may have changed.")

        available_data = {
            "title": title_link["title"],
            "price": price_node.get_text(strip=True).replace("Â£", "£"),
        }
        return {field: available_data[field] for field in fields}
