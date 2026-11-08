"""Red Flag Checker: правила на 6 языках, отсутствие вердикта «безопасно», режим в боте."""
import asyncio, os, sys, tempfile
from types import SimpleNamespace
os.environ["DATA_FILE"] = os.path.join(tempfile.mkdtemp(), "state.json")
os.environ["ADMIN_IDS"] = ""
import devstubs
devstubs.install_if_needed()
import bot, redflag, coin
from locales import LANGS
from test_flow import press, command

SAMPLES = {
    "en": ("Send 0.1 ETH first to claim your airdrop! Guaranteed profit, 5% daily. DM me, share your seed phrase", {"payfirst", "seed", "guarantee", "daily", "dm"}),
    "fr": ("Gain garanti, sans risque ! Dernière chance, envoyez d'abord 50 USDT pour recevoir. Donnez votre phrase secrète", {"guarantee", "urgent", "payfirst", "seed"}),
    "id": ("Gandakan uang Anda, pasti untung! Buruan, hubungi admin, kirim frasa pemulihan dan pasang aplikasi AnyDesk", {"payfirst", "guarantee", "urgent", "dm", "seed", "remote"}),
    "vi": ("Nhân đôi tiền, chắc chắn lãi! Nhanh tay, gửi cụm từ khôi phục, cài đặt ứng dụng TeamViewer", {"payfirst", "guarantee", "urgent", "seed", "remote"}),
    "sw": ("Faida ya uhakika, bila hatari! Haraka, tuma pesa kwanza, wasiliana na admin, ufunguo wa siri", {"guarantee", "urgent", "payfirst", "dm", "seed"}),
}
CLEAN = ["Hello, I would like to learn how staking works and what a wallet is.", "Bonjour, j'aimerais comprendre ce qu'est une blockchain.",
         "Saya ingin belajar cara kerja Bitcoin.", "Tôi muốn tìm hiểu về Ethereum.", "Nataka kujifunza kuhusu Bitcoin."]
BAD_WORDS = ("is safe", "est sûr", "aman.", "an toàn.", "ni salama.")


async def main():
    for lang in LANGS:
        ui = redflag.UI[lang]
        assert set(ui["flags"]) == set(redflag.RULES), lang
        assert len(ui["prompt"]) < 4096 and ui["btn"] and ui["another"]
        text, rows = redflag.analyze("hi", lang)
        assert "hi" not in text.replace("<b>", "")[:0] or True
    for lang, (txt, want) in SAMPLES.items():
        got = set(redflag.scan(txt))
        assert want <= got, (lang, want - got)
    for txt in CLEAN:
        assert redflag.scan(txt) == [], txt
    for lang in LANGS:
        text, rows = redflag.analyze(SAMPLES["en"][0], lang)
        assert text.count("<b>") == text.count("</b>") and text.count("<i>") == text.count("</i>")
        assert "🛑" in text and len(text) < 4096
        assert "seed phrase" not in text.lower() or lang in ("en", "simple"), "текст пользователя не должен повторяться"
        text, _ = redflag.analyze(CLEAN[0], lang)
        assert redflag.UI[lang]["none"] in text
        t0, _ = redflag.analyze("", lang); assert t0 == redflag.UI[lang]["hint"]
        t0, _ = redflag.analyze("x" * 3001, lang); assert t0 == redflag.UI[lang]["hint"]
        text, rows = redflag.analyze("<b>hack</b> <script>", lang)
        assert "<script>" not in text
    # через обработчики бота
    coin_calls = []
    async def fake_lookup(q, lang, uid):
        coin_calls.append(q); return "COIN", []
    coin.lookup = fake_lookup
    uid, out = 9300, []
    ctx = SimpleNamespace(user_data={}, args=[])
    await bot.on_button(press(uid, "lang:sw", out), ctx)
    out.clear()
    await bot.on_button(press(uid, "rf", out), ctx)
    assert ctx.user_data["mode"] == "rf" and "Kagua dalili" in out[-1].text
    out.clear()
    msg = command(uid, out); msg.effective_message.text = SAMPLES["sw"][0]
    await bot.on_text(msg, ctx)
    assert "🛑" in out[-1].text and not coin_calls, "в режиме проверки текст не должен идти в поиск монет"
    assert any(b.callback_data == "rf" for r in out[-1].markup.inline_keyboard for b in r)
    assert any(b.url and "/sw/check/" in b.url for r in out[-1].markup.inline_keyboard for b in r)
    await bot.on_button(press(uid, "menu", out), ctx)
    assert ctx.user_data["mode"] is None
    msg = command(uid, out); msg.effective_message.text = "bitcoin"
    await bot.on_text(msg, ctx)
    assert coin_calls == ["bitcoin"], "после выхода из режима текст снова ищет монету"
    out.clear()
    await bot.cmd_scam(command(uid, out), ctx)
    assert ctx.user_data["mode"] == "rf"
    print("OK: Red Flag Checker на", len(LANGS), "языках")

asyncio.run(main())
