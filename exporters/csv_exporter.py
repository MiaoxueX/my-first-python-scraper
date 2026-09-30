"""CSV data exporter."""

import csv
from pathlib import Path

from exporters.base import BaseExporter, ExportError


class CsvExporter(BaseExporter):
    """Export records to a UTF-8 CSV file with a header row."""

    def export(self, items: list[dict[str, str]], fields: list[str], output_path: Path) -> Path:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", newline="", encoding="utf-8-sig") as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fields, extrasaction="ignore")
                writer.writeheader()
                writer.writerows(items)
        except OSError as error:
            raise ExportError(f"Could not write CSV file '{output_path}': {error}") from error
        return output_path
