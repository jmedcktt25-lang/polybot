import json
import os
from datetime import datetime

LOG_FILE = os.path.expanduser("~/polybot/trades.json")

def load_trades():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, "r") as f:
        return json.load(f)

def save_trades(trades):
    with open(LOG_FILE, "w") as f:
        json.dump(trades, f, indent=2)

def already_logged(question):
    trades = load_trades()
    open_trades = [t for t in trades if t["status"] == "open"]
    for t in open_trades:
        if t["question"] == question:
            return True
    return False

def log_recommendation(question, recommendation, yes_price, no_price, volume, end_date, claude_probability):
    if already_logged(question):
        print(f"Skipping duplicate: '{question[:50]}...'")
        return None

    trades = load_trades()
    trade = {
        "id": len(trades) + 1,
        "date_logged": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "recommendation": recommendation,
        "yes_price": yes_price,
        "no_price": no_price,
        "volume": volume,
        "end_date": end_date,
        "claude_probability": claude_probability,
        "stake": 10,
        "status": "open",
        "result": None,
        "pnl": 0
    }
    trades.append(trade)
    save_trades(trades)
    print(f"Logged NEW trade #{trade['id']}: {recommendation} on '{question[:50]}'")
    return trade

def resolve_trade(trade_id, won):
    trades = load_trades()
    for t in trades:
        if t["id"] == trade_id:
            t["status"] = "closed"
            t["result"] = "won" if won else "lost"
            if won:
                if t["recommendation"] == "BET YES":
                    t["pnl"] = round((10 / t["yes_price"]) - 10, 2)
                else:
                    t["pnl"] = round((10 / t["no_price"]) - 10, 2)
            else:
                t["pnl"] = -10
            save_trades(trades)
            print(f"Resolved trade #{trade_id}: {'WON' if won else 'LOST'} — P&L: ${t['pnl']}")
            return t
    print(f"Trade #{trade_id} not found")

def show_summary():
    trades = load_trades()
    if not trades:
        print("No trades logged yet.")
        return

    seen = set()
    unique_trades = []
    for t in trades:
        if t["question"] not in seen or t["status"] == "closed":
            seen.add(t["question"])
            unique_trades.append(t)

    closed = [t for t in unique_trades if t["status"] == "closed"]
    open_trades = [t for t in unique_trades if t["status"] == "open"]
    wins = [t for t in closed if t["result"] == "won"]
    total_pnl = sum(t["pnl"] for t in closed)
    win_rate = round(len(wins) / len(closed) * 100) if closed else 0

    print("\nPAPER TRADING SUMMARY")
    print("="*50)
    print(f"Unique markets tracked: {len(unique_trades)}")
    print(f"Open trades: {len(open_trades)}")
    print(f"Closed trades: {len(closed)}")
    print(f"Win rate: {win_rate}%")
    print(f"Total P&L: ${round(total_pnl, 2)}")
    print("\nOPEN TRADES:")
    for t in open_trades:
        print(f"  #{t['id']} {t['recommendation']} — {t['question'][:50]}...")
        print(f"       Logged: {t['date_logged']} | Resolves: {t['end_date'][:10]}")
    if closed:
        print("\nCLOSED TRADES:")
        for t in closed:
            print(f"  #{t['id']} {t['result'].upper()} ${t['pnl']} — {t['question'][:50]}...")

show_summary()
