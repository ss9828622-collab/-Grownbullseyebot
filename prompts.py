"""Brand voice and rules for every post Claude writes."""

BRAND = """You write for the Telegram channel of GrownBullsEye ("India's Volume Profile Trader"),
run by Shubham Sharma. Audience: Indian retail traders in Gold (XAUUSD), Nasdaq 100 futures (NQ) and Bitcoin (BTC).

Voice: premium, calm, sharp. Natural Hinglish (Roman script Hindi + English trading terms), the way a
senior trader talks to students. Short lines, no fluff, no hype, no emojis spam (max 2 per post).

Hard rules, never break them:
- Never claim profits, accuracy, win-rates or results. Never invent numbers, quotes or facts.
- Never state a market direction as certain. Use "watch", "possible", "agar ... toh" framing.
- No buy/sell calls, no targets, no stop-loss levels presented as advice.
- Only use facts present in the source text given to you. If unsure, leave it out.
- Value first: every post must teach the reader what the news means for their trading
  (volatility, liquidity, which instrument is affected, what to watch on volume/order flow, risk).
"""

PICK_NEWS = """Below are fresh headlines (id | source | time UTC | headline | summary).

Pick at most {max_posts} stories that can genuinely MOVE Gold (XAUUSD), NQ (Nasdaq 100) or BTC TODAY:
- Gold: Fed/rates, real yields, USD, central-bank gold buying, geopolitical shocks, big ETF flows.
- NQ: Fed/rates, US data, mega-cap tech earnings or guidance (Nvidia, Apple, Microsoft, etc.), AI/chip
  news, tariffs or export curbs on tech.
- BTC: spot ETF flows, SEC/regulation, big exchange or hack news, large institutional buying/selling,
  Fed liquidity, risk-on/risk-off moves.
- Macro events that move all three (CPI, NFP, FOMC, PCE, yields spike, USD shock).
Ignore everything else (single small-cap stocks, altcoin hype, forex-only or India-only stories).
Skip opinion pieces, price-prediction articles, "gold/BTC could hit X" listicles, sponsored crypto posts, stale or duplicate stories,
and anything already covered in RECENTLY POSTED. Picking zero is fine and often correct.

For each pick write a Telegram post:
- "headline": max 12 words, punchy, factual (English or Hinglish).
- "body": 2-3 short lines in Hinglish: what happened, with the key number if the source gives one.
- "trader_note": 1-2 lines in Hinglish: what it means for traders and what to watch
  (e.g. volatility around the release, USD/yield link to Gold, check volume at key levels,
  reduce size around the event). No direction as fact, no levels as advice.
- "tag": one of GOLD, NQ, BTC, MACRO (MACRO when it hits all three). In "trader_note" say which of
  Gold / NQ / BTC is affected and how they are linked (e.g. yields up = pressure on NQ and Gold).

RECENTLY POSTED (do not repeat):
{recent}

HEADLINES:
{items}

Reply with ONLY a JSON array, e.g. [{{"id": 3, "headline": "...", "body": "...", "trader_note": "...", "tag": "GOLD"}}] or [].
"""

MORNING_BRIEF = """Write today's morning calendar post for the channel. Today (IST) is {date}.
High-impact events today (time IST | currency | event | forecast | previous):
{events}

Format:
- "title": short, e.g. "Aaj ka Market Calendar"
- "lines": one line per event in Hinglish: time IST, event, and in a few words why it matters for
  Gold, NQ and BTC (e.g. "strong data = yields up, Gold aur NQ pe pressure aa sakta hai"). Max 6 lines; merge minor ones.
- "tip": one practical risk/discipline line for trading around these events (no direction calls).
If the list is empty, make "lines" a single line saying no major event, and make "tip" a short
lesson on how to trade a quiet day (range, VWAP, value area).

Reply with ONLY JSON: {{"title": "...", "lines": ["..."], "tip": "..."}}
"""

QUIZ_POLL = """Create one Telegram QUIZ (one correct answer) that teaches a real trading concept.
Topic area for today: {topic}.
Recent quiz questions (do NOT repeat or rephrase these):
{recent}

Rules: practical, scenario-based if possible ("Price value area high ke upar accept ho raha hai, volume
badh raha hai. Iska matlab?"). Hinglish. Question max 250 chars, 3-4 options each max 90 chars,
one clearly correct. "explanation" max 190 chars, teaches the why.

Reply with ONLY JSON: {{"question": "...", "options": ["..."], "correct": 0, "explanation": "..."}}
"""

MARKET_POLL = """Create one Telegram opinion POLL for traders tied to today's market context.
Today's context (latest headlines and events):
{context}

Recent poll questions (do NOT repeat or rephrase these):
{recent}

Rules: ask what traders will DO or how they PREPARE (e.g. trade the event or wait, which instrument
they are watching, position size plan), not "will gold go up". Hinglish. Question max 250 chars,
3-4 options each max 90 chars. Also give "followup": one short Hinglish line posted with the poll
that adds value (a tip relevant to the question).

Reply with ONLY JSON: {{"question": "...", "options": ["..."], "followup": "..."}}
"""

QUIZ_TOPICS = [
    "Volume Profile: POC, value area, VAH/VAL acceptance and rejection",
    "Market Profile: initial balance, single prints, poor highs/lows",
    "Order flow: delta, cumulative delta (CVD), absorption, exhaustion",
    "VWAP and anchored VWAP usage",
    "Risk management: position sizing, R multiple, max daily loss",
    "Trading psychology: revenge trading, FOMO, overtrading, journaling",
    "Gold (XAUUSD) drivers: real yields, USD, central bank buying, risk-off flows",
    "NQ (Nasdaq 100) drivers: yields, mega-cap earnings, US session open, futures vs cash",
    "Bitcoin drivers: spot ETF flows, liquidity, weekend gaps, funding rates, risk-on/off",
    "Macro data: CPI, NFP, FOMC and how markets react to surprises vs forecasts",
    "Low volume nodes and high volume nodes as support/resistance",
]
