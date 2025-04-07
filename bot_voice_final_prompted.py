
import asyncio
import os
import datetime
import subprocess
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import openai

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_KEY:
    raise ValueError("❗ Не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY")

openai.api_key = OPENAI_KEY
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

MAX_REQUESTS_PER_DAY = 20
user_limits = {}
user_state = {}

menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/утп")],
        [KeyboardButton(text="/ца")],
        [KeyboardButton(text="/контент")],
        [KeyboardButton(text="/скриптпродаж")],
        [KeyboardButton(text="/кейс")],
        [KeyboardButton(text="/проджект")],
        [KeyboardButton(text="/чат-бот")],
        [KeyboardButton(text="/финмодель")],
        [KeyboardButton(text="/созданиеКП")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Привет! Я помощник таргетологов, созданный @renafomicheva\n"
        "Напиши /меню, чтобы начать работу или просто текстом, что необходимо сделать 🔥\n\n"
        "📌 Не более 20 GPT-запросов в день на пользователя",
        reply_markup=menu_keyboard
    )

@dp.message(lambda message: message.voice or message.audio or message.document)
async def handle_voice_audio(message: Message):
    if message.voice:
        file_id = message.voice.file_id
        ogg_file = f"voice_{message.from_user.id}.ogg"
        mp3_file = f"voice_{message.from_user.id}.mp3"
    elif message.audio:
        file_id = message.audio.file_id
        ogg_file = f"audio_{message.from_user.id}.ogg"
        mp3_file = f"audio_{message.from_user.id}.mp3"
    elif message.document:
        file_id = message.document.file_id
        ogg_file = f"doc_{message.from_user.id}.ogg"
        mp3_file = f"doc_{message.from_user.id}.mp3"
    else:
        await message.answer("Не удалось обработать голосовое сообщение.")
        return

    file = await bot.get_file(file_id)
    await bot.download_file(file.file_path, ogg_file)
    subprocess.run(["ffmpeg", "-y", "-i", ogg_file, mp3_file], capture_output=True)

    with open(mp3_file, "rb") as audio_file:
        transcript = openai.Audio.transcribe("whisper-1", audio_file)

    await message.answer(f"🎧 Вы сказали: {transcript['text']}")
    await process_input(message, transcript["text"])

async def process_input(message: Message, text: str):
    user_id = message.from_user.id
    today = datetime.date.today()
    if user_id not in user_limits or user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"date": today, "count": 0}
    if user_limits[user_id]["count"] >= MAX_REQUESTS_PER_DAY:
        await message.answer("🚫 Превышен лимит запросов на сегодня. Попробуйте завтра.")
        return

    user_limits[user_id]["count"] += 1
    current_command = user_state.get(user_id)

    if not current_command:
        await message.answer("Сначала выберите команду из /меню, а потом отправьте текст.")
        return

    system_prompt = {
        "/утп": "Ты — опытный маркетолог и промпт-инженер. Проанализируй нишу и составь 10 уникальных УТП по указанному алгоритму.",
        "/ца": "Проанализируй целевую аудиторию, её боли, страхи, желания, сегменты и выдай 3 аватара клиентов.",
        "/контент": "Сделай анализ, УТП и контент-план на месяц для указанной ниши, 15 постов по заданным алгоритмам.",
        "/скриптпродаж": "Ты — эксперт по продажам. Определи этап сделки и составь ответ для клиента, чтобы продвинуть его к оплате.",
        "/кейс": "Составь кейс по рекламе: заголовок, с чем пришёл клиент, что сделали, цифры, причины успеха, вывод и призыв.",
        "/проджект": "Ты — проект-менеджер. Разбери эмоции клиента, сформулируй ответ в тоне поддержки и лидерства.",
        "/чат-бот": "Создай прогревающую воронку в чат-боте с этапами и текстами под указанную нишу.",
        "/финмодель": "Рассчитай финмодель и рост бизнеса, запроси недостающие данные, сделай выводы.",
        "/созданиеКП": "Сделай коммерческое предложение по шаблону: структура, выгоды, офферы, тон и оформление."
    }.get(current_command)

    if system_prompt:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": text}
            ],
            temperature=0.7
        )
        await message.answer(response.choices[0].message.content)
        user_state[user_id] = None  # очистим состояние
    else:
        await message.answer("Выберите команду из меню.")

@dp.message(Command("меню"))
async def show_menu(message: Message):
    await cmd_start(message)

@dp.message(Command("утп", "ца", "контент", "скриптпродаж", "кейс", "проджект", "чат-бот", "финмодель", "созданиеКП"))
async def set_mode(message: Message):
    user_state[message.from_user.id] = message.text
    await message.answer("Готово! А теперь пришлите, пожалуйста, текст или задачу, с которой мне работать 📝")

async def main():
    print("Бот запущен ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
