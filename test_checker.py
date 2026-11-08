"""Проверка страницы Token check в браузере: EVM, Solana и TRON на моделях ответов GoPlus/CoinGecko (без сети)."""
import json, subprocess, sys, time, socket
from playwright.sync_api import sync_playwright

def free_port():
    s = socket.socket(); s.bind(("", 0)); p = s.getsockname()[1]; s.close(); return p

SOL = "So11111111111111111111111111111111111111112"
TRON = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
EVM = "0xdac17f958d2ee523a2206206994597c13d831ec7"
EVIL = '<img src=x onerror="window.__xss=1">'

GP = {
    "evm": {EVM: {"is_honeypot": "1", "sell_tax": "0.6", "buy_tax": "0", "is_mintable": "0", "holder_count": "50"}},
    "tron": {TRON: {"is_honeypot": "0", "is_mintable": "1", "is_open_source": "1", "holder_count": "5000", "sell_tax": "0", "buy_tax": "0"}},
    "sol": {SOL: {"mintable": {"status": "1", "authority": []}, "freezable": {"status": "0"}, "balance_mutable_authority": {"status": "0"},
                   "none_transferable": "0", "holders": [{"account": "a", "percent": "0.2"}, {"account": "b", "percent": "0.1"}]}},
}
CG = {"id": "tether", "name": EVIL, "symbol": "usdt", "market_data": {"market_cap": {"usd": 1e9}, "total_volume": {"usd": 1e8}},
      "tickers": [1, 2, 3], "links": {"homepage": ["https://x.example"]}, "genesis_date": "2014-01-01"}

def main():
    port = free_port()
    srv = subprocess.Popen([sys.executable, "-m", "http.server", str(port), "-d", "site/dist"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    time.sleep(1)
    urls = []
    try:
        with sync_playwright() as p:
            b = p.chromium.launch()
            for lang in ("en", "fr", "id", "vi", "sw", "simple"):
                for net, addr, kind in (("1", EVM, "evm"), ("tron", TRON, "tron"), ("solana", SOL, "sol")):
                    pg = b.new_page()
                    errs = []
                    pg.on("pageerror", lambda e: errs.append(str(e)))
                    def gp(route):
                        urls.append(route.request.url)
                        body = {"code": 1, "result": GP[kind]}
                        route.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin": "*"}, body=json.dumps(body))
                    def cg(route):
                        urls.append(route.request.url)
                        route.fulfill(status=200, content_type="application/json", headers={"access-control-allow-origin": "*"}, body=json.dumps(CG))
                    pg.route("https://api.gopluslabs.io/**", gp)
                    pg.route("https://api.coingecko.com/**", cg)
                    pg.goto(f"http://localhost:{port}/{lang}/check/")
                    pg.select_option("#ck-net", net)
                    pg.fill("#ck-addr", addr)
                    pg.click("#ck-btn")
                    pg.wait_for_selector("#ck-out:not([hidden])", timeout=8000)
                    rows = pg.eval_on_selector_all("#ck-out .ck-row", "els => els.map(e => e.className)")
                    assert len(rows) >= 14, (lang, net, len(rows))
                    assert pg.evaluate("window.__xss") is None, "XSS"
                    assert not pg.query_selector("#ck-out img"), "теги из чужих данных попали в разметку"
                    txt = pg.inner_text("#ck-out")
                    assert "safe" not in txt.lower() or lang != "en", txt
                    if kind == "evm":
                        assert "ck-row stop" in " ".join(rows), "honeypot/налог 60% должны дать STOP"
                    if kind == "tron":
                        assert any("flag" in r for r in rows), "mintable на TRON должен дать предупреждение"
                    if kind == "sol":
                        assert any("flag" in r for r in rows), "mint authority на Solana должен дать предупреждение"
                        assert sum("unknown" in r for r in rows) >= 4, "для Solana часть пунктов 'нет данных'"
                    assert not errs, errs
                    # неверный адрес для сети
                    pg.fill("#ck-addr", EVM if kind != "evm" else SOL)
                    pg.click("#ck-btn")
                    assert pg.is_visible("#ck-err"), "ошибка адреса не показана"
                    pg.close()
            b.close()
    finally:
        srv.terminate()
    assert any("/solana/token_security" in u for u in urls) and any("token_security/tron" in u for u in urls)
    assert any("/coins/solana/contract/" in u for u in urls) and any("/coins/tron/contract/" in u for u in urls)
    assert not any(TRON.lower() in u for u in urls), "адрес TRON нельзя приводить к нижнему регистру"
    print("OK: Token check, EVM + TRON + Solana, 6 языков, запросов в тесте:", len(urls))

main()
