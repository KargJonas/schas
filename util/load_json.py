import json
from pathlib import Path
from typing import Any


class DotDict:
    def __init__(self, dictionary):
        for key, value in dictionary.items():
            if isinstance(value, dict):
                setattr(self, key, DotDict(value))
            else:
                setattr(self, key, value)


# Loads JSON files relative to the project root
def load_json(file_name: str) -> Any:
    file_path = Path(__file__).parent.parent / file_name
    if not file_path.is_file():
        raise FileNotFoundError(f"File '{file_name}' not found!")
    with open(file_path) as file:
        return DotDict(json.load(file))