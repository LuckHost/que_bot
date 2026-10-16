import json

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent


def read_json(file_name: str) -> (list, dict):
    with open(DATA_DIR / file_name, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(file_name: str, data: (list, dict)) -> None:
    with open(DATA_DIR / file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
