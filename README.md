Telegramm Bot for queues control
---
![python version 3.9](https://img.shields.io/badge/python-3.9-blue)
![aiogram](https://img.shields.io/badge/aiogram-3.0-lightblue)

---

![image](https://github.com/egorgur/AsyncQueueBot/assets/122800013/d642fc9d-bb97-4eb4-a522-5238b0299294)
![image](https://github.com/egorgur/AsyncQueueBot/assets/122800013/1e2ca252-8371-45a3-b54c-5212e067cd99)
![image](https://github.com/egorgur/AsyncQueueBot/assets/122800013/67528c1a-3ddd-4d86-9c7b-cfa138ac37e2)
![image](https://github.com/egorgur/AsyncQueueBot/assets/122800013/d83f6e86-17d7-45ab-a6ba-4a4d5ce9e74e)
![image](https://github.com/egorgur/AsyncQueueBot/assets/122800013/710a7ac7-30ce-40eb-8fcc-323fbbd11a39)
![image](https://github.com/egorgur/AsyncQueueBot/assets/122800013/1c504727-28ad-4a16-be88-c4be0b0d0cf5)

---

## Деплой на Linux (systemd)

Нужен Python 3.10–3.14 (ограничение aiogram 3.31). Время отложенных очередей
считается в `BOT_TIMEZONE` (по умолчанию `Asia/Krasnoyarsk`), TZ сервера не важна.

### Установка

```bash
sudo useradd --system --home /opt/queuebot --shell /usr/sbin/nologin queuebot
sudo git clone <url репозитория> /opt/queuebot
cd /opt/queuebot
sudo python3 -m venv venv
sudo venv/bin/pip install -r requirements.txt
sudo chown -R queuebot:queuebot /opt/queuebot/core/downloads
```

### Настройки (.env)

```bash
sudo cp .env.example .env
sudo nano .env
sudo chown root:queuebot .env && sudo chmod 640 .env
```

| Переменная     | Обязательна | Описание |
|----------------|-------------|----------|
| `TOKEN`        | да  | токен бота от @BotFather |
| `ADMIN_ID`     | да  | id админов через запятую: `111,222`. Первому бот пишет о запуске/остановке |
| `BOT_TIMEZONE` | нет | таймзона отложенных очередей, по умолчанию `Asia/Krasnoyarsk` |
| `LOG_LEVEL`    | нет | `DEBUG` / `INFO` / `WARNING` / `ERROR`, по умолчанию `INFO` |
| `DATA_DIR`     | нет | каталог с json-данными, по умолчанию `core/data_files` (юнит задаёт `/var/lib/queuebot`) |

`settings.py` больше не используется: значения `TOKEN` и `ADMIN_ID` из него перенесите в `.env`
(список `ADMIN_ID = [111, 222]` записывается как `ADMIN_ID=111,222`).

Если бот не стартует из-за настроек, причина будет в логе одной строкой
(например, `Не задана переменная окружения TOKEN`).

### Запуск

```bash
sudo cp deploy/queuebot.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now queuebot
sudo systemctl status queuebot
journalctl -u queuebot -f          # логи
```

Локально (Windows/Linux) без systemd: заполнить `.env` в корне репозитория и
запустить `python core/main.py`.

### Где лежат данные

При запуске через юнит — в `/var/lib/queuebot` (`DATA_DIR`):

- `queue_list.json` — очереди и места в них;
- `timed_queues.json` — отложенные очереди;
- `users_info.json` — пользователи, писавшие боту `/start`.

Без `DATA_DIR` — в `core/data_files`. Файлы пишутся атомарно (временный файл + rename).
Бэкап — просто копия этих трёх файлов.

### Перенос данных со старого сервера

1. Остановите бота на старом сервере. Два экземпляра с одним токеном работать не могут,
   а данные разъедутся.
2. Скопируйте `core/data_files/queue_list.json`, `timed_queues.json` и `users_info.json`
   со старого сервера в `/var/lib/queuebot/` на новом:
   ```bash
   sudo systemctl stop queuebot
   sudo install -d -o queuebot -g queuebot /var/lib/queuebot
   sudo cp queue_list.json timed_queues.json users_info.json /var/lib/queuebot/
   sudo chown queuebot:queuebot /var/lib/queuebot/*.json
   sudo systemctl start queuebot
   ```
3. Формат файлов не изменился. В записи отложенных очередей бот при первой проверке дописывает
   поле `due` — точный момент создания. Для перенесённых записей этот момент считается от времени
   запуска нового бота: если время отложенной очереди прошло, пока бот был выключен, она сработает
   в этот день следующего месяца. После переноса проверьте список в «Управление очередями» →
   «Отложенные очереди».
