import requests

def fetch_yahoo_data(ticker):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range=2y&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        res = requests.get(url, headers=headers).json()
        closes = res['chart']['result'][0]['indicators']['quote'][0]['close']
        return [c for c in closes if c is not None]
    except Exception as e:
        print(f"Fehler bei {ticker}: {e}")
        return []

def calculate_sma(data, n):
    if len(data) < n: return 0
    return sum(data[-n:]) / n

def spy_tips_cool():
    # NEU: Nur noch SPY und TIPS, kein Gold mehr
    spy_data = fetch_yahoo_data("^SP500TR")
    tips_data = fetch_yahoo_data("TIP")
    # gold_data = fetch_yahoo_data("GC=F")  # ENTFERNT

    if not spy_data or not tips_data:  # Kein Gold mehr benötigt
        return None, None, None, 0, 0

    spy_close  = spy_data[-1]
    tips_close = tips_data[-1]
    # gold_close = gold_data[-1]  # ENTFERNT

    # NEU: SMA160/160 statt 150/200
    spy_sma  = calculate_sma(spy_data, 160)
    tips_sma = calculate_sma(tips_data, 160)
    # gold_sma = calculate_sma(gold_data, 175)  # ENTFERNT

    spy_ok  = spy_close > spy_sma
    tips_ok = tips_close > tips_sma
    # gold_ok = gold_close > gold_sma  # ENTFERNT

    # NEU: Nur noch binäres Signal (Buy/Cash), kein Gold mehr
    if spy_ok and tips_ok:
        current_signal = "Buy"
    else:
        current_signal = "Cash"

    spy_diff  = ((spy_close  - spy_sma)  / spy_sma)  * 100
    tips_diff = ((tips_close - tips_sma) / tips_sma) * 100
    # gold_diff = ((gold_close - gold_sma) / gold_sma) * 100  # ENTFERNT

    # NEU: Nur 5 Return-Werte statt 7 (kein Gold mehr)
    return current_signal, spy_ok, tips_ok, spy_diff, tips_diff
