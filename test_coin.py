"""Проверка Coin Explainer без сети: python test_coin.py

Подменяет запросы к CoinGecko готовыми ответами и проверяет: поиск, выбор из списка, отчёт на всех языках,
лимиты Telegram, HTML, отсутствие вердиктов, защиту от вредного текста в данных, ошибки сети и лимит запросов.
"""
import asyncio
import os
import re
import sys
import tempfile
from types import SimpleNamespace

os.environ["DATA_FILE"] = os.path.join(tempfile.mkdtemp(), "state.json")
os.environ["ADMIN_IDS"] = ""

import devstubs  # noqa: E402

devstubs.install_if_needed()

import bot  # noqa: E402
import coin  # noqa: E402
from locales import LANGS  # noqa: E402
from test_flow import command, press  # noqa: E402

TAGS = re.compile(r"</?(b|i|code)>")
BTC = {"id": "bitcoin", "name": "Bitcoin", "symbol": "btc", "market_cap_rank": 1, "categories": ["Smart Contract Platform", None],
       "description": {"en": "Bitcoin is the first <a href=\"x\">decentralized</a> cryptocurrency. It runs without a central bank. A third sentence."},
       "genesis_date": "2009-01-03", "platforms": {"": ""},
       "market_data": {"current_price": {"usd": 65000.5}, "market_cap": {"usd": 1.3e12}, "total_volume": {"usd": 3e10},
                       "price_change_percentage_24h": 1.2, "ath_change_percentage": {"usd": -10},
                       "circulating_supply": 19.7e6, "total_supply": 21e6, "max_supply": 21e6}}
SHADY = {"id": "shady-coin", "name": "<b>Shady</b> & Co", "symbol": "shd", "market_cap_rank": None, "categories": [],
         "description": {"en": "<script>alert(1)</script> Guaranteed 100x <b>returns</b>!"}, "genesis_date": "2099-01-01",
         "platforms": {"ethereum": "0xabc"},
         "market_data": {"current_price": {"usd": 0.000012}, "market_cap": {"usd": 50000}, "total_volume": {"usd": 5},
                         "price_change_percentage_24h": -45, "ath_change_percentage": {"usd": -99.5},
                         "circulating_supply": 1e6, "total_supply": 1e9, "max_supply": None}}
SEARCH = {"coins": [{"id": "bitcoin", "name": "Bitcoin", "symbol": "BTC", "market_cap_rank": 1},
                    {"id": "bitcoin-cash", "name": "Bitcoin Cash", "symbol": "BCH", "market_cap_rank": 20},
                    {"id": "fake-btc", "name": "Fake BTC", "symbol": "BTC", "market_cap_rank": None},
                    {"id": "x" * 70, "name": "Too long id", "symbol": "LONG", "market_cap_rank": 5}]}
calls = []


def install(mode="ok"):
    async def fake(path, params):
        calls.append(path)
        if mode == "down":
            raise OSError("no network")
        if mode == "busy":
            return 429, None
        if path == "/search":
            q = (params or {}).get("query", "")
            if q == "nothing":
                return 200, {"coins": []}
            if q == "shd":
                return 200, {"coins": [SEARCH["coins"][2] | {"id": "shady-coin", "name": "Shady", "symbol": "SHD"}]}
            return 200, SEARCH
        if path == "/coins/bitcoin":
            return 200, BTC
        if path == "/coins/shady-coin":
            return 200, SHADY
        return 404, None

    coin._fetch = fake
    coin._CACHE.clear()
    coin._LAST.clear()


def check(where, text, rows=None):
    assert 0 < len(text) <= 4096, f"{where}: длина {len(text)}"
    assert text.count("<b>") == text.count("</b>") and text.count("<i>") == text.count("</i>"), f"{where}: теги не парные"
    assert "<" not in TAGS.sub("", text), f"{where}: посторонний тег: {text}"
    for row in rows or []:
        for kind, label, data in row:
            assert label.strip()
            if kind == "cb":
                assert len(data.encode()) <= 64, f"{where}: callback {data} длиннее 64 байт"
            else:
                assert data.startswith("https://"), f"{where}: ссылка не https"


async def main():
    for lang in LANGS:
        install()
        text, rows = await coin.lookup("bitcoin", lang, 1)  # точное совпадение: сразу отчёт
        check(f"{lang}/btc", text, rows)
        assert "Bitcoin (BTC)" in text and "$65,000.50" in text and "#1" in text, f"{lang}: нет основных данных"
        assert "A third sentence" not in text, f"{lang}: описание длиннее двух предложений"
        assert "<a " not in text and "decentralized" in text, f"{lang}: теги в описании"
        for bad in ("buy now", "should buy", "safe to buy", "guaranteed"):
            assert bad not in text.lower(), f"{lang}: вердикт «{bad}»"
        install()
        text, rows = await coin.lookup("shd", lang, 2)
        check(f"{lang}/shady", text, rows)
        assert "&lt;b&gt;Shady&lt;/b&gt;" in text and "<script>" not in text, f"{lang}: данные из сети не экранированы"
        assert text.count("•") >= 5, f"{lang}: мало предупреждений для рискованной монеты"
        install()
        text, rows = await coin.lookup("bit", lang, 3)  # нет точного совпадения: список выбора
        check(f"{lang}/pick", text, rows)
        data = [r[0][2] for r in rows]
        install()
        text, rows = await coin.lookup("btc", lang, 8)  # тикер совпал с топовой монетой: сразу отчёт, клоны без ранга не мешают
        assert "Bitcoin (BTC)" in text, f"{lang}: тикер btc"
        assert data[0] == "cn:bitcoin" and "cn:" + "x" * 70 not in data and len(rows) <= 5, f"{lang}: список {data}"
        for mode, key in (("down", "err"), ("busy", "busy")):
            install(mode)
            text, rows = await coin.lookup("bitcoin", lang, 4)
            assert text == coin.COIN_UI[lang][key], f"{lang}: {mode}"
        install()
        text, _ = await coin.lookup("nothing", lang, 5)
        assert "nothing" in text and text != coin.COIN_UI[lang]["hint"], f"{lang}: не найдено"
        text, _ = await coin.lookup("x" * 41, lang, 6)
        assert text == coin.COIN_UI[lang]["hint"], f"{lang}: длинный запрос"
        text, _ = await coin.lookup("bitcoin", lang, 7)
        text2, _ = await coin.lookup("bitcoin", lang, 7)  # второй сразу: пауза
        assert text2 == coin.COIN_UI[lang]["cooldown"], f"{lang}: нет паузы между запросами"

    # через обработчики бота
    install()
    uid, out = 9100, []
    await bot.on_button(press(uid, "lang:id", out), None)
    out.clear()
    await bot.on_button(press(uid, "coin", out), None)
    assert "Coin Explainer" in out[-1].text and out[-1].markup.inline_keyboard[-1][0].callback_data == "coin"
    out.clear()
    await bot.on_text(SimpleNamespace(callback_query=None, effective_user=SimpleNamespace(id=uid),
                                      effective_message=SimpleNamespace(text="bitcoin", reply_text=command(uid, out).effective_message.reply_text)), None)
    assert "Bitcoin (BTC)" in out[-1].text, "текстовое сообщение не разобрано"
    assert any(b.url and b.url.startswith("https://www.coingecko.com/") for r in out[-1].markup.inline_keyboard for b in r)
    assert any(b.url and "/id/check/" in b.url for r in out[-1].markup.inline_keyboard for b in r), "нет ссылки на проверку токена на языке пользователя"
    out.clear()
    coin._LAST.clear()
    await bot.on_button(press(uid, "cn:bitcoin", out), None)
    assert "Bitcoin (BTC)" in out[-1].text
    out.clear()
    await bot.cmd_coin(command(uid, out), None)
    assert "Coin Explainer" in out[-1].text, "/coin без запроса должен показать подсказку"
    out.clear()
    await bot.on_text(command(77777, out), None) if False else None
    print("OK: Coin Explainer на", len(LANGS), "языках, запросов к сети в тесте:", len(calls))


if __name__ == "__main__":
    asyncio.run(main())
    sys.exit(0)
