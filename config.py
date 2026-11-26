"""All the knobs in one place. Edit this file to change sources, timings or limits."""

# ---- News sources (RSS). A broken feed is skipped, it never stops the bot. ----
FEEDS = {
    # Gold
    "Google News: Gold": "https://news.google.com/rss/search?q=gold+price+OR+bullion+OR+XAUUSD+when:2h&hl=en-US&gl=US&ceid=US:en",
    # NQ / Nasdaq 100
    "Google News: Nasdaq": "https://news.google.com/rss/search?q=Nasdaq+OR+%22Nasdaq+100%22+OR+%22tech+stocks%22+OR+Nvidia+OR+%22Magnificent+Seven%22+when:2h&hl=en-US&gl=US&ceid=US:en",
    "investingLive": "https://investinglive.com/feed",
    # BTC
    "CoinDesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "Cointelegraph": "https://cointelegraph.com/rss",
    "Google News: Bitcoin": "https://news.google.com/rss/search?q=Bitcoin+OR+BTC+OR+%22bitcoin+ETF%22+when:2h&hl=en-US&gl=US&ceid=US:en",
    # Macro that moves all three
    "Google News: Fed/Dollar": "https://news.google.com/rss/search?q=Fed+OR+Powell+OR+%22US+dollar%22+OR+Treasury+yields+OR+CPI+when:2h&hl=en-US&gl=US&ceid=US:en",
}

# Step 1 (free, no AI): a headline must contain at least one of these words (lowercase) to go further.
KEYWORDS = [
    # Gold
    "gold", "xau", "bullion", "precious metal",
    # NQ
    "nasdaq", "nq", "tech stock", "nvidia", "apple", "microsoft", "alphabet", "amazon", "meta ",
    "tesla", "magnificent", "semiconductor", "chip", "earnings", "s&p 500", "wall street", "futures",
    # BTC
    "bitcoin", "btc", "crypto", "etf flow", "spot etf", "stablecoin", "halving", "sec ",
    # Macro drivers of all three
    "fed", "fomc", "powell", "rate cut", "rate hike", "interest rate", "cpi", "inflation", "pce",
    "nfp", "payroll", "jobs report", "unemployment", "gdp", "dollar", "dxy", "treasury", "yield",
    "tariff", "sanction", "war", "ceasefire", "geopolit", "recession", "risk-off", "liquidity",
]

# ---- AI writer ----
# Free: set GEMINI_API_KEY (from aistudio.google.com). Optional paid: ANTHROPIC_API_KEY uses Claude.
GEMINI_MODELS = ["gemini-flash-lite-latest", "gemini-flash-latest", "gemini-2.5-flash"]  # tried in order
MODEL = "claude-sonnet-5-5"

# ---- Pacing (IST) ----
NEWS_MAX_AGE_MIN = 60          # ignore stories older than this (and any story with no timestamp)
MAX_NEWS_POSTS_PER_RUN = 1     # at most 1 story per check
MAX_NEWS_POSTS_PER_DAY = 4     # only the most important news
MIN_GAP_BETWEEN_NEWS_MIN = 120 # at least 2 hours between news posts
MIN_IMPORTANCE = 8             # AI scores 1-10; only 8+ gets posted
# Live prices given to the AI so it can reject stale/contradicting stories (Yahoo Finance, free)
LIVE_SYMBOLS = {"Gold": "GC=F", "NQ (Nasdaq 100 fut)": "NQ=F", "BTC": "BTC-USD"}
QUIET_HOURS = (23, 7)          # no news posts from 23:00 to 06:59 IST (calendar alerts still go)

MORNING_BRIEF_AT = "09:30"     # daily "Aaj ka market calendar" post
POLL_SLOTS = ["11:00", "19:30"]  # 2 polls/day: first is a learning quiz, second a market poll
EVENT_ALERT_MIN_BEFORE = 30    # heads-up this many minutes before a high-impact event
CALENDAR_CURRENCIES = {"USD"}  # US data moves Gold, NQ and BTC most
CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

HASHTAG = "#GrownBullsEye"
