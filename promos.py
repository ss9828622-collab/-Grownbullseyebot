"""Scheduled promo posts for OLD MONEY BULLSEYE CLUB. Fixed text (no AI), so links are always exact.

Edit the texts or schedule here. Versions rotate so members don't see the same post every time.
"""

ENABLED = False   # set True to start posting

# (time IST, weekdays: 0=Mon ... 6=Sun, which versions to rotate)
SCHEDULE = [
    ("20:00", [0, 2, 4, 6], ["full", "value"]),   # Mon, Wed, Fri, Sun evening peak
    ("10:30", [1, 5], ["short"]),                  # Tue, Sat morning peak
]

LINKS = """👉 <b>ELEFIN</b>
https://partners.elefin.com/go/BQXB-B6LPZB
Referral Code: <code>BQXB-B6LPZB</code>"""

FOOTER = "<i>Partner link.</i>"

TEXTS = {
    "full": f"""<b>OLD MONEY BULLSEYE CLUB</b> 🐎

✅ Exclusive VIP Community Membership
✅ Weekly market discussions and educational sessions
✅ Access to our trading knowledge and community

<b>HOW TO JOIN?</b>
Simply open an account through our partner ELEFIN and deposit $200 or more.
No additional membership fees. No extra charges.

<b>OPEN YOUR ACCOUNT:</b>

{LINKS}

📩 Questions? DM @SHUBH_Bullseye

{FOOTER}""",

    "value": f"""🐎 <b>Market padhna seekhna hai, sirf signals follow karna nahi?</b>

OLD MONEY BULLSEYE CLUB mein har hafte market discussions aur educational sessions hote hain: Volume Profile, Order Flow, aur Gold/NQ/BTC ke key levels ka logic. Community ke saath seekho, akele nahi.

<b>Join kaise karein:</b> neeche diye ELEFIN link se account kholo aur $200+ deposit karo. Koi alag membership fee nahi.

{LINKS}

📩 DM @SHUBH_Bullseye

{FOOTER}""",

    "short": f"""🐎 <b>OLD MONEY BULLSEYE CLUB</b>: weekly market sessions + VIP community.

Join: partner account kholo + $200 deposit. No membership fee.
ELEFIN: https://partners.elefin.com/go/BQXB-B6LPZB (code <code>BQXB-B6LPZB</code>)

📩 DM @SHUBH_Bullseye

{FOOTER}""",
}
