#!/usr/bin/env bash
# скачиваем uv и запускаем команду установки зависимостей
curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/.local/bin/env
make install

# Создаем таблицы в базе данных (если есть DATABASE_URL)
if [ -n "$DATABASE_URL" ]; then
    psql -a -d "$DATABASE_URL" -f database.sql
fi