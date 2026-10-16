import os

from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent

# Переменные, уже заданные в окружении (например, systemd EnvironmentFile), не перезаписываются
load_dotenv(BASE_DIR / '.env')


def _required(name: str) -> str:
    value = os.getenv(name, '').strip()
    if not value:
        raise SystemExit(f'Не задана переменная окружения {name}. '
                         f'Задайте её в окружении или в файле {BASE_DIR / ".env"} (пример: .env.example)')
    return value


def _parse_admin_ids(value: str) -> list:
    try:
        ids = [int(part) for part in value.split(',') if part.strip()]
    except ValueError:
        raise SystemExit(f'ADMIN_ID должен быть списком числовых id через запятую, получено: {value!r}')
    if not ids:
        raise SystemExit('ADMIN_ID должен содержать хотя бы один id')
    return ids


TOKEN = _required('TOKEN')
ADMIN_ID = _parse_admin_ids(_required('ADMIN_ID'))
