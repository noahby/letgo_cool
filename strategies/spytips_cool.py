import requests

def fetch_yahoo_data(ticker):
    # Exakt die gleiche Abfrage wie im Google Apps Script
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=2y&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers).json()
        closes = res['chart']['result'][0]['indicators']['quote'][0]['close']
        # None-Werte entfernen (wie im Sheet)
        return [c for c in closes if c is not None]
    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
        return []

def calculate_sma(data, n):
    if len(data) < n: return 0
    return sum(data[-n:]) / n

def spy_tips_cool():
    # 1. Daten holen
    spy_data = fetch_yahoo_data("^SP500TR")
    tips_data = fetch_yahoo_data("TIP")
    gold_data = fetch_yahoo_data("GC=F")

    if not spy_data or not tips_data or not gold_data:
        return None, None, None, None, 0, 0, 0

    # 2. Kurse für heute (letzter Index)
    spy_close = spy_data[-1]
    tips_close = tips_data[-1]
    gold_close = gold_data[-1]

    # 3. SMAs berechnen (wie im Sheet: Durchschnitt der letzten N Tage)
    spy_sma = calculate_sma(spy_data, 150)
    tips_sma = calculate_sma(tips_data, 200)
    gold_sma = calculate_sma(gold_data, 175)

    # 4. Booleans für den Status
    spy_ok = spy_close > spy_sma
    tips_ok = tips_close > tips_sma
    gold_ok = gold_close > gold_sma

    # 5. Signal-Logik 1:1 wie im Sheet
    if spy_ok and tips_ok:
        current_signal = "Buy"
    elif gold_ok:
        current_signal = "Gold"
    else:
        current_signal = "Cash"

    # 6. Prozentuale Differenzen berechnen
    spy_diff = ((spy_close - spy_sma) / spy_sma) * 100
    tips_diff = ((tips_close - tips_sma) / tips_sma) * 100
    gold_diff = ((gold_close - gold_sma) / gold_sma) * 100

    print(f"DEBUG: TIPS-Kurs {tips_close:.4f} / SMA {tips_sma:.4f}")
    
    return current_signal, spy_ok, tips_ok, gold_ok, spy_diff, tips_diff, gold_diff
