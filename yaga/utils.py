import re
from pathlib import Path
from typing import Any

import yaml
from jinja2 import Template


def load_yaml_file(path: str | Path) -> dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def merge_config_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(result.get(key), dict):
            result[key] = merge_config_dicts(result[key], value)
        else:
            result[key] = value
    return result


def process_api_template(template: str, context: dict[str, Any], strict: bool = False) -> str:
    pattern = re.compile(r"\{([^}]+)\}")

    def replace(match: re.Match[str]) -> str:
        path = match.group(1).split(".")
        value: Any = context
        for key in path:
            if isinstance(value, dict):
                value = value.get(key)
            else:
                value = getattr(value, key, None)
            if value is None:
                return match.group(0) if not strict else ""
        return str(value)

    return pattern.sub(replace, template)


def render_prompt(template: str | None, context: dict[str, Any]) -> str:
    if not template:
        return ""
    return Template(template).render(**context)
