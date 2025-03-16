import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties  # Добавляем настройку по умолчанию
from solana_analysis import analyze_wallet  # Импортируем функцию анализа кошелька

# Замените на свой токен бота
TOKEN = "8023030097:AAHan7dwzp4RiWpHf50duqEEEZX9-puCm_Y"

# Создаём бота с MarkdownV2
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="MarkdownV2"))
dp = Dispatcher()

# Включаем логирование
logging.basicConfig(level=logging.INFO)

@dp.message(Command("start"))
async def start_command(message: Message):
    await message.answer(
        "👋 Привет\\! Я бот для анализа кошельков Solana\n\n"
        "🔹 Отправьте мне адрес кошелька, и я предоставлю вам анализ PnL за предыдущую 1000 транзакций"
    )

@dp.message()
async def handle_wallet(message: Message):
    wallet = message.text.strip()

    # Проверяем, что адрес кошелька корректный
    if len(wallet) < 32 or len(wallet) > 44:
        await message.answer("❌ Неверный адрес кошелька\\! Попробуйте снова\.")
        return

    await message.answer(f"🔄 Анализируем кошелек `{wallet}`, подождите\.\.\.")

    try:
        # Запускаем анализ кошелька
        result = analyze_wallet(wallet)

        # Отправляем результат пользователю с экранированными символами
        await message.answer(f"✅ *Анализ завершён\\!*\n\n{result}")

    except Exception as e:
        await message.answer(f"❌ Произошла ошибка: `{str(e)}`")

async def main():
    """Функция запуска бота"""
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


