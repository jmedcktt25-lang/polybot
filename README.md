# Polymarket AI Trading Bot

An automated prediction market analysis bot that runs 24/7 and uses Claude AI to identify potentially mispriced odds on Polymarket.

## What it does
- Fetches live markets from Polymarket's API every hour
- Filters for markets with genuine uncertainty (10-90% odds range)
- Sends each market to Claude AI which estimates the true probability
- Flags markets where the odds appear mispriced
- Logs all recommendations with timestamps for paper trading validation

## Tech stack
- Python 3.12
- Polymarket CLOB API
- Anthropic Claude API
- Cron scheduling (runs hourly 24/7)

## How to run
1. Clone the repo
2. Install dependencies: `pip install requests anthropic`
3. Set your API key: `export ANTHROPIC_API_KEY="your_key"`
4. Run: `python3 smartbot.py`

## Project status
Currently in paper trading phase — tracking recommendation accuracy before deploying real capital.

## Author
Jamie Duckett
