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

def main():
    # 7 Werte empfangen
    signal, spy_ok, tips_ok, gold_ok, spy_diff, tips_diff, gold_diff = spy_tips_cool()
    
    if signal is None:
        print("Skipped")
        return

    # Text-Layout im alten Stil zusammenbauen
    # Wir nehmen an, dass Cooldown 0 ist, wie in deinem Wunsch-Text
    cooldown_text = "GO LONG NOW (cooldown activated for 0 days)\n\n"
    
    # Status-Zeile
    market_status = f"Currently in market ({'SPY' if signal == 'Buy' else signal}) (0 cooldown days remaining)"
    
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
