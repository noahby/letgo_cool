import traceback
from strategies.spytips_cool import spy_tips_cool

def saveText(subject, subject2=None, text=None):
    if not subject and not subject2:
        return
    d = open('message.txt', 'w')
    if subject:
        d.write(subject + "\n\n")
    if subject2:
        d.write(subject2 + "\n\n")
    if text:
        d.write(text)
    d.close()

import os

def main():
    # 7 Werte empfangen
    signal, spy_ok, tips_ok, gold_ok, spy_diff, tips_diff, gold_diff = spy_tips_cool()
    
    if signal is None:
        print("Skipped")
        return

    # 1. Prüfe, ob das Signal ein Wechsel ist
    last_signal = "None"
    history_file = "history_150_200_175.txt" # Passe den Namen hier ggf. an!
    
    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            lines = f.readlines()
            if lines:
                last_signal = lines[-1].strip() # Nimmt die letzte Zeile als altes Signal

    # 2. Cooldown-Text nur bei Wechsel setzen
    if signal != last_signal:
        cooldown_text = f"SIGNAL WECHSEL: Neuer Modus -> {signal.upper()}\n\n"
        # Speichere das neue Signal in die Historie
        with open(history_file, 'a') as f:
            f.write(signal + "\n")
    else:
        cooldown_text = f"Marktstatus: {signal.upper()} (kein Wechsel)\n\n"

    # Rest bleibt gleich
    market_status = f"Currently in market ({'SPY' if signal == 'Buy' else signal}) (0 cooldown days remaining)"
    
    # ... (Rest der details und saveText wie gehabt)
    
    # Die Signal-Details
    details = (
    f"The SIGNAL is {signal.upper()}\n"
    f"The SPY signal is {'BUY' if spy_ok else 'SELL'} with a difference of {spy_diff:.2f}%\n"
    f"The TIPS signal is {'BUY' if tips_ok else 'SELL'} with a difference of {tips_diff:.2f}%\n"
    f"The GOLD signal is {'GOLD' if gold_ok else 'SELL'} with a difference of {gold_diff:.2f}%"
    )

    
    full_text = cooldown_text + market_status + "\n" + details
    saveText(full_text)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error = repr(traceback.format_exception(e))
        saveText("Error", error)
