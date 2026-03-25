import requests
import json

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

    # Only look at markets between 10% and 90% — sweet spot
    if yes_price < 0.10 or yes_price > 0.90:
        return None

    # Score the edge — closer to 50/50 with high volume = interesting
    edge_score = round(abs(yes_price - 0.5) * 100, 1)

    if yes_price < no_price:
        recommendation = "BET YES"
        bet_price = yes_price
        reason = f"YES at {round(yes_price*100)}% — market may be undervaluing this"
    else:
        recommendation = "BET NO"
        bet_price = no_price
        reason = f"NO at {round(no_price*100)}% — market may be undervaluing this"

    return {
        "question": question,
        "yes_price": yes_price,
        "no_price": no_price,
        "volume": volume,
        "recommendation": recommendation,
        "bet_price": bet_price,
        "reason": reason,
        "end_date": end_date,
        "edge_score": edge_score
    }

def run_bot():
    print("\nPOLYMARKET RECOMMENDATION BOT v2")
    print("="*50)
    print("Fetching live markets...\n")

    markets = get_markets()
    results = []

    for market in markets:
        analysis = analyze_market(market)
        if analysis and analysis["volume"] > 5000:
            results.append(analysis)

    results.sort(key=lambda x: x["volume"], reverse=True)

    if not results:
        print("No markets found in the sweet spot. Try again later.")
        return

    print(f"Found {len(results)} markets worth considering\n")
    print("TOP OPPORTUNITIES:")
    print("="*50)

    for i, r in enumerate(results[:5], 1):
        print(f"\n#{i} {r['question']}")
        print(f"   YES: {round(r['yes_price']*100)}%  |  NO: {round(r['no_price']*100)}%")
        print(f"   Volume: ${round(r['volume']):,}")
        print(f"   Resolves: {r['end_date'][:10] if r['end_date'] else 'Unknown'}")
        print(f"   -> {r['recommendation']} — {r['reason']}")

    print("\n" + "="*50)
    print("Disclaimer: This is for paper trading only.")
    print("Always do your own research.\n")

run_bot()
