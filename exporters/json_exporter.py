"""JSON data exporter."""

import json
from pathlib import Path

from exporters.base import BaseExporter, ExportError


class JsonExporter(BaseExporter):
    """Export records to a readable UTF-8 JSON file."""

    def export(self, items: list[dict[str, str]], fields: list[str], output_path: Path) -> Path:
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with output_path.open("w", encoding="utf-8") as json_file:
                json.dump(items, json_file, ensure_ascii=False, indent=2)
                json_file.write("\n")
        except OSError as error:
            raise ExportError(f"Could not write JSON file '{output_path}': {error}") from error
        return output_path
