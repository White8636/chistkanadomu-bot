#!/bin/bash
set -e

cd /root/chistkanadomu-bot || exit 1
echo "📦 git pull..."
git pull

# Загружаем переменные окружения из .env (если файл есть)
if [ -f ".env" ]; then
  set -a
  . ./.env
  set +a
fi

echo "🔁 restart bot..."
pkill -f bot.py || true
nohup python3 bot.py > bot.log 2>&1 &
echo "✅ done"
