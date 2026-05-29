# backfill.py  –  einmal ausführen, danach löschen
import requests
from datetime import date

COOLDOWN_DAYS = 15
HISTORY_FILE = f"history_150_200_175_{COOLDOWN_DAYS}.txt"

def fetch_yahoo_data(ticker, range_="5y"):
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}?range={range_}&interval=1d"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers).json()
    result = res['chart']['result'][0]
    timestamps = result['timestamp']
    closes = result['indicators']['quote'][0]['close']
    dates = [str(date.fromtimestamp(t)) for t in timestamps]
    # None-Werte rausfiltern (beide Listen synchron halten)
    pairs = [(d, c) for d, c in zip(dates, closes) if c is not None]
    return [p[0] for p in pairs], [p[1] for p in pairs]

def calculate_sma(data, n, i):
    """SMA zum Zeitpunkt i (0-basiert)"""
    if i < n - 1:
        return None
    return sum(data[i - n + 1 : i + 1]) / n

# Daten holen
print("Lade Daten...")
spy_dates, spy_closes   = fetch_yahoo_data("^SP500TR")
tips_dates, tips_closes = fetch_yahoo_data("TIP")
gold_dates, gold_closes = fetch_yahoo_data("GC=F")

# Gemeinsame Datumsmenge (alle drei müssen vorhanden sein)
common_dates = sorted(set(spy_dates) & set(tips_dates) & set(gold_dates))
print(f"{len(common_dates)} gemeinsame Handelstage gefunden.")

spy_map  = dict(zip(spy_dates,  spy_closes))
tips_map = dict(zip(tips_dates, tips_closes))
gold_map = dict(zip(gold_dates, gold_closes))

spy_c  = [spy_map[d]  for d in common_dates]
tips_c = [tips_map[d] for d in common_dates]
gold_c = [gold_map[d] for d in common_dates]

# Strategie simulieren
indicator = None
cooldown  = 0
lines     = []

for i, d in enumerate(common_dates):
    spy_sma  = calculate_sma(spy_c,  150, i)
    tips_sma = calculate_sma(tips_c, 200, i)
    gold_sma = calculate_sma(gold_c, 175, i)

    if spy_sma is None or tips_sma is None or gold_sma is None:
        continue  # noch nicht genug Daten für SMA

    spy_ok  = spy_c[i]  > spy_sma
    tips_ok = tips_c[i] > tips_sma
    gold_ok = gold_c[i] > gold_sma

    if spy_ok and tips_ok:
        new_signal = "Buy"
    elif gold_ok:
        new_signal = "Gold"
    else:
        new_signal = "Cash"

    # Cooldown dekrementieren
    if cooldown > 0:
        cooldown -= 1

    # Signalwechsel → Cooldown setzen
    if indicator is not None and new_signal != indicator and cooldown == 0:
        cooldown = COOLDOWN_DAYS

    indicator = new_signal
    lines.append(f"{d},{new_signal},{cooldown}")

# Datei schreiben
with open(HISTORY_FILE, 'w') as f:
    f.write("\n".join(lines) + "\n")

print(f"Fertig! {len(lines)} Einträge in {HISTORY_FILE} geschrieben.")
print(f"Letzter Eintrag: {lines[-1]}")
