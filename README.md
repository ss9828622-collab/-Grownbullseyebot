# GrownBullsEye Telegram Market Bot

Runs by itself every 10 minutes. No copy-paste, no manual posting.

## What it posts

| When (IST) | Post | Value to members |
|---|---|---|
| As news breaks, 07:00 to 23:00 | ⚡ News post: headline, what happened (Hinglish), 🎯 Trader note | What the news means for Gold/forex and what to watch. Claude skips noise, predictions and repeats. Max 2 per run, 14 per day. |
| 08:30 | 🗓 Aaj ka Market Calendar | Today's high-impact events (USD, INR, EUR, GBP, JPY, CNY) in IST with why each matters, plus one risk tip. |
| 30 min before each high-impact event | ⏰ Event alert | Forecast vs previous and how to handle the volatility. |
| 11:00 | Quiz poll (1 correct answer + explanation) | Teaches a concept: Volume Profile, Order Flow, VWAP, risk, psychology, Gold drivers. Never repeats. |
| 19:30 | Market poll + 💡 tip | Asks how members are preparing for today's market (not "will gold go up"). |

Brand rules are built into every prompt (see `prompts.py`): no profit/accuracy claims, no direction stated as fact,
no buy/sell calls, only facts from the source.

## One-time setup (about 10 minutes)

1. **Telegram bot**: in Telegram open @BotFather, send `/newbot`, copy the token. Add the bot to your channel
   as an **admin** with "Post Messages" permission.
2. **Free AI key**: go to aistudio.google.com, sign in with Google, click "Get API key" → "Create API key".
   No card needed. (Optional: an Anthropic key instead uses Claude, which is paid.)
3. **GitHub repo**: put these files in a **public** repo (Claude can do this for you). Public repos get unlimited
   free GitHub Actions minutes; a private repo would run out of free minutes at a 10-minute schedule.
   Your keys stay hidden either way: GitHub secrets are encrypted and never shown in the code or logs.
4. In the repo go to **Settings → Secrets and variables → Actions → New repository secret** and add:
   - `TELEGRAM_BOT_TOKEN` = the BotFather token
   - `TELEGRAM_CHAT_ID` = your channel username, e.g. `@grownbullseye`
   - `GEMINI_API_KEY` = the free Google AI key
5. Go to the **Actions** tab, open "Telegram market bot", click **Run workflow**, type `quiz` and run it.
   A quiz should appear in your channel within a minute. After that it runs on its own.

## Changing things

Everything is in `config.py`: news sources, keywords, quiet hours, poll times, daily limits.
Manual test runs from the Actions tab: `news`, `calendar`, `quiz`, `poll`.
To pause the bot: Actions tab → "Telegram market bot" → ⋯ → Disable workflow.

## Cost

Everything is free: GitHub Actions (public repo), Google Gemini free tier (the bot makes well under
its daily limit), Telegram Bot API, and the news/calendar feeds.

## Who controls the channel

You stay the only human admin. The bot is a program, not a person, and Telegram needs it listed as an
admin only so it can post. When adding it, turn on **only** "Post Messages" and turn off every other
right (add admins, delete, ban, edit info). Only you have the bot token and the GitHub account, so only
you can change or stop it.
