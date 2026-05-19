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
    # 1. Empfange die 4 Werte von spy_tips_cool
    signal, spy_ok, tips_ok, gold_ok = spy_tips_cool()
    
    # 2. Prüfen, ob Daten kamen (wir prüfen das Signal)
    if signal is None:
        print("Skipped")
    else:
        # 3. Baue die Texte zusammen
        # Wir übergeben jetzt das Signal als Hauptbetreff
        # und die Status-Infos der Indikatoren als subject2/text
        status_text = f"SPY > SMA: {spy_ok}\nTIPS > SMA: {tips_ok}\nGOLD > SMA: {gold_ok}"
        saveText(f"Signal: {signal}", "Status der Indikatoren:", status_text)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error = repr(traceback.format_exception(e))
        saveText("Error", error)
