#!/usr/bin/env bash
set -e

# Переход в каталог скрипта (корень проекта)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

VENV_DIR=".venv"
REQUIREMENTS="requirements.txt"

# Создание виртуального окружения, если его нет
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment in $VENV_DIR..."
    if command -v python3 &>/dev/null; then
        python3 -m venv "$VENV_DIR"
    elif command -v python &>/dev/null; then
        python -m venv "$VENV_DIR"
    else
        echo "Error: Python not found. Install Python 3.10+ and try again." >&2
        exit 1
    fi
    echo "Virtual environment created."
fi

# Активация виртуального окружения
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# Установка зависимостей, если не установлены (проверка по aiogram)
if ! python -c "import aiogram" 2>/dev/null; then
    echo "Installing dependencies from $REQUIREMENTS..."
    pip install -r "$REQUIREMENTS"
    echo "Dependencies installed."
else
    # Обновление зависимостей при наличии requirements (опционально, быстро если всё установлено)
    pip install -q -r "$REQUIREMENTS" 2>/dev/null || true
fi

# Запуск бота
echo "Starting bot..."
exec python -m app.bot
