#!/bin/bash

echo "📦 Обновляем проект из GitHub..."
cd /root/chistkanadomu-bot || exit
git pull

echo "🔁 Перезапускаем бота..."
pkill -f bot.py
nohup python3 bot.py > bot.log 2>&1 &

echo "✅ Бот успешно обновлён и перезапущен!"
