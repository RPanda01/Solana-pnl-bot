import pandas as pd  # Для работы с таблицами (DataFrame)
import datetime  # Для работы с датами
import os  # Для работы с файловой системой
from solscan_downloader import download_solscan_csv
import re

def escape_markdown(text: str) -> str:
    # Список символов, которые нужно экранировать
    special_characters = r"[_*`\[\]()~>#+\-=|{}.!]"

    # Экранируем каждый специальный символ
    escaped_text = re.sub(f'([{special_characters}])', r'\\\1', text)
    
    return escaped_text

def analyze_wallet(wallet: str) -> str:
    # Путь для сохранения файла
    save_path = f"D:\\solAnal\\trans_{wallet}.csv"

    # Загружаем файл с помощью solscan_downloader.py
    download_solscan_csv(wallet, save_path)

    # Проверяем, что файл был скачан
    if not os.path.exists(save_path):
        return f"❌ Ошибка: файл для кошелька `{wallet}` не найден"

    # Загружаем CSV-файл в DataFrame
    df = pd.read_csv(save_path)

    # Проверяем, есть ли нужные колонки
    required_columns = {"Time", "Flow", "Value", "TokenAddress"}
    if not required_columns.issubset(df.columns):
        return "❌ Ошибка: отсутствуют обязательные колонки в CSV файле"

    # Конвертируем временные метки в читаемый формат
    df["Time"] = pd.to_datetime(df["Time"], unit="s")
    df["Date"] = df["Time"].dt.date  # Создаем отдельную колонку с датой

    # Фильтруем только сделки с SOL
    SOL_TOKEN_ADDRESS = "SOL"
    df_sol = df[df["TokenAddress"] == SOL_TOKEN_ADDRESS]

    # Разделяем входящие и исходящие транзакции
    inflows = df_sol[df_sol["Flow"] == "in"]
    outflows = df_sol[df_sol["Flow"] == "out"]

    # Общий PnL
    total_in = inflows["Value"].sum()
    total_out = outflows["Value"].sum()
    total_pnl = total_in - total_out

    # PnL по дням
    daily_in = inflows.groupby("Date")["Value"].sum()
    daily_out = outflows.groupby("Date")["Value"].sum()
    daily_pnl = (daily_in - daily_out).fillna(0)

    # Самый прибыльный и убыточный дни
    best_day = daily_pnl.idxmax()
    best_pnl = daily_pnl.max()
    worst_day = daily_pnl.idxmin()
    worst_pnl = daily_pnl.min()

    # Подсчет комиссий
    fee_threshold = 1
    fees = df_sol[(df_sol["Flow"] == "out") & (df_sol["Value"] <= fee_threshold)]
    total_fees = fees["Value"].sum()
    daily_fees = fees.groupby("Date")["Value"].sum().fillna(0)

    # Чистый PnL без учета комиссий
    daily_pnl_no_fees = daily_pnl + daily_fees

    # Формируем отчет по дням
    daily_report = "\n".join([
        f"{date} {pnl:.6f} $ {pnl_no_fees:.6f} $ {fees:.6f} $"
        for date, pnl, pnl_no_fees, fees in zip(daily_pnl.index, daily_pnl, daily_pnl_no_fees, daily_fees)
    ])

    # Формируем итоговый текст с экранированием символа !
    result_text = (
        f"✅ *Анализ завершён*\n\n"
        f"📊 *Анализ транзакций по Solana кошельку:*\n"
        f"💰 *Общий доход:* `{total_in:.6f} $`\n"
        f"💸 *Общий расход:* `{total_out:.6f} $`\n"
        f"📉 *Чистый PnL:* `{total_pnl:.6f} $`\n\n"
        f"📅 *PnL по дням:*\n```\nDate PnL без комиссии Сумма комиссий\n{daily_report}\n```\n\n"
        f"✅ *Самый прибыльный день:* `{best_day}` \\(\\+{best_pnl:.6f} $\\)\n"
        f"❌ *Самый убыточный день:* `{worst_day}` \\({worst_pnl:.6f} $\\)\n\n"
        f"🏦 *Сумма комиссий:* `{total_fees:.6f} $`"
    )

    # Возвращаем результат с экранированным текстом
    return escape_markdown(result_text)

