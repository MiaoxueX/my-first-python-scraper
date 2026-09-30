"""Shared HTTP helpers for crawlers."""

from abc import ABC, abstractmethod

import requests


class CrawlError(RuntimeError):
    """Raised when a website cannot be fetched or parsed safely."""


class BaseCrawler(ABC):
    """Base class that provides requests, retries, and a common collect API."""

    def __init__(self, timeout: int = 10, retries: int = 2) -> None:
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()

    def get_page(self, url: str) -> str:
        """Fetch one page, retrying temporary network and HTTP failures."""
        last_error: requests.RequestException | None = None
        for attempt in range(1, self.retries + 2):
            try:
                response = self.session.get(url, timeout=self.timeout)
                response.raise_for_status()
                response.encoding = response.encoding or "utf-8"
                return response.text
            except requests.RequestException as error:
                last_error = error
                if attempt <= self.retries:
                    print(f"Request failed (attempt {attempt}); retrying...")

        raise CrawlError(
            f"Could not fetch '{url}' after {self.retries + 1} attempts: {last_error}"
        ) from last_error

    @abstractmethod
    def collect(self, count: int, fields: list[str]) -> list[dict[str, str]]:
        """Collect up to count records containing only the requested fields."""
