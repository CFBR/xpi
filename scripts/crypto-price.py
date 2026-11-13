# crypto-price.py — Bitcoin, Ethereum and Monero prices.
#
# State:
#   crypto_coins     comma list of ids or BTC/ETH/XMR aliases
#   crypto_currency  usd, eur, gbp, or another CoinGecko currency
#   crypto_refresh   seconds between API reads, minimum 60
#   crypto_seconds   seconds per page, default 3
#   color            Unicorn color name or #RRGGBB
#
# Prices come from the public CoinGecko simple price endpoint. A failed read
# keeps the last good values on screen.

import json
import time
import urllib.parse
import urllib.request

import _display
import _dot
import _xpi_state

DEFAULT_COINS = "bitcoin,ethereum,monero"
DEFAULT_CURRENCY = "usd"
DEFAULT_REFRESH = 120
DEFAULT_COLOR = (0, 255, 0)
ALIASES = {
    "btc": "bitcoin", "bitcoin": "bitcoin",
    "eth": "ethereum", "ethereum": "ethereum",
    "xmr": "monero", "monero": "monero",
}
SYMBOLS = {"bitcoin": "BTC", "ethereum": "ETH", "monero": "XMR"}


def coins():
    raw = str(_xpi_state.value("crypto_coins") or DEFAULT_COINS)
    result = []
    for part in raw.split(","):
        key = part.strip().lower()
        if not key:
            continue
        coin = ALIASES.get(key, key)
        if coin not in result:
            result.append(coin)
    return result or ["bitcoin"]


def currency():
    value = str(_xpi_state.value("crypto_currency") or DEFAULT_CURRENCY)
    return value.strip().lower() or DEFAULT_CURRENCY


def refresh_seconds():
    try:
        return max(60, int(_xpi_state.value("crypto_refresh") or DEFAULT_REFRESH))
    except (TypeError, ValueError):
        return DEFAULT_REFRESH


def page_seconds():
    try:
        return max(1.0, min(30.0, float(_xpi_state.value("crypto_seconds") or 3)))
    except (TypeError, ValueError):
        return 3.0


def symbol(coin):
    return SYMBOLS.get(coin, coin[:3].upper())


def compact_price(value):
    try:
        number = float(value)
    except (TypeError, ValueError):
        return "--"
    if number >= 1000000000:
        text = "%.1fB" % (number / 1000000000.0)
    elif number >= 1000000:
        text = "%.1fM" % (number / 1000000.0)
    elif number >= 1000:
        text = "%.1fK" % (number / 1000.0)
        text = text.replace(".0K", "K")
    elif number >= 100:
        text = str(int(round(number)))
    elif number >= 1:
        text = ("%.1f" % number).rstrip("0").rstrip(".")
    else:
        text = "%.2f" % number
    return text[:6]


def change_text(value):
    if value is None:
        return "--"
    return ("+%.1f%%" % value) if value >= 0 else ("%.1f%%" % value)


def parse(data, ids, currency_code):
    result = []
    for coin in ids:
        row = data.get(coin) or {}
        price = row.get(currency_code)
        if price is None:
            continue
        change = row.get("%s_24h_change" % currency_code)
        result.append({
            "id": coin,
            "symbol": symbol(coin),
            "price": float(price),
            "change": None if change is None else float(change),
        })
    return result


def fetch(previous):
    ids = coins()
    current_currency = currency()
    url = ("https://api.coingecko.com/api/v3/simple/price?ids=%s"
           "&vs_currencies=%s&include_24hr_change=true"
           % (urllib.parse.quote(",".join(ids)),
              urllib.parse.quote(current_currency)))
    request = urllib.request.Request(url, headers={
        "User-Agent": "xpi", "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=15) as response:
            data = json.load(response)
        result = parse(data, ids, current_currency)
        if result:
            print("crypto-price.py: %s %s"
                  % (", ".join(ids), current_currency.upper()))
            return result
    except Exception as exc:
        print("crypto-price.py: fetch failed:", exc)
    return previous


def pages(data):
    if not data:
        return ["--"]
    result = []
    for coin in data:
        result.append(coin["symbol"])
        result.append(compact_price(coin["price"]))
        result.append(change_text(coin["change"]))
    return result


def summary(coin, currency_code):
    if coin is None:
        return "NO DATA"
    if coin["change"] is None:
        change = "NA"
    elif coin["change"] >= 0:
        change = "UP%.1f" % coin["change"]
    else:
        change = "DN%.1f" % abs(coin["change"])
    return "%s %s %s %s" % (
        coin["symbol"], compact_price(coin["price"]),
        currency_code.upper(), change)


def run_microdot():
    import microdotphat

    data = []
    last = 0.0
    print("crypto-price.py: microdot-phat", ",".join(coins()))
    while True:
        if time.time() - last >= refresh_seconds():
            data = fetch(data)
            last = time.time()
        for text in pages(data):
            microdotphat.clear()
            _dot.big_text(text)
            microdotphat.show()
            time.sleep(page_seconds())


def run_unicorn():
    import unicornhat

    shape, unicornhat = _display.setup_unicorn()
    data = []
    last = 0.0
    print("crypto-price.py: unicorn", shape)
    while True:
        if time.time() - last >= refresh_seconds():
            data = fetch(data)
            last = time.time()
        for coin in data or [None]:
            grid = _display.text_bitmap(summary(coin, currency()))
            offset = 0
            end = time.time() + page_seconds()
            while time.time() < end:
                color = _display.parse_color(
                    _xpi_state.value("color"), DEFAULT_COLOR)
                if coin is not None:
                    if coin["change"] is not None and coin["change"] < 0:
                        color = (255, 64, 64)
                    elif coin["change"] is not None:
                        color = (64, 255, 64)
                _display.draw_unicorn(grid, offset, shape, color)
                offset += 1
                time.sleep(0.05)


def main():
    try:
        import microdotphat
        if microdotphat.is_connected():
            return run_microdot()
    except Exception as exc:
        print("crypto-price.py: no microdot-phat:", exc)
    try:
        import unicornhat
    except Exception as exc:
        print("crypto-price.py: no unicorn-hat:", exc)
        raise SystemExit(1)
    return run_unicorn()


if __name__ == "__main__":
    main()
