# Запуск бота как сервиса systemd (автозапуск на сервере)

Инструкция по управлению ботом через systemd: автозапуск при старте сервера, запуск, остановка и перезагрузка.

## Расположение и содержимое unit-файла

**Путь к файлу сервиса:** `/etc/systemd/system/infobot.service`

Создать или отредактировать файл (требуются права root):

```bash
sudo nano /etc/systemd/system/infobot.service
```

**Содержимое файла:**

```ini
[Unit]
Description=Info Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/home/bots/InfoBot
ExecStart=/home/bots/InfoBot/run.sh
Restart=always

[Install]
WantedBy=multi-user.target
```

Сохраните файл (в nano: `Ctrl+O`, Enter, `Ctrl+X`), затем выполните перезагрузку конфигурации systemd:

```bash
sudo systemctl daemon-reload
```

---

## Добавление в автозапуск

Включить запуск бота при каждой загрузке сервера:

```bash
sudo systemctl enable infobot.service
```

Проверить, что автозапуск включён:

```bash
sudo systemctl is-enabled infobot
```

Должно вывести: `enabled`.

---

## Запуск бота

Запустить сервис (сейчас, без перезагрузки сервера):

```bash
sudo systemctl start infobot
```

Проверить статус:

```bash
sudo systemctl status infobot
```

В выводе должно быть `Active: active (running)`. Выход из просмотра статуса: клавиша `q`.

---

## Остановка бота

Остановить сервис:

```bash
sudo systemctl stop infobot
```

Проверить, что сервис остановлен:

```bash
sudo systemctl status infobot
```

Должно быть `Active: inactive (dead)`.

---

## Перезагрузка бота

Перезапустить сервис (удобно после обновления кода или правки конфигов):

```bash
sudo systemctl restart infobot
```

Проверить статус после перезапуска:

```bash
sudo systemctl status infobot
```

---

## Просмотр логов

Логи вывода бота (stdout/stderr) через journald:

```bash
sudo journalctl -u infobot.service -f
```

`-f` — показывать новые строки в реальном времени (выход: `Ctrl+C`).

Последние 100 строк без «хвоста»:

```bash
sudo journalctl -u infobot.service -n 100
```

Логи за сегодня:

```bash
sudo journalctl -u infobot.service --since today
```

Файловые логи бота (loguru) по-прежнему пишутся в каталог `app/logs/` внутри проекта.

---

## Краткая шпаргалка

| Действие | Команда |
|----------|--------|
| Включить автозапуск | `sudo systemctl enable infobot` |
| Запустить | `sudo systemctl start infobot` |
| Остановить | `sudo systemctl stop infobot` |
| Перезапустить | `sudo systemctl restart infobot` |
| Статус | `sudo systemctl status infobot` |
| Логи в реальном времени | `sudo journalctl -u infobot -f` |

После изменения unit-файла всегда выполняйте:

```bash
sudo systemctl daemon-reload
```

затем при необходимости:

```bash
sudo systemctl restart infobot
```
