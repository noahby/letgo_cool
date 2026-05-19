# 1. Schlusskurse extrahieren
    spy_close = spy_raw['close']
    tips_close = tips_raw['close']
    gold_close = gold_raw['close']

    # 2. MultiIndex bereinigen: Nur das reine Datum behalten
    spy_close.index = pd.to_datetime(spy_close.index.get_level_values('date')).normalize()
    tips_close.index = pd.to_datetime(tips_close.index.get_level_values('date')).normalize()
    gold_close.index = pd.to_datetime(gold_close.index.get_level_values('date')).normalize()

    # 3. Datums-Achsen perfekt synchronisieren (Wie axis=1 in Google Sheets)
    main_df = pd.concat([spy_close, tips_close, gold_close], axis=1)
    main_df.columns = ['spy', 'tips', 'gold']
    
    # 4. Lücken füllen (Forward-Fill für Feiertags-Asynchronitäten)
    main_df = main_df.ffill().dropna()

    # 5. Erst JETZT die SMAs auf den perfekt synchronisierten Daten berechnen!
    main_df['spy_sma'] = main_df['spy'].rolling(window=SPY_SMA).mean()
    main_df['tips_sma'] = main_df['tips'].rolling(window=TIPS_SMA).mean()
    main_df['gold_sma'] = main_df['gold'].rolling(window=GOLD_SMA).mean()

    # Rows ohne vollständige SMAs am Anfang löschen
    main_df = main_df.dropna()

    # Relative Differenzen für die Signale
    spy_diff = (main_df['spy'] - main_df['spy_sma']) / main_df['spy_sma']
    tips_diff = (main_df['tips'] - main_df['tips_sma']) / main_df['tips_sma']
    gold_diff = (main_df['gold'] - main_df['gold_sma']) / main_df['gold_sma']
