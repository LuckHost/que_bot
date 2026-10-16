import logging

from datetime import datetime

from data_files import funcs

from asyncio import sleep
from aiogram import Bot

from handlers.basic import ping_all_users

from config import TIMEZONE

CHECK_INTERVAL_SECONDS = 10


def next_occurrence(date: str, time: str, now: datetime) -> datetime:
    """Ближайший момент с днём месяца date и временем time ("ЧЧ.ММ"), не раньше начала текущей минуты."""
    parsed_time = datetime.strptime(time, "%H.%M")
    day = int(date)
    start = now.replace(second=0, microsecond=0)
    year, month = start.year, start.month
    for _ in range(13):
        try:
            candidate = start.replace(year=year, month=month, day=day,
                                      hour=parsed_time.hour, minute=parsed_time.minute)
        except ValueError:  # в этом месяце нет такого дня
            candidate = None
        if candidate is not None and candidate >= start:
            return candidate
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    raise ValueError(f'Invalid day of month: {date!r}')


async def process_timed_queues(bot: Bot, invalid_queues: set) -> None:
    now = datetime.now(TIMEZONE)
    for queue_name, queue_data in funcs.get_all_timed_queue_data():
        due = queue_data.get('due')
        if due is None:
            # Запись создана хэндлером (или старой версией бота) и хранит только день месяца и время.
            # Фиксируем срок один раз, иначе после наступления времени он «уезжал» бы на следующий месяц.
            try:
                due = next_occurrence(queue_data['date'], queue_data['time'], now).isoformat()
            except (KeyError, TypeError, ValueError):
                if queue_name not in invalid_queues:
                    invalid_queues.add(queue_name)
                    logging.warning(f'Timed queue {queue_name!r} has invalid date/time: {queue_data}')
                continue
            funcs.set_timed_queue_due(queue_name, due)
        logging.debug(f'Timed queue {queue_name!r} is due at {due}')
        if datetime.fromisoformat(due) <= now:
            funcs.delete_timed_queue(queue_name)
            if funcs.make_new_queue(queue_name) is True:
                await ping_all_users(bot, f"Создана очередь {queue_name} {queue_data['time']}")
            else:
                logging.warning(f'Timed queue {queue_name!r}: queue already exists, not created')


async def timed_queues_processor(bot: Bot):
    invalid_queues = set()
    while True:
        try:
            await process_timed_queues(bot, invalid_queues)
        except Exception:
            logging.exception('Timed queues check failed')
        await sleep(CHECK_INTERVAL_SECONDS)
