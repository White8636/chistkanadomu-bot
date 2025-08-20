#!/bin/bash
set -Eeuo pipefail

DATE="$(date +%Y%m%d_%H%M%S)"
BASE_DIR="/opt/himchik"
BACKUP_DIR="/opt/backups"
BRANCH="main"
SERVICE_NAME="chistkanadomu-bot"   # если имя сервиса другое — поменяй

echo "🚀 [$DATE] Начинаем деплой..."

# 0) .env (если есть)
if [[ -f "$BASE_DIR/.env" ]]; then
  set -a
  . "$BASE_DIR/.env"
  set +a
fi

# 1) Бэкап (ASCII-кавычки и опции ДО путей!)
echo "💾 Создание бэкапа..."
mkdir -p "$BACKUP_DIR"
tar -czf "$BACKUP_DIR/himchik_backup_${DATE}.tar.gz" --exclude="$BACKUP_DIR" "$BASE_DIR" || true
echo "✅ Бэкап: $BACKUP_DIR/himchik_backup_${DATE}.tar.gz"

# 2) Код из GitHub — жёсткая синхронизация
echo "🔄 Обновление кода из GitHub..."
cd "$BASE_DIR"
git fetch origin "$BRANCH"
git reset --hard "origin/$BRANCH"

# 3) Зависимости
echo "📦 Обновление зависимостей..."
if [[ -d "venv" ]]; then
  source venv/bin/activate
else
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
fi
if [[ -f "requirements.txt" ]]; then
  pip install -r requirements.txt
fi
deactivate

# 4) Перезапуск бота
if command -v systemctl >/dev/null 2>&1 && systemctl status "$SERVICE_NAME" >/dev/null 2>&1; then
  echo "🔁 Перезапуск systemd-сервиса..."
  sudo systemctl restart "$SERVICE_NAME"
else
  echo "🔁 Перезапуск через nohup..."
  pkill -f bot.py || true
  nohup "$BASE_DIR/venv/bin/python" "$BASE_DIR/bot.py" > "$BASE_DIR/bot.log" 2>&1 &
fi

# 5) Telegram-уведомление (без HTTP-проверок сайта)
NOTIFY_TOKEN="${TELEGRAM_NOTIFY_TOKEN:-${BOT_TOKEN:-}}"
NOTIFY_CHAT="${TELEGRAM_NOTIFY_CHAT_ID:-${ADMIN_CHAT_ID:-}}"
if [[ -n "${NOTIFY_TOKEN:-}" && -n "${NOTIFY_CHAT:-}" ]]; then
  MSG="$(printf "🚀 Himchik: деплой завершён\n🕒 %s\n📦 %s" "$(date '+%F %T')" "himchik_backup_${DATE}.tar.gz")"
  curl -s --max-time 10 -X POST "https://api.telegram.org/bot${NOTIFY_TOKEN}/sendMessage" \
       -d chat_id="${NOTIFY_CHAT}" -d text="${MSG}" >/dev/null || true
fi

echo "🏁 Готово."
