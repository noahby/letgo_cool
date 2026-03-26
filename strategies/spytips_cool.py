import os
import pandas as pd
import yahooquery as yq
from .constants import *
import numpy as np
import time

def spy_tips_cool():
    # Attempt to download data from Yahoo Finance, retry up to TRY_COUNT times
    for i in range(TRY_COUNT):
        try:
            spy = yq.Ticker('^SP500TR').history(period="max", adj_ohlc=True, adj_timezone=False)
            tips = yq.Ticker('TIP').history(period="max", adj_ohlc=True, adj_timezone=False)
            gold = yq.Ticker('GC=F').history(period="max", adj_ohlc=True, adj_timezone=False)
        except Exception as e:
            print(f"({i+1}/{TRY_COUNT}) Failed to download data from Yahoo Finance: {e}")
            time.sleep(2)
            continue
        # Check if any data is empty
        if spy.empty or tips.empty or gold.empty:
            print(f"({i+1}/{TRY_COUNT}) Failed to download data from Yahoo Finance. Please check your internet connection or the ticker symbols.")
            time.sleep(2)
        else:
            break
    else:
        return "Error", "Failed to download data from Yahoo Finance after multiple attempts.", "Please try again later manually"

    # Drop the last row if its close value is NaN (incomplete trading day)
    def drop_last_if_nan(df, col='close'):
        if df is None or df.empty:
            return df
        try:
            if pd.isna(df[col].iloc[-1]):
                return df.iloc[:-1]
        except Exception:
            return df
        return df

    spy = drop_last_if_nan(spy)
    tips = drop_last_if_nan(tips)
    gold = drop_last_if_nan(gold)

    # Extract date index from MultiIndex and set as DataFrame index
    date_level_str_spy = pd.Index([str(x) for x in spy.index.get_level_values("date")])
    date_level_str_tips = pd.Index([str(x) for x in tips.index.get_level_values("date")])
    date_level_str_gold = pd.Index([str(x) for x in gold.index.get_level_values("date")])

    # Detect rows that contain time info (intraday timestamps)
    colon_mask_spy = date_level_str_spy.str.contains(":")
    colon_mask_tips = date_level_str_tips.str.contains(":")
    colon_mask_gold = date_level_str_gold.str.contains(":")

    # Strip time info, keep only the date part
    spy.index = pd.to_datetime(date_level_str_spy.where(~colon_mask_spy, date_level_str_spy.str.split(" ").str[0]))
    tips.index = pd.to_datetime(date_level_str_tips.where(~colon_mask_tips, date_level_str_tips.str.split(" ").str[0]))
    gold.index = pd.to_datetime(date_level_str_gold.where(~colon_mask_gold, date_level_str_gold.str.split(" ").str[0]))

    # Extract close prices
    spy_close = spy['close']
    tips_close = tips['close']
    gold_close = gold['close']

    # Calculate rolling SMAs
    spy_sma_rolling = spy_close.rolling(window=SPY_SMA).mean()
    tips_sma_rolling = tips_close.rolling(window=TIPS_SMA).mean()
    gold_sma_rolling = gold_close.rolling(window=GOLD_SMA).mean()

    # Calculate relative difference between close and SMA
    spy_diff = (spy_close - spy_sma_rolling) / spy_sma_rolling
    tips_diff = (tips_close - tips_sma_rolling) / tips_sma_rolling
    gold_diff = (gold_close - gold_sma_rolling) / gold_sma_rolling

    # Determine the market state for a given index position:
    # BUY (SPY) if both SPY and TIPS are above SMA,
    # GOLD if only gold is above SMA,
    # SELL (cash) otherwise
    def get_state(idx):
        if spy_diff.iloc[idx] > 0 and tips_diff.iloc[idx] > 0:
            return BUY
        elif gold_diff.iloc[idx] > 0:
            return GOLD
        else:
            return SELL

    fileName = HISTORY_FILENAME + "_" + str(SPY_SMA) + "_" + str(TIPS_SMA) + "_" + str(COOLDOWN_DAYS) + ".txt"
    last_entry = None

    if not os.path.exists(fileName):
        # Find the most recent continuous sequence of at least COOLDOWN_DAYS days with the same state
        consecutive_days = 1
        for i in range(2, min(len(spy_diff), len(tips_diff), len(gold_diff))):
            if get_state(-i) == get_state(-i + 1):
                consecutive_days += 1
            else:
                consecutive_days = 1
            if consecutive_days >= COOLDOWN_DAYS:
                break
        else:
            print("Could not find a continuous sequence of cooldown days.")
            return "Error", "Could not find a continuous sequence of cooldown days.", "This happens if the data is not sufficient or the cooldown days are too high."

        # Write history file from the found start index up to today
        f = open(fileName, 'w')
        indicator = None
        cooldown = 0
        for j in range(i, 0, -1):
            if np.isnan(spy_diff.iloc[-j]) or np.isnan(tips_diff.iloc[-j]) or np.isnan(gold_diff.iloc[-j]):
                return "Error", None, "SMA calculation failed, please try again later. Some indicators are NaN."
            state = get_state(-j)
            if cooldown == 0:
                if indicator is not None and state != indicator:
                    cooldown = COOLDOWN_DAYS
                indicator = state
            f.write(f"{spy.index[-j]},{spy_close.iloc[-j]},{tips_close.iloc[-j]},{gold_close.iloc[-j]},"
                    f"{spy_sma_rolling.iloc[-j]},{tips_sma_rolling.iloc[-j]},{gold_sma_rolling.iloc[-j]},"
                    f"{indicator},{cooldown}\n")
            if cooldown > 0:
                cooldown -= 1
        f.close()
    else:
        # Read existing history file and get last recorded entry
        f = open(fileName, 'r')
        file_c = f.readlines()
        f.close()
        last_entry = file_c[-1].split(",")

        # If already up to date, nothing to do
        if last_entry[0] == str(spy.index[-1]):
            print("Already checked today")
            return None, None, None

        # Find the index of the last recorded date in the spy data
        last_date = pd.to_datetime(last_entry[0])
        last_index = spy.index.get_loc(last_date)
        last_rev_index = last_index - len(spy.index)
        cooldown = int(last_entry[8])
        indicator = last_entry[7].strip()

        assert last_rev_index < -1, "Last entry index is not negative, something went wrong with the data."

        # Append new entries since the last recorded date
        for j in range(last_rev_index + 1, 0):
            if np.isnan(spy_diff.iloc[j]) or np.isnan(tips_diff.iloc[j]) or np.isnan(gold_diff.iloc[j]):
                return "Error", None, "SMA calculation failed, please try again later. Some indicators are NaN."
            if cooldown > 0:
                cooldown -= 1
            state = get_state(j)
            if cooldown == 0 and state != indicator:
                cooldown = COOLDOWN_DAYS
                indicator = state
            f = open(fileName, 'a')
            f.write(f"{spy.index[j]},{spy_close.iloc[j]},{tips_close.iloc[j]},{gold_close.iloc[j]},"
                    f"{spy_sma_rolling.iloc[j]},{tips_sma_rolling.iloc[j]},{gold_sma_rolling.iloc[j]},"
                    f"{indicator},{cooldown}\n")
            f.close()

    # Read the latest entry from the history file
    f = open(fileName, 'r')
    file_c = f.readlines()
    f.close()

    # Parse latest entry: date, spy_close, tips_close, gold_close, spy_sma, tips_sma, gold_sma, indicator, cooldown
    new_entry_raw = file_c[-1].split(",")
    new_entry = {
        "date": new_entry_raw[0],
        "spy_close": float(new_entry_raw[1]),
        "tips_close": float(new_entry_raw[2]),
        "gold_close": float(new_entry_raw[3]),
        "spy_sma": float(new_entry_raw[4]),
        "tips_sma": float(new_entry_raw[5]),
        "gold_sma": float(new_entry_raw[6]),
        "indicator": new_entry_raw[7].strip(),
        "cooldown": int(new_entry_raw[8]),
    }

    # Determine current raw signals (before cooldown)
    spy_indicator = TRUE if new_entry["spy_close"] > new_entry["spy_sma"] else FALSE
    tips_indicator = TRUE if new_entry["tips_close"] > new_entry["tips_sma"] else FALSE
    gold_indicator = TRUE if new_entry["gold_close"] > new_entry["gold_sma"] else FALSE
    total_indicator = new_entry["indicator"]

    # Helper dict for human-readable state strings
    state_str = {BUY: "in market (SPY)", GOLD: "in gold", SELL: "in cash"}

    subject = ""
    subject2 = ""
    text = ""

    if last_entry is None:
        # First run: always notify with current state
        if total_indicator == BUY:
            subject = MAIN_SIGNAL_CHANGE_LONG.format(new_entry["cooldown"])
        elif total_indicator == GOLD:
            subject = MAIN_SIGNAL_CHANGE_GOLD.format(new_entry["cooldown"])
        else:
            subject = MAIN_SIGNAL_CHANGE_SHORT.format(new_entry["cooldown"])

        text += f"Currently {state_str.get(total_indicator, total_indicator)} ({new_entry['cooldown']} cooldown days remaining)\n"
        text += f"The SIGNAL is {total_indicator}\n"
        text += f"The SPY signal is {spy_indicator} with a difference of {spy_diff.iloc[-1]:.2%}\n"
        text += f"The TIPS signal is {tips_indicator} with a difference of {tips_diff.iloc[-1]:.2%}\n"
        text += f"The GOLD signal is {gold_indicator} with a difference of {gold_diff.iloc[-1]:.2%}\n"
    else:
        # Parse previous entry for comparison
        last_entry_parsed = {
            "date": last_entry[0],
            "spy_close": float(last_entry[1]),
            "tips_close": float(last_entry[2]),
            "gold_close": float(last_entry[3]),
            "spy_sma": float(last_entry[4]),
            "tips_sma": float(last_entry[5]),
            "gold_sma": float(last_entry[6]),
            "indicator": last_entry[7].strip(),
            "cooldown": int(last_entry[8]),
        }

        last_spy_indicator = TRUE if last_entry_parsed["spy_close"] > last_entry_parsed["spy_sma"] else FALSE
        last_tips_indicator = TRUE if last_entry_parsed["tips_close"] > last_entry_parsed["tips_sma"] else FALSE
        last_gold_indicator = TRUE if last_entry_parsed["gold_close"] > last_entry_parsed["gold_sma"] else FALSE
        last_total_indicator = last_entry_parsed["indicator"]

        # Check if the main indicator (with cooldown) changed
        if total_indicator != last_total_indicator:
            if total_indicator == BUY:
                subject = MAIN_SIGNAL_CHANGE_LONG.format(new_entry["cooldown"])
            elif total_indicator == GOLD:
                subject = MAIN_SIGNAL_CHANGE_GOLD.format(new_entry["cooldown"])
            else:
                subject = MAIN_SIGNAL_CHANGE_SHORT.format(new_entry["cooldown"])
        else:
            # Check cooldown warnings
            for i in COOLDOWN_WARNINGS:
                if new_entry["cooldown"] <= i and last_entry_parsed["cooldown"] > i:
                    subject = COOLDOWN_WARNINGS_TEXT[COOLDOWN_WARNINGS.index(i)]

        # Check if any raw indicator changed (regardless of cooldown)
        if spy_indicator != last_spy_indicator or tips_indicator != last_tips_indicator or gold_indicator != last_gold_indicator:
            subject2 = INDICATOR_CHANGE_TITLE

        # Build status text
        text += f"Currently {state_str.get(total_indicator, total_indicator)} ({new_entry['cooldown']} cooldown days remaining)\n"
        text += f"The SIGNAL {'remains' if total_indicator == last_total_indicator else 'has changed to'} {total_indicator}\n"
        text += f"The SPY signal {'remains' if spy_indicator == last_spy_indicator else 'has changed to'} {spy_indicator}"
        text += f" with a difference of {spy_diff.iloc[-1]:.2%}\n"
        text += f"The TIPS signal {'remains' if tips_indicator == last_tips_indicator else 'has changed to'} {tips_indicator}"
        text += f" with a difference of {tips_diff.iloc[-1]:.2%}\n"
        text += f"The GOLD signal {'remains' if gold_indicator == last_gold_indicator else 'has changed to'} {gold_indicator}"
        text += f" with a difference of {gold_diff.iloc[-1]:.2%}\n"

        if DAILY_NOTIFICATION and subject == "" and subject2 == "":
            subject = "Daily Notification"

    return subject, subject2, text
