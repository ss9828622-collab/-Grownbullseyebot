"""All the knobs in one place. Edit this file to change sources, timings or limits."""

# ---- News sources (RSS). A broken feed is skipped, it never stops the bot. ----
FEEDS = {
    "FXStreet": "https://www.fxstreet.com/rss/news",
    "investingLive": "https://investinglive.com/feed",
    "Kitco": "https://www.kitco.com/rss/KitcoNews.xml",
    "ET Markets": "https://economictimes.indiatimes.com/markets/commodities/rssfeeds/1808152121.cms",
    "Google News: Gold": "https://news.google.com/rss/search?q=gold+price+OR+bullion+when:2h&hl=en-IN&gl=IN&ceid=IN:en",
    "Google News: Fed/Dollar": "https://news.google.com/rss/search?q=Fed+OR+Powell+OR+%22US+dollar%22+OR+Treasury+yields+when:2h&hl=en-US&gl=US&ceid=US:en",
    "Google News: India macro": "https://news.google.com/rss/search?q=RBI+OR+rupee+OR+%22India+inflation%22+when:2h&hl=en-IN&gl=IN&ceid=IN:en",
}

# Headline must contain at least one of these (lowercase) to be considered.
KEYWORDS = [
    "gold", "xau", "bullion", "silver", "fed", "fomc", "powell", "rate cut", "rate hike",
    "interest rate", "cpi", "inflation", "pce", "nfp", "payroll", "jobs report", "unemployment",
    "gdp", "dollar", "dxy", "treasury", "yield", "ecb", "boj", "rbi", "rupee", "usd/inr",
    "usdinr", "eur/usd", "eurusd", "gbp/usd", "usd/jpy", "crude", "oil", "opec", "tariff",
    "sanction", "war", "ceasefire", "geopolit", "central bank", "recession", "pmi", "ism",
]

# ---- AI writer ----
# Free: set GEMINI_API_KEY (from aistudio.google.com). Optional paid: ANTHROPIC_API_KEY uses Claude.
GEMINI_MODELS = ["gemini-flash-latest", "gemini-flash-lite-latest", "gemini-2.5-flash"]  # tried in order
MODEL = "claude-sonnet-5-5"

# ---- Pacing (IST) ----
NEWS_MAX_AGE_MIN = 90          # ignore stories older than this
MAX_NEWS_POSTS_PER_RUN = 2     # Claude picks at most this many per run
MAX_NEWS_POSTS_PER_DAY = 14
QUIET_HOURS = (23, 7)          # no news posts from 23:00 to 06:59 IST (calendar alerts still go)

MORNING_BRIEF_AT = "08:30"     # daily "Aaj ka market calendar" post
POLL_SLOTS = ["11:00", "19:30"]  # 2 polls/day: first is a learning quiz, second a market poll
EVENT_ALERT_MIN_BEFORE = 30    # heads-up this many minutes before a high-impact event
CALENDAR_CURRENCIES = {"USD", "INR", "CNY", "EUR", "GBP", "JPY"}
CALENDAR_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"

HASHTAG = "#GrownBullsEye"
