#!/bin/bash

echo "📦 Обновление проекта..."
cd /root/chistkanadomu-bot || exit
git pull

echo "🚀 Перезапуск бота..."
pkill -f bot.py
nohup python3 bot.py > bot.log 2>&1 &

echo "✅ Готово!"
