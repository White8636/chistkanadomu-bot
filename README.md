# Chistka Na Domu Bot

## Установка и запуск

1. Клонируйте проект.
2. Установите зависимости:
    ```
    pip install -r requirements.txt
   ```
3. Создайте файл `.env` на основе `.env.example` и заполните значения:
   ```
   BOT_TOKEN=<токен вашего бота>
   ADMIN_CHAT_ID=<ваш Telegram ID>
   ```
   Затем загрузите переменные окружения, например:
   ```
   source .env
   ```

4. Запустите:
   ```
   python3 bot.py
   ```