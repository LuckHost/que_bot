import json
import os
import tempfile

from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent


def read_json(file_name: str) -> (list, dict):
    with open(DATA_DIR / file_name, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json(file_name: str, data: (list, dict)) -> None:
    # Пишем во временный файл рядом и атомарно подменяем им исходный,
    # чтобы падение посреди записи не оставило обрезанный JSON
    fd, tmp_path = tempfile.mkstemp(dir=DATA_DIR, prefix=f'.{file_name}.', suffix='.tmp')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, DATA_DIR / file_name)
    except BaseException:
        try:
            os.unlink(tmp_path)
        except OSError:
            pass
        raise
