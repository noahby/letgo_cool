# STRATEGY PARAMETERS

# ********************************** SPY TIPS COOL STRATEGY **********************************
SPY_SMA = 150
TIPS_SMA = 200
GOLD_SMA = 200

COOLDOWN_DAYS = 15

# number of attempts to download data
TRY_COUNT = 3
DAILY_NOTIFICATION = True

# main subjects
MAIN_SIGNAL_CHANGE_LONG = f"GO LONG NOW (cooldown activated for {0} days)"
MAIN_SIGNAL_CHANGE_SHORT = f"GO IN CASH NOW (cooldown activated for {0} days)"
MAIN_SIGNAL_CHANGE_GOLD = f"GO IN GOLD NOW (cooldown activated for {0} days)"
COOLDOWN_WARNINGS = [1]
COOLDOWN_WARNINGS_TEXT = ["Cooldown warning: Last day of cooldown"]

# sub subjects
INDICATOR_CHANGE_TITLE = "Some Indicators changed"
assert len(COOLDOWN_WARNINGS) == len(COOLDOWN_WARNINGS_TEXT), "COOLDOWN_WARNINGS and COOLDOWN_WARNINGS_TEXT must have the same length"

# ********************************** END SPY TIPS COOL STRATEGY **********************************

# DO NOT CHANGE THESE
BUY = "BUY"
SELL = "SELL"
GOLD = "GOLD"
HISTORY_FILENAME = "history"
