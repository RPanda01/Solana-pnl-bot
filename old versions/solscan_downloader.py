import csv
import requests
import os

def get_wallet_transactions(wallet_address, offset=0, limit=50):
    url = f"https://public-api.solscan.io/account/transactions?account={wallet_address}&offset={offset}&limit={limit}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка: {response.status_code}")
        return None

def get_transaction_details(tx_hash):
    url = f"https://public-api.solscan.io/transaction/{tx_hash}"
    headers = {"Accept": "application/json"}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Ошибка получения деталей транзакции {tx_hash}: {response.status_code}")
        return None

def save_transactions_to_csv(wallet_address, save_path):
    transactions = get_wallet_transactions(wallet_address)
    if not transactions:
        print("❌ Не удалось получить данные о транзакциях.")
        return
    
    csv_filename = os.path.join(save_path, f"export_transfer_{wallet_address}.csv")
    
    with open(csv_filename, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Signature", "Time", "Action", "From", "To", "Amount", "Flow", "Value", "Decimals", "TokenAddress"])
        
        for tx in transactions:
            tx_details = get_transaction_details(tx.get("txHash", ""))
            
            if not tx_details:
                continue
            
            # Определяем From, To, Amount и Token
            from_address = tx_details.get("signer", "")
            instructions = tx_details.get("parsedInstruction", [])
            
            to_address = ""
            amount = ""
            token_address = "SOL"
            decimals = 9
            
            for instr in instructions:
                if "destination" in instr:
                    to_address = instr["destination"]
                if "amount" in instr:
                    amount = instr["amount"]
                if "tokenAddress" in instr:
                    token_address = instr["tokenAddress"]
                    decimals = instr.get("decimals", 9)
            
            # Определяем Flow
            flow = "out" if from_address == wallet_address else "in"
            
            # Вычисляем Value (просто переводим Amount в нормальный формат)
            value = float(amount) / (10 ** decimals) if amount else ""
            
            writer.writerow([
                tx.get("txHash", ""),
                tx.get("blockTime", ""),
                "TRANSFER",  # API не дает Action, ставим TRANSFER по умолчанию
                from_address,
                to_address,
                amount,
                flow,
                value,
                decimals,
                token_address
            ])
    
    print(f"✅ CSV-файл сохранен: {csv_filename}")

# 🔹 Пример использования
wallet = "3mQKQtTvzqMSHk9BMewU98G1uNZqywkoCGimt2k7XdVW"  # Укажите свой кошелек
save_path = "./"  # Папка для сохранения
save_transactions_to_csv(wallet, save_path)
