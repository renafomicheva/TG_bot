# Telegram Bot GPT (Render-ready)

Бот, который работает в Telegram и подключён к GPT (OpenAI).  
Поддерживает команды, голосовые сообщения и ограничения на использование.

## 🚀 Как запустить на Render

1. Подключи GitHub к Render.com
2. Создай новый Background Worker
3. Укажи:
   - Build command: `pip install -r requirements.txt`
   - Start command: `python bot_voice_final_prompted.py`
4. В разделе Environment добавь:
   - `TELEGRAM_BOT_TOKEN`
   - `OPENAI_API_KEY`
