import pandas as pd
import os
import re
import logging

# Включаем логирование
logging.basicConfig(level=logging.INFO)


def escape_markdown(text: str) -> str:
    # Список символов, которые нужно экранировать
    special_characters = r"[_*`\[\]()~>#+\-=|{}.!]"

    # Экранируем каждый специальный символ
    escaped_text = re.sub(f'([{special_characters}])', r'\\\1', text)
    
    return escaped_text

def analyze_wallet_from_file(file_path: str) -> str:
    """Анализирует загруженный CSV-файл и возвращает результат анализа."""
    try:
        # Проверяем, что файл был скачан
        if not os.path.exists(file_path):
            return f"❌ Error: File for wallet `{wallet}` not found"
        
        # Загружаем CSV-файл в DataFrame
        df = pd.read_csv(file_path)

        # Проверяем наличие обязательных колонок
        required_columns = {"Time", "Flow", "Value", "TokenAddress"}
        if not required_columns.issubset(df.columns):
            return escape_markdown("❌ Error: Required columns are missing in the CSV file")

        # Конвертируем временные метки в читаемый формат
        df["Time"] = pd.to_datetime(df["Time"], unit="s")
        df["Date"] = df["Time"].dt.date

        # Фильтруем только транзакции SOL
        SOL_TOKEN_ADDRESS = "SOL"
        df_sol = df[df["TokenAddress"] == SOL_TOKEN_ADDRESS]

        # Разделяем входящие и исходящие транзакции
        inflows = df_sol[df_sol["Flow"] == "in"]
        outflows = df_sol[df_sol["Flow"] == "out"]

        # Рассчитываем PnL
        total_in = inflows["Value"].sum()
        total_out = outflows["Value"].sum()
        total_pnl = total_in - total_out

        # PnL по дням
        daily_in = inflows.groupby("Date")["Value"].sum()
        daily_out = outflows.groupby("Date")["Value"].sum()
        daily_pnl = (daily_in - daily_out).fillna(0)

        # Самый прибыльный и убыточный дни
        best_day = daily_pnl.idxmax() if not daily_pnl.empty else "NA"
        best_pnl = daily_pnl.max() if not daily_pnl.empty else 0
        worst_day = daily_pnl.idxmin() if not daily_pnl.empty else "NA"
        worst_pnl = daily_pnl.min() if not daily_pnl.empty else 0

        # Подсчет комиссий
        fee_threshold = 1
        fees = df_sol[(df_sol["Flow"] == "out") & (df_sol["Value"] <= fee_threshold)]
        total_fees = fees["Value"].sum()
        daily_fees = fees.groupby("Date")["Value"].sum().fillna(0)

        # Чистый PnL без учета комиссий
        daily_pnl_no_fees = daily_pnl + daily_fees

        # Формируем отчет по дням
        daily_report = "\n".join([
            f"{date} {pnl:.6f}$ {pnl_no_fees:.6f}$ {fees:.6f}$"
            for date, pnl, pnl_no_fees, fees in zip(daily_pnl.index, daily_pnl, daily_pnl_no_fees, daily_fees)
        ])

        # Формируем итоговый текст
        result_text = (
            f"✅ *Analysis completed*\n\n"
            f"📊 *Solana wallet transaction analysis:*\n"
            f"💰 *Total inflow:* `{total_in:.6f}$`\n"
            f"💸 *Total outflow:* `{total_out:.6f}$`\n"
            f"📉 *Net PnL:* `{total_pnl:.6f}$`\n\n"
            f"📅 *PnL by days:*\n```\nDate | PnL with fees | PnL without fees | Total fees\n{daily_report}\n```\n\n"
            f"✅ *Best day:* `{best_day} ({best_pnl:.6f}$)`\n"
            f"❌ *Worst day:* `{worst_day} ({worst_pnl:.6f}$)`\n\n"
            f"🏦 *Total fees:* `{total_fees:.6f}$`"
        )

        os.remove(file_path)  # Удаляем скачанный файл после анализа
        
        return escape_markdown(result_text)

    except Exception as e:
         return escape_markdown(f"❌ Error analyzing file: `{str(e)}`")

