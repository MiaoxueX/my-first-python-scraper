"""Offline tests for configuration, pagination, exports, and error messages."""

import csv
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.config import ConfigError, ScraperConfig
from core.manager import ScraperManager
from crawlers.books import BookCrawler


FIRST_PAGE = """
<article class='product_pod'><h3><a title='First book'></a></h3><p class='price_color'>£10.00</p></article>
<article class='product_pod'><h3><a title='Second book'></a></h3><p class='price_color'>£20.00</p></article>
<li class='next'><a href='catalogue/page-2.html'>next</a></li>
"""
FIRST_AND_LAST_PAGE = """
<article class='product_pod'><h3><a title='First book'></a></h3><p class='price_color'>£10.00</p></article>
<article class='product_pod'><h3><a title='Second book'></a></h3><p class='price_color'>£20.00</p></article>
"""
SECOND_PAGE = """
<article class='product_pod'><h3><a title='Third book'></a></h3><p class='price_color'>£30.00</p></article>
"""


class ScraperTests(unittest.TestCase):
    def make_config(self, directory: Path, **overrides) -> ScraperConfig:
        settings = {
            "target": "books",
            "fields": ["title", "price"],
            "count": 5,
            "output": str(directory / "nested" / "books.csv"),
            "format": "csv",
        }
        settings.update(overrides)
        path = directory / "config.json"
        path.write_text(json.dumps(settings), encoding="utf-8")
        return ScraperConfig.from_file(path)

    def test_book_crawler_respects_count_fields_and_pagination(self):
        crawler = BookCrawler()
        with patch.object(crawler, "get_page", side_effect=[FIRST_PAGE, SECOND_PAGE]) as get_page:
            books = crawler.collect(3, ["title"])
        self.assertEqual(books, [{"title": "First book"}, {"title": "Second book"}, {"title": "Third book"}])
        self.assertEqual(get_page.call_count, 2)

    def test_book_crawler_collects_twenty_items(self):
        nodes = "".join(
            f"<article class='product_pod'><h3><a title='Book {number}'></a></h3>"
            f"<p class='price_color'>£{number}.00</p></article>"
            for number in range(1, 21)
        )
        crawler = BookCrawler()
        with patch.object(crawler, "get_page", return_value=nodes):
            books = crawler.collect(20, ["title", "price"])
        self.assertEqual(len(books), 20)
        self.assertEqual(books[0], {"title": "Book 1", "price": "£1.00"})
        self.assertEqual(books[-1], {"title": "Book 20", "price": "£20.00"})

    def test_default_book_fields_are_used_when_omitted(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            self.make_config(directory)
            raw = json.loads((directory / "config.json").read_text(encoding="utf-8"))
            raw.pop("fields")
            (directory / "config.json").write_text(json.dumps(raw), encoding="utf-8")
            config = ScraperConfig.from_file(directory / "config.json")
        self.assertEqual(config.fields, ["title", "price"])

    def test_unsupported_field_has_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ConfigError, "Unsupported field.*rating"):
                self.make_config(Path(temporary_directory), fields=["title", "rating"])

    def test_unsupported_format_has_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            with self.assertRaisesRegex(ConfigError, "format.*csv, json"):
                self.make_config(Path(temporary_directory), format="xml")

    def test_missing_required_configuration_has_clear_error(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "config.json"
            path.write_text('{"target": "books"}', encoding="utf-8")
            with self.assertRaisesRegex(ConfigError, "Missing required configuration"):
                ScraperConfig.from_file(path)

    def test_manager_exports_requested_fields_to_csv_and_creates_directory(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            config = self.make_config(directory, count=5, fields=["title"])
            with patch.object(BookCrawler, "get_page", return_value=FIRST_AND_LAST_PAGE):
                count, output = ScraperManager(config).run()
            self.assertEqual(count, 2)
            self.assertTrue(output.is_file())
            with output.open(encoding="utf-8-sig", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(rows, [{"title": "First book"}, {"title": "Second book"}])

    def test_manager_exports_requested_fields_to_json(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            directory = Path(temporary_directory)
            output = directory / "created" / "books.json"
            config = self.make_config(directory, output=str(output), format="json", fields=["price"])
            with patch.object(BookCrawler, "get_page", return_value=FIRST_AND_LAST_PAGE):
                count, saved_path = ScraperManager(config).run()
            self.assertEqual(count, 2)
            self.assertEqual(json.loads(saved_path.read_text(encoding="utf-8")), [{"price": "£10.00"}, {"price": "£20.00"}])


if __name__ == "__main__":
    unittest.main()
