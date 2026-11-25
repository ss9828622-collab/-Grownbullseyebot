#!/usr/bin/env python3
"""GrownBullsEye Telegram engine: fast market news, event alerts, morning calendar, 2 polls/day.

Run `python bot.py` every ~10 minutes (GitHub Actions does this). Each run decides by itself
what is due, using state.json so nothing is posted twice.

Env vars:
  TELEGRAM_BOT_TOKEN   bot token from @BotFather (bot must be admin of the channel)
  TELEGRAM_CHAT_ID     channel, e.g. @grownbullseye
  ANTHROPIC_API_KEY    Claude API key
  DRY_RUN=1            print posts instead of sending (no Telegram needed)
Only the Python standard library is used.
"""
import datetime as dt
import email.utils
import hashlib
import html
import json
import os
import random
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import config
import promos
import prompts

IST = dt.timezone(dt.timedelta(hours=5, minutes=30))
STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")
DRY_RUN = os.environ.get("DRY_RUN") == "1"
UA = "Mozilla/5.0 (compatible; MarketNewsBot/1.0)"


def log(*a):
    print(dt.datetime.now(IST).strftime("%H:%M:%S"), *a, flush=True)


# ---------------------------------------------------------------- state
def load_state():
    try:
        with open(STATE_FILE) as f:
            s = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        s = {}
    for k, v in {"seen": {}, "recent_posts": [], "recent_quiz": [], "recent_polls": [],
                 "done": {}, "alerted": [], "daily_count": {}}.items():
        s.setdefault(k, v)
    return s


def save_state(s):
    cutoff = time.time() - 3 * 86400
    s["seen"] = {k: t for k, t in s["seen"].items() if t > cutoff}
    s["recent_posts"] = s["recent_posts"][-40:]
    s["recent_quiz"] = s["recent_quiz"][-60:]
    s["recent_polls"] = s["recent_polls"][-60:]
    s["alerted"] = s["alerted"][-200:]
    today = dt.datetime.now(IST).date()
    keep = {(today - dt.timedelta(days=i)).isoformat() for i in range(3)}
    s["done"] = {k: v for k, v in s["done"].items() if k[:10] in keep}
    s["daily_count"] = {k: v for k, v in s["daily_count"].items() if k in keep}
    with open(STATE_FILE, "w") as f:
        json.dump(s, f, indent=1, ensure_ascii=False)


# ---------------------------------------------------------------- http
def http(url, data=None, headers=None, timeout=25):
    h = {"User-Agent": UA}
    h.update(headers or {})
    req = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def claude(prompt, max_tokens=1500):
    """Ask the AI writer. Uses free Google Gemini if GEMINI_API_KEY is set, else Claude."""
    if os.environ.get("GEMINI_API_KEY"):
        body = json.dumps({
            "system_instruction": {"parts": [{"text": prompts.BRAND}]},
            "contents": [{"role": "user", "parts": [{"text": prompt}]}],
            "generationConfig": {"maxOutputTokens": 4096, "temperature": 0.7,
                                 "responseMimeType": "application/json"},
        }).encode()
        raw, last_err = None, None
        for attempt in range(2):            # free tier is sometimes busy: retry + fall back to other models
            for model in config.GEMINI_MODELS:
                try:
                    raw = http(f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                               body, {"x-goog-api-key": os.environ["GEMINI_API_KEY"],
                                      "content-type": "application/json"}, timeout=60)
                    break
                except Exception as e:
                    last_err = e
                    log(f"gemini {model} failed: {e}")
            if raw:
                break
            time.sleep(10)
        if not raw:
            raise RuntimeError(f"all Gemini models failed: {last_err}")
        parts = json.loads(raw)["candidates"][0]["content"]["parts"]
        text = "".join(p.get("text", "") for p in parts if not p.get("thought"))
        m = re.search(r"(\[.*\]|\{.*\})", text, re.S)
        return json.loads(m.group(1)) if m else None
    body = json.dumps({
        "model": config.MODEL,
        "max_tokens": max_tokens,
        "system": prompts.BRAND,
        "messages": [{"role": "user", "content": prompt}],
    }).encode()
    raw = http("https://api.anthropic.com/v1/messages", body, {
        "x-api-key": os.environ["ANTHROPIC_API_KEY"],
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }, timeout=90)
    text = "".join(b.get("text", "") for b in json.loads(raw)["content"])
    m = re.search(r"(\[.*\]|\{.*\})", text, re.S)
    return json.loads(m.group(1)) if m else None


def tg(method, **params):
    if DRY_RUN:
        log(f"[DRY RUN] {method}:\n" + json.dumps(params, indent=1, ensure_ascii=False))
        return {"ok": True}
    token = os.environ["TELEGRAM_BOT_TOKEN"]
    params["chat_id"] = os.environ["TELEGRAM_CHAT_ID"]
    data = json.dumps(params).encode()
    raw = http(f"https://api.telegram.org/bot{token}/{method}", data,
               {"content-type": "application/json"})
    res = json.loads(raw)
    if not res.get("ok"):
        raise RuntimeError(f"Telegram error: {res}")
    return res


def send_text(text):
    return tg("sendMessage", text=text, parse_mode="HTML", disable_web_page_preview=True)


# ---------------------------------------------------------------- news
def strip_tags(s):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s or ""))).strip()


def parse_time(s):
    if not s:
        return None
    try:
        return email.utils.parsedate_to_datetime(s).astimezone(dt.timezone.utc)
    except (TypeError, ValueError):
        pass
    try:
        return dt.datetime.fromisoformat(s.replace("Z", "+00:00")).astimezone(dt.timezone.utc)
    except ValueError:
        return None


def fetch_feed(name, url):
    root = ET.fromstring(http(url))
    out = []
    atom = "{http://www.w3.org/2005/Atom}"
    for it in root.iter("item"):
        out.append((it.findtext("title"), it.findtext("link"),
                    it.findtext("pubDate") or it.findtext("{http://purl.org/dc/elements/1.1/}date"),
                    it.findtext("description")))
    for it in root.iter(atom + "entry"):
        link = it.find(atom + "link")
        out.append((it.findtext(atom + "title"), link.get("href") if link is not None else "",
                    it.findtext(atom + "updated") or it.findtext(atom + "published"),
                    it.findtext(atom + "summary")))
    items = []
    for title, link, pub, desc in out:
        title = strip_tags(title)
        if not title:
            continue
        items.append({"source": name, "title": title, "link": (link or "").strip(),
                      "time": parse_time(pub), "summary": strip_tags(desc)[:300]})
    return items


def norm_key(title):
    t = re.sub(r" - [^-]+$", "", title.lower())          # drop " - Reuters" suffix (Google News)
    return hashlib.md5(re.sub(r"[^a-z0-9]", "", t)[:80].encode()).hexdigest()


def run_news(state, now):
    if config.QUIET_HOURS[0] <= now.hour or now.hour < config.QUIET_HOURS[1]:
        log("quiet hours, skip news")
        return
    day = now.date().isoformat()
    if state["daily_count"].get(day, 0) >= config.MAX_NEWS_POSTS_PER_DAY:
        log("daily news cap reached")
        return
    fresh_cut = dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=config.NEWS_MAX_AGE_MIN)
    cands = []
    for name, url in config.FEEDS.items():
        try:
            items = fetch_feed(name, url)
        except Exception as e:  # one bad feed must not stop the bot
            log(f"feed failed: {name}: {e}")
            continue
        for it in items:
            k = norm_key(it["title"])
            if k in state["seen"]:
                continue
            state["seen"][k] = time.time()
            if it["time"] and it["time"] < fresh_cut:
                continue
            text = (it["title"] + " " + it["summary"]).lower()
            if any(w in text for w in config.KEYWORDS):
                cands.append(it)
    log(f"{len(cands)} fresh relevant headlines")
    if not cands:
        return
    cands = cands[:25]
    lines = "\n".join(
        f"{i} | {c['source']} | {c['time'].strftime('%H:%M') if c['time'] else '?'} | {c['title']} | {c['summary'][:200]}"
        for i, c in enumerate(cands))
    left = config.MAX_NEWS_POSTS_PER_DAY - state["daily_count"].get(day, 0)
    picks = claude(prompts.PICK_NEWS.format(
        max_posts=min(config.MAX_NEWS_POSTS_PER_RUN, left),
        recent="\n".join(state["recent_posts"][-15:]) or "(none)",
        items=lines)) or []
    for p in picks[:config.MAX_NEWS_POSTS_PER_RUN]:
        try:
            src = cands[int(p["id"])]
        except (KeyError, ValueError, IndexError, TypeError):
            continue
        e = html.escape
        src_name = re.sub(r"^Google News: .*", "News", src["source"])
        source = f'<a href="{e(src["link"])}">{e(src_name)}</a>' if src["link"] else e(src_name)
        text = (f"⚡ <b>{e(p['headline'])}</b>\n\n{e(p['body'])}\n\n"
                f"🎯 <b>Trader note:</b> {e(p['trader_note'])}\n\n"
                f"<i>Source: {source}</i>  #{e(p.get('tag', 'MACRO'))} {config.HASHTAG}")
        send_text(text)
        state["recent_posts"].append(p["headline"])
        state["daily_count"][day] = state["daily_count"].get(day, 0) + 1
        log("posted news:", p["headline"])


# ---------------------------------------------------------------- calendar
def load_calendar():
    events = json.loads(http(config.CALENDAR_URL))
    out = []
    for ev in events:
        if ev.get("impact") != "High" or ev.get("country") not in config.CALENDAR_CURRENCIES:
            continue
        try:
            t = dt.datetime.fromisoformat(ev["date"]).astimezone(IST)
        except (KeyError, ValueError):
            continue
        out.append({**ev, "ist": t})
    return out


def run_calendar(state, now):
    try:
        cal = load_calendar()
    except Exception as e:
        log(f"calendar failed: {e}")
        return []
    today = [ev for ev in cal if ev["ist"].date() == now.date()]

    key = now.date().isoformat() + ":brief"
    if now.strftime("%H:%M") >= config.MORNING_BRIEF_AT and key not in state["done"] and now.hour < 12:
        rows = "\n".join(f"{ev['ist'].strftime('%H:%M')} | {ev['country']} | {ev['title']} | "
                         f"{ev.get('forecast') or '-'} | {ev.get('previous') or '-'}"
                         for ev in sorted(today, key=lambda x: x["ist"])) or "(no high-impact events)"
        b = claude(prompts.MORNING_BRIEF.format(date=now.strftime("%A, %d %b %Y"), events=rows))
        if b:
            e = html.escape
            text = (f"🗓 <b>{e(b['title'])}</b>  ({now.strftime('%d %b')})\n\n"
                    + "\n".join(f"• {e(l)}" for l in b["lines"])
                    + f"\n\n💡 {e(b['tip'])}\n\n{config.HASHTAG}")
            send_text(text)
            state["done"][key] = True
            log("posted morning brief")

    for ev in today:
        mins = (ev["ist"] - now).total_seconds() / 60
        ek = f"{ev['ist'].isoformat()}|{ev['title']}"
        if 0 < mins <= config.EVENT_ALERT_MIN_BEFORE and ek not in state["alerted"]:
            e = html.escape
            text = (f"⏰ <b>{int(mins)} min mein: {e(ev['country'])} {e(ev['title'])}</b>\n\n"
                    f"Forecast: {e(ev.get('forecast') or '-')}  |  Previous: {e(ev.get('previous') or '-')}\n"
                    f"Release ke around spreads aur volatility badh sakte hain. Size chhota rakho, "
                    f"pehli candle ke peeche mat bhaago, volume confirm hone do.\n\n{config.HASHTAG}")
            send_text(text)
            state["alerted"].append(ek)
            log("posted alert:", ev["title"])
    return today


# ---------------------------------------------------------------- polls
def run_polls(state, now, today_events):
    hhmm = now.strftime("%H:%M")
    for i, slot in enumerate(config.POLL_SLOTS):
        key = f"{now.date().isoformat()}:poll{i}"
        # due once the slot time passes, but give up after 3 hours (e.g. if the runner was down)
        slot_t = dt.datetime.combine(now.date(), dt.time.fromisoformat(slot), IST)
        if key in state["done"] or not (slot_t <= now < slot_t + dt.timedelta(hours=3)):
            continue
        if i == 0:
            topic = random.choice(prompts.QUIZ_TOPICS)
            q = claude(prompts.QUIZ_POLL.format(topic=topic,
                       recent="\n".join(state["recent_quiz"][-30:]) or "(none)"))
            if not q:
                continue
            tg("sendPoll", question=q["question"][:300], options=[o[:100] for o in q["options"]][:10],
               type="quiz", correct_option_id=int(q["correct"]),
               explanation=q["explanation"][:200], is_anonymous=True)
            state["recent_quiz"].append(q["question"])
        else:
            ctx = "\n".join(state["recent_posts"][-8:]) + "\n" + "\n".join(
                f"{ev['ist'].strftime('%H:%M')} IST {ev['country']} {ev['title']}" for ev in today_events)
            q = claude(prompts.MARKET_POLL.format(context=ctx.strip() or "(quiet day)",
                       recent="\n".join(state["recent_polls"][-30:]) or "(none)"))
            if not q:
                continue
            tg("sendPoll", question=q["question"][:300], options=[o[:100] for o in q["options"]][:10],
               is_anonymous=True)
            if q.get("followup"):
                send_text(f"💡 {html.escape(q['followup'])}\n\n{config.HASHTAG}")
            state["recent_polls"].append(q["question"])
        state["done"][key] = True
        log(f"posted poll {i}")


# ---------------------------------------------------------------- promos
def run_promos(state, now):
    if not promos.ENABLED:
        return
    for i, (slot, days, versions) in enumerate(promos.SCHEDULE):
        key = f"{now.date().isoformat()}:promo{i}"
        slot_t = dt.datetime.combine(now.date(), dt.time.fromisoformat(slot), IST)
        if now.weekday() not in days or key in state["done"] or not (slot_t <= now < slot_t + dt.timedelta(hours=1)):
            continue
        n = state.setdefault("promo_rot", {}).get(str(i), 0)
        send_text(promos.TEXTS[versions[n % len(versions)]])
        state["promo_rot"][str(i)] = n + 1
        state["done"][key] = True
        log(f"posted promo {i}")


# ---------------------------------------------------------------- main
def main():
    state = load_state()
    now = dt.datetime.now(IST)
    if len(sys.argv) > 1:   # manual test: python bot.py news|calendar|quiz|poll
        cmd = sys.argv[1]
        if cmd == "news":
            run_news(state, now)
        elif cmd == "calendar":
            state["done"].pop(now.date().isoformat() + ":brief", None)
            run_calendar(state, now.replace(hour=9, minute=0))
        elif cmd.startswith("promo"):   # promo, promo-full, promo-value, promo-short
            send_text(promos.TEXTS[cmd.split("-", 1)[1] if "-" in cmd else "full"])
        elif cmd in ("quiz", "poll"):
            i = 0 if cmd == "quiz" else 1
            state["done"].pop(f"{now.date().isoformat()}:poll{i}", None)
            slot = dt.time.fromisoformat(config.POLL_SLOTS[i])
            run_polls(state, dt.datetime.combine(now.date(), slot, IST), [])
        save_state(state)
        return
    steps = [("calendar", lambda: run_calendar(state, now))]
    today_events = []
    for name, fn in steps:
        try:
            today_events = fn() or []
        except Exception as e:
            log(f"{name} failed: {e}")
    for name, fn in [("polls", lambda: run_polls(state, now, today_events)),
                     ("promos", lambda: run_promos(state, now)),
                     ("news", lambda: run_news(state, now))]:
        try:
            fn()
        except Exception as e:
            log(f"{name} failed: {e}")
    save_state(state)


if __name__ == "__main__":
    main()
