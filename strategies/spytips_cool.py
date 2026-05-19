import pandas as pd
import yfinance as yf
import os

# Konstanten für die Signale
BUY = "Buy"
GOLD = "Gold"
SELL = "Cash"

# Konstanten für die SMAs
SPY_SMA = 150
TIPS_SMA = 200
GOLD_SMA = 175

def spy_tips_cool():
    print("Starte LETSGO Signal-Berechnung (Python-Edition)...")

    # 1. Daten von Yahoo Finance laden (2 Jahre für sichere SMA-Berechnung)
    spy_raw = yf.download("^SP500TR", period="2y", interval="1d")
    tips_raw = yf.download("TIP", period="2y", interval="1d")
    gold_raw = yf.download("GC=F", period="2y", interval="1d")

    if spy_raw.empty or tips_raw.empty or gold_raw.empty:
        print("Fehler: Konnte keine Marktdaten von Yahoo Finance laden.")
        return None

    # 2. Schlusskurse extrahieren (Spaltennamen bei yfinance sind meist klein geschrieben)
    # Falls dein yfinance 'Close' mit großem C liefert, passt Python das automatisch an (.lower())
    spy_raw.columns = [col.lower() for col in spy_raw.columns]
    tips_raw.columns = [col.lower() for col in tips_raw.columns]
    gold_raw.columns = [col.lower() for col in gold_raw.columns]

    spy_close = spy_raw['close']
    tips_close = tips_raw['close']
    gold_close = gold_raw['close']

    # 3. MultiIndex auflösen, falls yfinance die Daten geschachtelt zurückgibt
    if isinstance(spy_close.index, pd.MultiIndex):
        spy_close.index = pd.to_datetime(spy_close.index.get_level_values('date')).normalize()
    else:
        spy_close.index = pd.to_datetime(spy_close.index).normalize()

    if isinstance(tips_close.index, pd.MultiIndex):
        tips_close.index = pd.to_datetime(tips_close.index.get_level_values('date')).normalize()
    else:
        tips_close.index = pd.to_datetime(tips_close.index).normalize()

    if isinstance(gold_close.index, pd.MultiIndex):
        gold_close.index = pd.to_datetime(gold_close.index.get_level_values('date')).normalize()
    else:
        gold_close.index = pd.to_datetime(gold_close.index).normalize()

    # 4. Datums-Achsen perfekt synchronisieren (Exakt wie axis=1 in Google Sheets)
    main_df = pd.concat([spy_close, tips_close, gold_close], axis=1)
    main_df.columns = ['spy', 'tips', 'gold']
    
    # 5. Lücken füllen (Forward-Fill für asynchrone Feiertage zwischen den Börsen)
    main_df = main_df.ffill().dropna()

    # 6. SMAs auf den perfekt synchronisierten Daten berechnen
    main_df['spy_sma'] = main_df['spy'].rolling(window=SPY_SMA).mean()
    main_df['tips_sma'] = main_df['tips'].rolling(window=TIPS_SMA).mean()
    main_df['gold_sma'] = main_df['gold'].rolling(window=GOLD_SMA).mean()

    # Zeilen ohne vollständige historische SMA-Werte abschneiden
    main_df = main_df.dropna()

    if main_df.empty:
        print("Fehler: Nach der SMA-Berechnung sind keine Daten übrig geblieben.")
        return None

    # 7. Signale für die Historie generieren
    signals = []
    for i in range(len(main_df)):
        spy_val = main_df['spy'].iloc[i]
        spy_sma = main_df['spy_sma'].iloc[i]
        tips_val = main_df['tips'].iloc[i]
        tips_sma = main_df['tips_sma'].iloc[i]
        gold_val = main_df['gold'].iloc[i]
        gold_sma = main_df['gold_sma'].iloc[i]

        # Kaskaden-Logik 1:1 wie im Google Sheet
        if spy_val > spy_sma and tips_val > tips_sma:
            state = BUY
        elif gold_val > gold_sma:
            state = GOLD
        else:
            state = SELL
        
        signals.append(state)

    main_df['signal'] = signals

    # 8. Letzten aktuellen Stand für Discord / Output ermitteln
    latest_row = main_df.iloc[-1]
    latest_date = main_df.index[-1].strftime("%Y-%m-%d")
    current_signal = latest_row['signal']

    print(f"Berechnung abgeschlossen für Stichtag: {latest_date}")
    print(f"Aktuelles Signal: {current_signal}")
    print(f"SPY: {latest_row['spy']:.2f} (SMA: {latest_row['spy_sma']:.2f})")
    print(f"TIPS: {latest_row['tips']:.2f} (SMA: {latest_row['tips_sma']:.2f})")
    print(f"GOLD: {latest_row['gold']:.2f} (SMA: {latest_row['gold_sma']:.2f})")

    # 9. Optional: History-Datei schreiben (falls dein main.py das hier erwartet)
    history_filename = "history_150_200_175.txt"
    try:
        with open(history_filename, "w") as f:
            for date, row in main_df.iterrows():
                f.write(f"{date.strftime('%Y-%m-%d')},{row['signal']}\n")
        print(f"Historie erfolgreich in {history_filename} exportiert.")
    except Exception as e:
        print(f"Fehler beim Schreiben der Historie-Datei: {e}")

    return {
        "date": latest_date,
        "signal": current_signal,
        "spy_above": bool(latest_row['spy'] > latest_row['spy_sma']),
        "tips_above": bool(latest_row['tips'] > latest_row['tips_sma']),
        "gold_above": bool(latest_row['gold'] > latest_row['gold_sma'])
    }
