"""Common exporter interface."""

from abc import ABC, abstractmethod
from pathlib import Path


class ExportError(RuntimeError):
    """Raised when collected data cannot be written to the chosen output file."""


class BaseExporter(ABC):
    """Base interface for data exporters."""

    @abstractmethod
    def export(self, items: list[dict[str, str]], fields: list[str], output_path: Path) -> Path:
        """Write items to output_path and return the path."""
