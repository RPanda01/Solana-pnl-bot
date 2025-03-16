import asyncio
import logging
import os
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from solana_analysis import analyze_wallet_from_file  # Импортируем функцию анализа CSV-файла

# Загружаем переменные из .env
load_dotenv()

# Замените на свой токен бота
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise ValueError("TOKEN is not set in the .env file")

# Создаём бота с MarkdownV2
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2"))
dp = Dispatcher()

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Папка для сохранения загруженных файлов
UPLOAD_FOLDER = "D://solAnal"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def escape_markdown(text: str) -> str:
    """Экранирует специальные символы MarkdownV2 для Telegram."""
    special_characters = r"_*[]()~`>#+-=|{}.!<>"
    return re.sub(f"([{re.escape(special_characters)}])", r"\\\1", text)

@dp.message(Command("start"))
async def start_command(message: Message):
    text = (
        "👋 Hello! I am a bot for analyzing Solana wallets.\n\n"
        "🔹 Send me a CSV file, and I will provide you with a PnL analysis for the last 1000 transactions."
    )
    await message.answer(escape_markdown(text))

@dp.message(lambda message: message.document)
async def handle_csv_file(message: Message):
    """Обрабатывает загруженный CSV-файл"""
    document = message.document

    # Проверяем, что файл имеет расширение .csv
    if not document.file_name.endswith(".csv"):
        await message.answer(escape_markdown("❌ Please send a CSV file"))
        return

    # Скачиваем файл
    file_path = os.path.join(UPLOAD_FOLDER, document.file_name)
    file_info = await bot.get_file(document.file_id)
    await bot.download_file(file_info.file_path, file_path)

    await message.answer(escape_markdown(f"🔄 Analyzing file `{document.file_name}`, please wait..."))

    # Анализируем CSV-файл
    try:
        result = analyze_wallet_from_file(file_path)
        await message.answer(result)  # Отправляем результат пользователю
    except Exception as e:
        await message.answer(escape_markdown(f"❌ Error analyzing file: `{str(e)}`"))

async def main():
    """Функция запуска бота"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

