import pandas as pd  # Для работы с таблицами (DataFrame)
import datetime  # Для работы с датами
import os  # Для работы с файловой системой
from solscan_downloader import download_solscan_csv

# Ваш кошелек
wallet = "3mQKQtTvzqMSHk9BMewU98G1uNZqywkoCGimt2k7XdVW"  # Замените на свой кошелек

def analyze_wallet(wallet: str) -> str:
   
    # Загружаем файл с помощью solscan_downloader.py
    download_solscan_csv(wallet)
    file_path=f"trans_{wallet}.csv"

    # Проверяем, что файл был скачан
    if file_path is None or not os.path.exists(file_path):
        print(f"Ошибка: файл для кошелька {wallet} не был загружен или не найден!")
        exit()

    # Теперь файл доступен по пути file_path, например:
    print(f"Файл успешно загружен: {file_path}")

    # Загружаем CSV-файл в DataFrame
    df = pd.read_csv(file_path)

    # Проверяем, есть ли нужные колонки
    required_columns = {"Time", "Flow", "Value", "TokenAddress"}
    if not required_columns.issubset(df.columns):
        print("Ошибка: отсутствуют обязательные колонки в CSV-файле!")
        exit()

    # Конвертируем временные метки в читаемый формат
    df["Time"] = pd.to_datetime(df["Time"], unit="s")
    df["Date"] = df["Time"].dt.date  # Создаем отдельную колонку с датой


    # Фильтруем только сделки с SOL (SOL Token Address)
    wSOL_TOKEN_ADDRESS = "So11111111111111111111111111111111111111112"
    SOL_TOKEN_ADDRESS = "SOL"  # Адрес wSOL
    #df_sol = df[df["TokenAddress"].isin([SOL_TOKEN_ADDRESS, wSOL_TOKEN_ADDRESS])]
    df_sol = df[df["TokenAddress"].isin([SOL_TOKEN_ADDRESS])]


    # Разделяем входящие и исходящие транзакции
    inflows = df_sol[df_sol["Flow"] == "in"]
    outflows = df_sol[df_sol["Flow"] == "out"]

    # ✅ Общий PnL (разница между входящими и исходящими средствами)
    total_in = inflows["Value"].sum()  # Все поступления
    total_out = outflows["Value"].sum()  # Все расходы
    total_pnl = total_in - total_out  # Чистая прибыль/убыток

    # ✅ PnL по дням
    daily_in = inflows.groupby("Date")["Value"].sum()
    daily_out = outflows.groupby("Date")["Value"].sum()
    daily_pnl = (daily_in - daily_out).fillna(0)  # Заполняем NaN нулями

    # ✅ Определяем самый прибыльный и самый убыточный дни
    best_day = daily_pnl.idxmax()
    best_pnl = daily_pnl.max()
    worst_day = daily_pnl.idxmin()
    worst_pnl = daily_pnl.min()

    # ✅ Подсчет комиссий (мелкие исходящие транзакции с value < 1 доллар)
    fee_threshold = 1  # Порог для комиссий (например, все транзакции меньше 1 доллара считаются комиссиями)

    # Фильтруем исходящие транзакции с комиссиями (value < 1 доллар)
    fees = df_sol[(df_sol["Flow"] == "out") & (df_sol["Value"] <= fee_threshold)]
    total_fees = fees["Value"].sum()

    # Группируем комиссии по дням
    daily_fees = fees.groupby("Date")["Value"].sum().fillna(0)

    # ✅ Чистый PnL без учета комиссий
    daily_pnl_no_fees = daily_pnl + daily_fees

    # Объединяем все показатели в один DataFrame для удобного отображения
    daily_report = pd.DataFrame({
        "PnL": daily_pnl.map(lambda x: f"{x:.6f} $"),
        "PnL без комиссий": daily_pnl_no_fees.map(lambda x: f"{x:.6f} $"),
        "Сумма комиссий": daily_fees.map(lambda x: f"-{abs(x):.6f} $"),
    }).fillna("0.000000 $")

    # ✅ Чистый PnL без учета комиссий
    daily_pnl_no_fees = daily_pnl + daily_fees  # Добавляем комиссии обратно, чтобы получить PnL без учета fee


    # 📊 Выводим результаты
    result_text = (
        f"📊 *Анализ транзакций по Solana-кошельку:*\n"
        f"💰 *Общий доход:* {total_in:.6f} $\n"
        f"💸 *Общий расход:* {total_out:.6f} $\n"
        f"📉 *Чистый PnL:* {total_pnl:.6f} $\n\n"
        f"📅 *PnL по дням:*\n{daily_report}\n\n"
        f"✅ *Самый прибыльный день:* {best_day} (+{best_pnl:.6f} $)\n"
        f"❌ *Самый убыточный день:* {worst_day} ({worst_pnl:.6f} $)\n\n"
        f"🏦 *Сумма комиссий:* {total_fees:.6f} $"
    )
    print(f"Результат сформирован")
    return result_text

