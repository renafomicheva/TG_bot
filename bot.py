import asyncio
import os
import datetime
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
import openai

# Загрузка токенов
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN or not OPENAI_KEY:
    raise ValueError("❗ Не найден TELEGRAM_BOT_TOKEN или OPENAI_API_KEY")

openai.api_key = OPENAI_KEY
bot = Bot(token=TELEGRAM_TOKEN)
dp = Dispatcher()

# Лимиты и состояния
MAX_REQUESTS_PER_DAY = 20
user_limits = {}
user_state = {}

# Главное меню
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

@dp.message(Command("утп"))
async def handle_utp(message: Message):
    user_state[message.from_user.id] = "утп"
    await message.answer("Напиши нишу, по которой нужно составить 10 УТП.")

@dp.message(Command("ца"))
async def handle_ca(message: Message):
    user_state[message.from_user.id] = "ца"
    await message.answer("Укажи нишу — я составлю анализ ЦА и 3 аватара.")

@dp.message(Command("контент"))
async def handle_content(message: Message):
    user_state[message.from_user.id] = "контент"
    await message.answer("Укажи нишу — я создам контент-план + 15 постов.")

@dp.message(Command("скриптпродаж"))
async def handle_script(message: Message):
    user_state[message.from_user.id] = "скрипт"
    await message.answer("Напиши сообщение от клиента — я подскажу, как продвинуть его к оплате.")

@dp.message(Command("кейс"))
async def handle_case(message: Message):
    user_state[message.from_user.id] = "кейс"
    await message.answer("Отправь данные по шаблону:\n— Ниша\n— Клиент\n— Задача\n— Сложности\n— Что делали\n— Цифры\n— Эмоции клиента")

@dp.message(Command("проджект"))
async def handle_project(message: Message):
    user_state[message.from_user.id] = "проджект"
    await message.answer("Опиши ситуацию с клиентом — я подскажу, как грамотно ответить как Project-менеджер.")

@dp.message(Command("чат-бот"))
async def handle_chatbot(message: Message):
    user_state[message.from_user.id] = "чат-бот"
    await message.answer("Укажи нишу — и я создам воронку для чат-бота ВКонтакте.")

@dp.message(Command("финмодель"))
async def handle_finmodel(message: Message):
    user_state[message.from_user.id] = "финмодель"
    await message.answer("Отправь данные для финмодели: чек, рост, клиентов, сроки, расходы и т.д.")

@dp.message(Command("созданиеКП"))
async def handle_offer(message: Message):
    user_state[message.from_user.id] = "созданиеКП"
    await message.answer("Напиши: название проекта, особенности, ссылки и соцсети — я соберу КП в формате слайдов.")

@dp.message()
async def handle_text(message: Message):
    user_id = message.from_user.id
    today = datetime.date.today()

    if user_id not in user_limits or user_limits[user_id]["date"] != today:
        user_limits[user_id] = {"count": 0, "date": today}

    if user_limits[user_id]["count"] >= MAX_REQUESTS_PER_DAY:
        await message.answer("⛔ Лимит 20 GPT-запросов на сегодня исчерпан. Приходи завтра!")
        return

    context = user_state.get(user_id, None)
    prompt_user = message.text

    if context == "утп":
        prompt = f"Ты опытный маркетолог. Составь 10 УТП для ниши: {prompt_user}"
    elif context == "ца":
        prompt = f"Проанализируй ЦА для ниши: {prompt_user} по алгоритму /ца и выдай 3 аватара."
    elif context == "контент":
        prompt = f"Создай контент-план на месяц для ниши: {prompt_user}, как по инструкции /контент"
    elif context == "скрипт":
        prompt = f"""
Ты — опытный менеджер по продажам. Клиент написал: "{prompt_user}"

1. Определи, на каком этапе продаж находится клиент.
2. Объясни, что сейчас важно учитывать в разговоре.
3. Сформулируй уверенный, живой и человечный ответ, чтобы продвинуть его к оплате.

Не используй шаблоны. Пиши, как будто ты настоящий продавец со стержнем и эмпатией.
"""
    elif context == "кейс":
        prompt = f"Создай кейс по шаблону /кейс на основе данных: {prompt_user}"
    elif context == "проджект":
        prompt = f"Клиентская ситуация: {prompt_user}. Ответь как Project-менеджер по алгоритму /проджект."
    elif context == "чат-бот":
        prompt = f"Создай чат-бот воронку по шаблону /чат-бот для ниши: {prompt_user}"
    elif context == "финмодель":
        prompt = f"Построй финмодель по данным: {prompt_user} по шаблону /финмодель"
    elif context == "созданиеКП":
        prompt = f"Собери коммерческое предложение в формате слайдов на основе: {prompt_user}"
    else:
        prompt = f"Пользователь пишет: {prompt_user}. Ответь как маркетолог и ассистент таргетолога."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_tokens=500,
            top_p=0.9,
            frequency_penalty=0.2,
            presence_penalty=0.1
        )
        answer = response.choices[0].message.content
        await message.answer(answer)
        user_limits[user_id]["count"] += 1
        user_state[user_id] = None

    except Exception as e:
        await message.answer("⚠️ Ошибка при обращении к GPT:\n" + str(e))

async def main():
    print("Бот запущен ✅")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
