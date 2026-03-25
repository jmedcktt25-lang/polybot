import requests
import json
import anthropic
import os
from datetime import datetime

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

def get_markets():
    url = "https://gamma-api.polymarket.com/markets?limit=50&active=true&closed=false"
    response = requests.get(url)
    return response.json()

def analyze_market(market):
    question = market.get("question", "")
    outcomes = market.get("outcomes", "[]")
    prices = market.get("outcomePrices", "[]")
    volume = float(market.get("volume", 0))
    end_date = market.get("endDate", "")
    closed = market.get("closed", True)
    active = market.get("active", False)

    if closed or not active:
        return None

    try:
        outcomes = json.loads(outcomes)
        prices = json.loads(prices)
    except:
        return None

    if len(prices) < 2:
        return None

    try:
        yes_price = float(prices[0])
        no_price = float(prices[1])
    except:
        return None

    if yes_price == 0 or no_price == 0:
        return None

    if yes_price < 0.10 or yes_price > 0.90:
        return None

    return {
        "question": question,
        "yes_price": yes_price,
        "no_price": no_price,
        "volume": volume,
        "end_date": end_date
    }

def ask_claude(market):
    prompt = f"""You are a prediction market analyst. Analyze this Polymarket market and give a recommendation.

Market: {market['question']}
Current YES price: {round(market['yes_price']*100)}%
Current NO price: {round(market['no_price']*100)}%
Volume: ${round(market['volume']):,}
Resolves: {market['end_date'][:10] if market['end_date'] else 'Unknown'}

Based on your knowledge, is the market price fair, too high, or too low for YES?
Give me:
1. Your estimated true probability (just a number like 35%)
2. Recommendation: BET YES, BET NO, or SKIP
3. One sentence reason why

Keep your answer short and direct."""

    message = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

def run_bot():
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    output = []
    output.append(f"\nPOLYMARKET SMART BOT (powered by Claude)")
    output.append(f"Run time: {timestamp}")
    output.append("="*50)
    output.append("Fetching live markets...\n")

    markets = get_markets()
    results = []

    for market in markets:
        analysis = analyze_market(market)
        if analysis and analysis["volume"] > 5000:
            results.append(analysis)

    results.sort(key=lambda x: x["volume"], reverse=True)
    top = results[:3]

    if not top:
        output.append("No markets found. Try again later.")
    else:
        output.append(f"Analyzing top {len(top)} markets with Claude...\n")
        output.append("="*50)

        for i, r in enumerate(top, 1):
            output.append(f"\n#{i} {r['question']}")
            output.append(f"   YES: {round(r['yes_price']*100)}%  |  NO: {round(r['no_price']*100)}%")
            output.append(f"   Volume: ${round(r['volume']):,}")
            output.append(f"   Resolves: {r['end_date'][:10] if r['end_date'] else 'Unknown'}")
            output.append(f"\n   Claude says:")
            try:
                response = ask_claude(r)
                for line in response.strip().split('\n'):
                    output.append(f"   {line}")
            except Exception as e:
                output.append(f"   Error: {e}")
            output.append("")

    output.append("="*50)
    output.append("Disclaimer: This is for paper trading only.\n")

    full_output = "\n".join(output)

    print(full_output)

    log_path = os.path.expanduser("~/polybot/log.txt")
    with open(log_path, "a") as f:
        f.write(full_output)
        f.write("\n\n")

    print(f"Results saved to ~/polybot/log.txt")

run_bot()
