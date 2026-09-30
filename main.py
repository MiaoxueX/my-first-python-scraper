"""Command-line entry point for the configurable scraper."""

from core.config import ConfigError, ScraperConfig
from core.manager import ScraperManager
from crawlers.base import CrawlError
from exporters.base import ExportError


def main() -> int:
    """Run the configured scraping task and print beginner-friendly status messages."""
    try:
        config = ScraperConfig.from_file()
        print("Scraping started...")
        print(f"Target: {config.target}")
        print(f"Fields: {', '.join(config.fields)}")
        print(f"Count: {config.count}")
        print(f"Format: {config.output_format}")
        print(f"Output: {config.output}")
        print("\nScraping...")

        collected_count, output_path = ScraperManager(config).run()
        print(f"{collected_count} item(s) collected.")
        if collected_count < config.count:
            print(f"The website had fewer than the requested {config.count} item(s).")
        print("\nExport completed:")
        print(output_path)
        return 0
    except (ConfigError, CrawlError, ExportError) as error:
        print(f"Error: {error}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
