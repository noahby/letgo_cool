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
    # Vorher:
# s, s2, t = spy_tips_cool()

# Neu (vier Variablen empfangen):
signal, spy_ok, tips_ok, gold_ok = spy_tips_cool()
    if s is None and s2 is None and t is None:
        print("Skipped")
    else:
        saveText(s, s2, t)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error = repr(traceback.format_exception(e))
        saveText("Error", error)
