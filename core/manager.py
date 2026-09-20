"""Application coordinator that connects configuration, crawlers, and exporters."""

from crawlers.books import BookCrawler
from exporters.csv_exporter import CsvExporter
from exporters.json_exporter import JsonExporter


class ScraperManager:
    """Run one configured scraping task from collection through export."""

    crawler_types = {"books": BookCrawler}
    exporter_types = {"csv": CsvExporter, "json": JsonExporter}

    def __init__(self, config) -> None:
        self.config = config

    def run(self) -> tuple[int, object]:
        """Collect configured records, export them, and return count and file path."""
        crawler = self.crawler_types[self.config.target]()
        exporter = self.exporter_types[self.config.output_format]()
        items = crawler.collect(self.config.count, self.config.fields)
        output_path = exporter.export(items, self.config.fields, self.config.output)
        return len(items), output_path
