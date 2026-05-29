import traceback
import os
from datetime import date
from strategies.spytips_cool import spy_tips_cool

COOLDOWN_DAYS = 15

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
    signal, spy_ok, tips_ok, gold_ok, spy_diff, tips_diff, gold_diff = spy_tips_cool()

    if signal is None:
        print("Skipped")
        return

    today = str(date.today())
    history_file = f"history_150_200_175_{COOLDOWN_DAYS}.txt"

    last_date = None
    last_signal = None
    last_cooldown = 0

    if os.path.exists(history_file):
        with open(history_file, 'r') as f:
            lines = [l.strip() for l in f.readlines() if l.strip()]
        if lines:
            parts = lines[-1].split(",")
            last_date     = parts[0]
            last_signal   = parts[1]
            last_cooldown = int(parts[2])

    if last_date == today:
        print("Already checked today")
        return

 cooldown = last_cooldown
if cooldown > 0:
    cooldown -= 1

# Signalwechsel → aber nur wenn kein Cooldown aktiv!
if last_signal is not None and signal != last_signal:
    if cooldown == 0:          # ← NUR dann wechseln
        cooldown = COOLDOWN_DAYS
    else:
        signal = last_signal   # ← Cooldown aktiv → Signal einfrieren

with open(history_file, 'a') as f:
    f.write(f"{today},{signal},{cooldown}\n")

    if last_signal is None or signal != last_signal:
        subject = f"SIGNAL WECHSEL: Neuer Modus → {signal.upper()}"
    else:
        subject = "Daily Notification"

    market_map = {"Buy": "SPY", "Gold": "GOLD", "Cash": "Cash"}
    market_status = (
        f"Currently in market ({market_map[signal]}) "
        f"({cooldown} cooldown days remaining)"
    )

    details = (
        f"The SIGNAL is {signal.upper()}\n"
        f"The SPY signal is {'BUY' if spy_ok else 'SELL'} "
        f"with a difference of {spy_diff:.2f}%\n"
        f"The TIPS signal is {'BUY' if tips_ok else 'SELL'} "
        f"with a difference of {tips_diff:.2f}%\n"
        f"The GOLD signal is {'BUY' if gold_ok else 'SELL'} "
        f"with a difference of {gold_diff:.2f}%"
    )

    full_text = market_status + "\n\n" + details
    saveText(subject, text=full_text)
    print(full_text)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error = repr(traceback.format_exception(e))
        saveText("Error", error)
