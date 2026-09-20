"""Configuration loading and validation for the scraper application."""

import json
from dataclasses import dataclass
from pathlib import Path


DEFAULT_FIELDS_BY_TARGET = {"books": ["title", "price"]}
SUPPORTED_FORMATS = {"csv", "json"}


class ConfigError(ValueError):
    """Raised when config.json is missing or contains invalid settings."""


@dataclass
class ScraperConfig:
    """Validated settings supplied by the user in config.json."""

    target: str
    fields: list[str]
    count: int
    output: Path
    output_format: str

    @classmethod
    def from_file(cls, config_path: str | Path = "config.json") -> "ScraperConfig":
        """Read and validate a JSON configuration file."""
        path = Path(config_path)
        if not path.is_file():
            raise ConfigError(f"Configuration file not found: {path}")

        try:
            with path.open("r", encoding="utf-8") as config_file:
                raw_config = json.load(config_file)
        except json.JSONDecodeError as error:
            raise ConfigError(f"Configuration file is not valid JSON: {error.msg}") from error
        except OSError as error:
            raise ConfigError(f"Could not read configuration file '{path}': {error}") from error

        if not isinstance(raw_config, dict):
            raise ConfigError("Configuration must be a JSON object.")

        return cls._from_dict(raw_config)

    @classmethod
    def _from_dict(cls, raw_config: dict) -> "ScraperConfig":
        required_keys = ("target", "count", "output", "format")
        missing_keys = [key for key in required_keys if key not in raw_config]
        if missing_keys:
            raise ConfigError("Missing required configuration: " + ", ".join(missing_keys))

        target = raw_config["target"]
        if not isinstance(target, str) or not target.strip():
            raise ConfigError("'target' must be a non-empty string.")
        target = target.strip().lower()
        if target not in DEFAULT_FIELDS_BY_TARGET:
            supported_targets = ", ".join(DEFAULT_FIELDS_BY_TARGET)
            raise ConfigError(f"Unsupported target '{target}'. Supported targets: {supported_targets}.")

        count = raw_config["count"]
        if isinstance(count, bool) or not isinstance(count, int) or count <= 0:
            raise ConfigError("'count' must be a positive integer.")

        output = raw_config["output"]
        if not isinstance(output, str) or not output.strip():
            raise ConfigError("'output' must be a non-empty file path.")

        output_format = raw_config["format"]
        if not isinstance(output_format, str) or output_format.lower() not in SUPPORTED_FORMATS:
            supported_formats = ", ".join(sorted(SUPPORTED_FORMATS))
            raise ConfigError(f"'format' must be one of: {supported_formats}.")

        fields = raw_config.get("fields", DEFAULT_FIELDS_BY_TARGET[target])
        if not isinstance(fields, list) or not fields or not all(isinstance(field, str) for field in fields):
            raise ConfigError("'fields' must be a non-empty list of field names.")
        if len(fields) != len(set(fields)):
            raise ConfigError("'fields' must not contain duplicate field names.")

        supported_fields = DEFAULT_FIELDS_BY_TARGET[target]
        unsupported_fields = [field for field in fields if field not in supported_fields]
        if unsupported_fields:
            raise ConfigError(
                f"Unsupported field(s) for target '{target}': {', '.join(unsupported_fields)}. "
                f"Supported fields: {', '.join(supported_fields)}."
            )

        return cls(
            target=target,
            fields=fields,
            count=count,
            output=Path(output),
            output_format=output_format.lower(),
        )
