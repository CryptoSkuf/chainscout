"""Coin Explainer: простой разбор монеты по бесплатным данным CoinGecko, без языковой модели и без расходов.

Бот спрашивает название или тикер, ищет монету и показывает: что это (описание CoinGecko на английском), основные цифры,
«на что смотреть» (нейтральные предупреждения по правилам) и следующие шаги. Вердиктов «стоит ли покупать» нет.

Модуль не зависит от telegram: возвращает текст (HTML для Telegram) и описание кнопок, а bot.py превращает их в клавиатуру.
Сеть вызывается через _fetch, поэтому в тестах её подменяют.
"""
from __future__ import annotations

import asyncio
import html
import os
import re
import time

import httpx

API = "https://api.coingecko.com/api/v3"
SITE_URL = os.getenv("SITE_URL", "https://chainscout.app").rstrip("/")
COOLDOWN = 3.0  # секунд между запросами одного пользователя
MAX_QUERY = 40

_SEM = asyncio.Semaphore(3)  # не больше трёх одновременных запросов к бесплатному API
_CACHE: dict = {}
_LAST: dict[int, float] = {}


class CoinError(Exception):
    """kind: busy (лимит бесплатного API) или err (прочее)."""

    def __init__(self, kind: str):
        super().__init__(kind)
        self.kind = kind


COIN_UI = {
    "en": {
        "btn": "🔎 Coin explainer",
        "prompt": "🔎 <b>Coin Explainer</b>\n\nSend me a coin name or ticker, for example <code>bitcoin</code> or <code>sol</code>. I will show the basics and what to look at. I do not say if you should buy.",
        "hint": "Send a short coin name or ticker (up to 40 characters).",
        "not_found": "I could not find «{q}» on CoinGecko. Check the spelling or try the ticker.",
        "pick": "Several coins match «{q}». Pick one:",
        "busy": "The free data source is busy. Please try again in a minute.",
        "err": "I could not get the data right now. Please try again later.",
        "cooldown": "One moment please. Wait a few seconds between requests.",
        "what": "What it is", "src": "Project description from CoinGecko, in English", "no_desc": "No description available.",
        "cat": "Category", "nums": "Numbers", "rank": "Rank", "price": "Price", "mcap": "Market cap", "vol": "24h volume",
        "chg": "24h change", "ath": "From all-time high", "circ": "In circulation", "age": "Listed since", "nets": "Networks",
        "flags_title": "Things to look at",
        "nothing": "Nothing unusual in these numbers. This does not mean it is safe.",
        "flags": {
            "small": "Small or unranked coin: the price can move a lot.",
            "lowvol": "Very low trading volume for its size: one trade can move the price.",
            "unlock": "Only {v} of the supply is in circulation. Future unlocks may add supply and push the price down.",
            "nomax": "No maximum supply: new coins can keep being created.",
            "athdrop": "The price is {v} below its all-time high.",
            "young": "Listed only {v} days ago. Young projects are riskier.",
            "swing": "Big move in 24 hours ({v}).",
            "token": "This is a token on another network. Fake copies exist: check the contract with the Token check tool.",
        },
        "next_title": "What to do next",
        "next": ["Open the project's official website and compare it with the links on CoinGecko.", "If it is a token, run its contract through the Token check tool.", "Go through the checklist before you spend anything."],
        "open_cg": "🌐 Open on CoinGecko", "tool": "✅ Token check tool", "guide": "📋 Checklist guide", "another": "🔎 Another coin",
        "note": "Data: CoinGecko. Information only. This is not a recommendation to buy or sell.",
    },
    "fr": {
        "btn": "🔎 Expliquer une crypto",
        "prompt": "🔎 <b>Coin Explainer</b>\n\nEnvoie-moi le nom ou le symbole d'une crypto, par exemple <code>bitcoin</code> ou <code>sol</code>. Je montre l'essentiel et ce qu'il faut regarder. Je ne dis pas s'il faut acheter.",
        "hint": "Envoie un nom court ou un symbole (40 caractères maximum).",
        "not_found": "Je n'ai pas trouvé « {q} » sur CoinGecko. Vérifie l'orthographe ou essaie le symbole.",
        "pick": "Plusieurs cryptos correspondent à « {q} ». Choisis-en une :",
        "busy": "La source de données gratuite est occupée. Réessaie dans une minute.",
        "err": "Je n'ai pas pu obtenir les données maintenant. Réessaie plus tard.",
        "cooldown": "Un instant. Attends quelques secondes entre deux demandes.",
        "what": "Ce que c'est", "src": "Description du projet par CoinGecko, en anglais", "no_desc": "Pas de description disponible.",
        "cat": "Catégorie", "nums": "Chiffres", "rank": "Rang", "price": "Prix", "mcap": "Capitalisation", "vol": "Volume 24 h",
        "chg": "Variation 24 h", "ath": "Depuis le record", "circ": "En circulation", "age": "Listé depuis", "nets": "Réseaux",
        "flags_title": "À surveiller",
        "nothing": "Rien d'inhabituel dans ces chiffres. Cela ne veut pas dire que c'est sûr.",
        "flags": {
            "small": "Petite crypto ou sans classement : le prix peut beaucoup bouger.",
            "lowvol": "Volume d'échange très faible pour sa taille : un seul échange peut faire bouger le prix.",
            "unlock": "Seulement {v} de l'offre est en circulation. De futurs déblocages peuvent ajouter de l'offre et faire baisser le prix.",
            "nomax": "Pas d'offre maximale : de nouvelles pièces peuvent continuer à être créées.",
            "athdrop": "Le prix est {v} sous son record.",
            "young": "Listé il y a seulement {v} jours. Les projets jeunes sont plus risqués.",
            "swing": "Gros mouvement en 24 heures ({v}).",
            "token": "C'est un token sur un autre réseau. Des copies frauduleuses existent : vérifie le contrat avec l'outil de vérification de token.",
        },
        "next_title": "Et ensuite",
        "next": ["Ouvre le site officiel du projet et compare-le avec les liens de CoinGecko.", "Si c'est un token, passe son contrat dans l'outil de vérification de token.", "Suis la checklist avant de dépenser quoi que ce soit."],
        "open_cg": "🌐 Ouvrir sur CoinGecko", "tool": "✅ Vérifier un token", "guide": "📋 Guide checklist", "another": "🔎 Une autre crypto",
        "note": "Données : CoinGecko. Information uniquement. Ce n'est pas une recommandation d'achat ou de vente.",
    },
    "id": {
        "btn": "🔎 Penjelas koin",
        "prompt": "🔎 <b>Coin Explainer</b>\n\nKirim nama atau ticker koin, misalnya <code>bitcoin</code> atau <code>sol</code>. Saya tampilkan dasar-dasarnya dan hal yang perlu dilihat. Saya tidak bilang apakah Anda harus membeli.",
        "hint": "Kirim nama koin atau ticker yang singkat (maksimal 40 karakter).",
        "not_found": "Saya tidak menemukan «{q}» di CoinGecko. Periksa ejaannya atau coba ticker.",
        "pick": "Beberapa koin cocok dengan «{q}». Pilih satu:",
        "busy": "Sumber data gratis sedang sibuk. Coba lagi satu menit lagi.",
        "err": "Saya belum bisa mengambil data sekarang. Coba lagi nanti.",
        "cooldown": "Sebentar ya. Tunggu beberapa detik di antara permintaan.",
        "what": "Apa ini", "src": "Deskripsi proyek dari CoinGecko, dalam bahasa Inggris", "no_desc": "Deskripsi tidak tersedia.",
        "cat": "Kategori", "nums": "Angka", "rank": "Peringkat", "price": "Harga", "mcap": "Kapitalisasi pasar", "vol": "Volume 24 jam",
        "chg": "Perubahan 24 jam", "ath": "Dari rekor tertinggi", "circ": "Beredar", "age": "Terdaftar sejak", "nets": "Jaringan",
        "flags_title": "Hal yang perlu dilihat",
        "nothing": "Tidak ada yang aneh pada angka-angka ini. Itu tidak berarti aman.",
        "flags": {
            "small": "Koin kecil atau tanpa peringkat: harga bisa bergerak jauh.",
            "lowvol": "Volume perdagangan sangat rendah untuk ukurannya: satu transaksi bisa menggerakkan harga.",
            "unlock": "Hanya {v} dari pasokan yang beredar. Pembukaan token di masa depan bisa menambah pasokan dan menekan harga.",
            "nomax": "Tidak ada pasokan maksimum: koin baru bisa terus dibuat.",
            "athdrop": "Harga {v} di bawah rekor tertingginya.",
            "young": "Baru terdaftar {v} hari lalu. Proyek muda lebih berisiko.",
            "swing": "Pergerakan besar dalam 24 jam ({v}).",
            "token": "Ini token di jaringan lain. Salinan palsu ada: periksa kontraknya dengan alat cek token.",
        },
        "next_title": "Langkah berikutnya",
        "next": ["Buka situs resmi proyek dan bandingkan dengan tautan di CoinGecko.", "Jika ini token, periksa kontraknya dengan alat cek token.", "Ikuti checklist sebelum mengeluarkan uang."],
        "open_cg": "🌐 Buka di CoinGecko", "tool": "✅ Alat cek token", "guide": "📋 Panduan checklist", "another": "🔎 Koin lain",
        "note": "Data: CoinGecko. Hanya informasi. Ini bukan rekomendasi untuk membeli atau menjual.",
    },
    "vi": {
        "btn": "🔎 Giải thích đồng coin",
        "prompt": "🔎 <b>Coin Explainer</b>\n\nHãy gửi tên hoặc mã của một đồng coin, ví dụ <code>bitcoin</code> hoặc <code>sol</code>. Mình sẽ cho xem những điều cơ bản và nên chú ý gì. Mình không nói bạn có nên mua hay không.",
        "hint": "Hãy gửi tên coin hoặc mã ngắn gọn (tối đa 40 ký tự).",
        "not_found": "Mình không tìm thấy «{q}» trên CoinGecko. Hãy kiểm tra chính tả hoặc thử mã coin.",
        "pick": "Có nhiều coin khớp với «{q}». Hãy chọn một:",
        "busy": "Nguồn dữ liệu miễn phí đang bận. Hãy thử lại sau một phút.",
        "err": "Hiện mình chưa lấy được dữ liệu. Hãy thử lại sau.",
        "cooldown": "Chờ một chút nhé. Hãy đợi vài giây giữa các yêu cầu.",
        "what": "Đây là gì", "src": "Mô tả dự án từ CoinGecko, bằng tiếng Anh", "no_desc": "Không có mô tả.",
        "cat": "Danh mục", "nums": "Con số", "rank": "Xếp hạng", "price": "Giá", "mcap": "Vốn hóa", "vol": "Khối lượng 24 giờ",
        "chg": "Biến động 24 giờ", "ath": "So với đỉnh lịch sử", "circ": "Đang lưu hành", "age": "Niêm yết từ", "nets": "Mạng",
        "flags_title": "Điều cần chú ý",
        "nothing": "Không có gì bất thường trong các con số này. Điều đó không có nghĩa là an toàn.",
        "flags": {
            "small": "Coin nhỏ hoặc chưa có xếp hạng: giá có thể biến động mạnh.",
            "lowvol": "Khối lượng giao dịch rất thấp so với quy mô: một giao dịch cũng có thể làm giá biến động.",
            "unlock": "Chỉ {v} nguồn cung đang lưu hành. Các đợt mở khóa sau này có thể thêm nguồn cung và kéo giá xuống.",
            "nomax": "Không có nguồn cung tối đa: coin mới có thể tiếp tục được tạo ra.",
            "athdrop": "Giá thấp hơn đỉnh lịch sử {v}.",
            "young": "Mới niêm yết {v} ngày trước. Dự án mới có rủi ro cao hơn.",
            "swing": "Biến động lớn trong 24 giờ ({v}).",
            "token": "Đây là token trên mạng khác. Có bản sao giả: hãy kiểm tra hợp đồng bằng công cụ kiểm tra token.",
        },
        "next_title": "Nên làm gì tiếp",
        "next": ["Mở trang web chính thức của dự án và so với các liên kết trên CoinGecko.", "Nếu là token, hãy kiểm tra hợp đồng bằng công cụ kiểm tra token.", "Đi qua checklist trước khi chi bất cứ khoản nào."],
        "open_cg": "🌐 Mở trên CoinGecko", "tool": "✅ Công cụ kiểm tra token", "guide": "📋 Hướng dẫn checklist", "another": "🔎 Coin khác",
        "note": "Dữ liệu: CoinGecko. Chỉ là thông tin. Đây không phải khuyến nghị mua hay bán.",
    },
    "sw": {
        "btn": "🔎 Eleza sarafu",
        "prompt": "🔎 <b>Coin Explainer</b>\n\nNitumie jina au alama ya sarafu, kwa mfano <code>bitcoin</code> au <code>sol</code>. Nitakuonyesha misingi na cha kuangalia. Sisemi kama unapaswa kununua.",
        "hint": "Tuma jina fupi la sarafu au alama (hadi herufi 40).",
        "not_found": "Sikuipata «{q}» kwenye CoinGecko. Angalia tahajia au jaribu alama.",
        "pick": "Sarafu kadhaa zinalingana na «{q}». Chagua moja:",
        "busy": "Chanzo cha data cha bure kina shughuli nyingi. Jaribu tena baada ya dakika moja.",
        "err": "Siwezi kupata data sasa hivi. Jaribu tena baadaye.",
        "cooldown": "Subiri kidogo. Ngoja sekunde chache kati ya maombi.",
        "what": "Ni nini", "src": "Maelezo ya mradi kutoka CoinGecko, kwa Kiingereza", "no_desc": "Hakuna maelezo.",
        "cat": "Kategoria", "nums": "Namba", "rank": "Nafasi", "price": "Bei", "mcap": "Thamani ya soko", "vol": "Kiasi cha saa 24",
        "chg": "Mabadiliko ya saa 24", "ath": "Kutoka kilele cha wakati wote", "circ": "Inayozunguka", "age": "Imeorodheshwa tangu", "nets": "Mitandao",
        "flags_title": "Mambo ya kuangalia",
        "nothing": "Hakuna jambo lisilo la kawaida kwenye namba hizi. Hiyo haimaanishi ni salama.",
        "flags": {
            "small": "Sarafu ndogo au isiyo na nafasi: bei inaweza kusogea sana.",
            "lowvol": "Kiasi cha biashara ni kidogo sana kwa ukubwa wake: biashara moja inaweza kusogeza bei.",
            "unlock": "{v} tu ya ugavi ndiyo inayozunguka. Kufunguliwa kwa tokeni baadaye kunaweza kuongeza ugavi na kushusha bei.",
            "nomax": "Hakuna ugavi wa juu zaidi: sarafu mpya zinaweza kuendelea kutengenezwa.",
            "athdrop": "Bei iko {v} chini ya kilele chake cha wakati wote.",
            "young": "Imeorodheshwa siku {v} tu zilizopita. Miradi michanga ina hatari kubwa zaidi.",
            "swing": "Mwendo mkubwa ndani ya saa 24 ({v}).",
            "token": "Hii ni tokeni kwenye mtandao mwingine. Nakala bandia zipo: kagua mkataba kwa zana ya kukagua tokeni.",
        },
        "next_title": "Hatua zinazofuata",
        "next": ["Fungua tovuti rasmi ya mradi na ilinganishe na viungo vya CoinGecko.", "Kama ni tokeni, pitisha mkataba wake kwenye zana ya kukagua tokeni.", "Pitia orodha ya kukagua kabla ya kutumia chochote."],
        "open_cg": "🌐 Fungua kwenye CoinGecko", "tool": "✅ Zana ya kukagua tokeni", "guide": "📋 Mwongozo wa orodha", "another": "🔎 Sarafu nyingine",
        "note": "Data: CoinGecko. Taarifa tu. Hii si pendekezo la kununua au kuuza.",
    },
    "simple": {
        "btn": "🔎 Coin explainer",
        "prompt": "🔎 <b>Coin Explainer</b>\n\nSend me the name or ticker of a coin, for example <code>bitcoin</code> or <code>sol</code>. I will show you the basics and what to look at. I do not say if you should buy.",
        "hint": "Send a short coin name or ticker (up to 40 characters).",
        "not_found": "I could not find «{q}» on CoinGecko. Check the spelling or try the ticker.",
        "pick": "More than one coin matches «{q}». Pick one:",
        "busy": "The free data source is busy. Please try again in one minute.",
        "err": "I cannot get the data right now. Please try again later.",
        "cooldown": "One moment please. Wait a few seconds between requests.",
        "what": "What it is", "src": "Project description from CoinGecko, in English", "no_desc": "There is no description.",
        "cat": "Category", "nums": "Numbers", "rank": "Rank", "price": "Price", "mcap": "Market cap", "vol": "24-hour volume",
        "chg": "Change in 24 hours", "ath": "From the all-time high", "circ": "In circulation", "age": "Listed since", "nets": "Networks",
        "flags_title": "Things to look at",
        "nothing": "Nothing strange in these numbers. This does not mean it is safe.",
        "flags": {
            "small": "A small coin, or a coin with no rank. The price can move a lot.",
            "lowvol": "The trading volume is very low for its size. One trade can move the price.",
            "unlock": "Only {v} of the supply is in circulation. Later unlocks can add supply and push the price down.",
            "nomax": "There is no maximum supply. New coins can keep being made.",
            "athdrop": "The price is {v} below its all-time high.",
            "young": "It was listed only {v} days ago. Young projects are riskier.",
            "swing": "A big move in 24 hours ({v}).",
            "token": "This is a token on another network. Fake copies exist. Check the contract with the Token check tool.",
        },
        "next_title": "What to do next",
        "next": ["Open the official website of the project. Compare it with the links on CoinGecko.", "If it is a token, check its contract with the Token check tool.", "Go through the checklist before you spend any money."],
        "open_cg": "🌐 Open on CoinGecko", "tool": "✅ Token check tool", "guide": "📋 Checklist guide", "another": "🔎 Another coin",
        "note": "Data: CoinGecko. Information only. This is not advice to buy or sell.",
    },
}


# ------------------------------------------------------------------ сеть
async def _fetch(path: str, params: dict | None) -> tuple[int, dict | None]:
    async with _SEM:
        async with httpx.AsyncClient(timeout=12, headers={"User-Agent": "ChainScoutBot/1.0 (+https://chainscout.app)"}) as client:
            response = await client.get(API + path, params=params)
    return response.status_code, (response.json() if response.status_code == 200 else None)


async def cg(path: str, params: dict | None = None, ttl: float = 300.0) -> dict | None:
    """Запрос к CoinGecko с кэшем на несколько минут. None: не найдено. CoinError: лимит или сбой."""
    key = (path, tuple(sorted((params or {}).items())))
    hit = _CACHE.get(key)
    if hit and time.monotonic() - hit[0] < ttl:
        return hit[1]
    try:
        status, data = await _fetch(path, params)
    except Exception as exc:  # noqa: BLE001 — любая сетевая ошибка превращается в понятное сообщение
        raise CoinError("err") from exc
    if status == 429:
        raise CoinError("busy")
    if status == 404:
        data = None
    elif status != 200:
        raise CoinError("err")
    if len(_CACHE) > 500:
        _CACHE.clear()
    _CACHE[key] = (time.monotonic(), data)
    return data


def too_soon(uid: int) -> bool:
    now = time.monotonic()
    if now - _LAST.get(uid, -1e9) < COOLDOWN:
        return True
    _LAST[uid] = now
    return False


# ------------------------------------------------------------------ форматирование
def money(n) -> str:
    if not isinstance(n, (int, float)):
        return "-"
    for limit, suffix in ((1e12, "T"), (1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= limit:
            return f"${n / limit:.2f}{suffix}"
    return f"${n:,.2f}"


def price(n) -> str:
    if not isinstance(n, (int, float)):
        return "-"
    return f"${n:,.2f}" if n >= 1 else f"${n:.6g}"


def short_desc(text: str | None, limit: int = 380) -> str:
    text = html.unescape(re.sub(r"<[^>]+>", " ", text or ""))
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        return ""
    out = ""
    for sentence in re.split(r"(?<=[.!?])\s+", text)[:2]:
        if len(out) + len(sentence) + 1 > limit:
            break
        out = f"{out} {sentence}".strip()
    return out or text[:limit].rstrip() + "…"


def pct(x: float) -> str:
    return f"{x:+.1f}%"


def flags_for(data: dict, ui: dict) -> list[str]:
    md = data.get("market_data") or {}
    usd = lambda key: (md.get(key) or {}).get("usd")  # noqa: E731
    flags = []
    rank = data.get("market_cap_rank")
    mcap, vol = usd("market_cap"), usd("total_volume")
    if not rank or rank > 500:
        flags.append(ui["flags"]["small"])
    if isinstance(mcap, (int, float)) and mcap > 0 and isinstance(vol, (int, float)) and vol / mcap < 0.001:
        flags.append(ui["flags"]["lowvol"])
    circ, total, mx = md.get("circulating_supply"), md.get("total_supply"), md.get("max_supply")
    base = mx or total
    if isinstance(circ, (int, float)) and isinstance(base, (int, float)) and base > 0 and circ / base < 0.5:
        flags.append(ui["flags"]["unlock"].format(v=f"{circ / base * 100:.0f}%"))
    if mx is None and isinstance(total, (int, float)) and total > 0:
        flags.append(ui["flags"]["nomax"])
    ath = (md.get("ath_change_percentage") or {}).get("usd")
    if isinstance(ath, (int, float)) and ath <= -90:
        flags.append(ui["flags"]["athdrop"].format(v=f"{abs(ath):.0f}%"))
    genesis = data.get("genesis_date")
    if genesis:
        try:
            days = (time.time() - time.mktime(time.strptime(genesis, "%Y-%m-%d"))) / 86400
            if days < 180:
                flags.append(ui["flags"]["young"].format(v=int(days)))
        except ValueError:
            pass
    change = md.get("price_change_percentage_24h")
    if isinstance(change, (int, float)) and abs(change) >= 20:
        flags.append(ui["flags"]["swing"].format(v=pct(change)))
    if any(addr for addr in (data.get("platforms") or {}).values()):
        flags.append(ui["flags"]["token"])
    return flags


def report_text(data: dict, lang: str) -> str:
    ui = COIN_UI[lang]
    e = html.escape
    md = data.get("market_data") or {}
    usd = lambda key: (md.get(key) or {}).get("usd")  # noqa: E731
    name = e(str(data.get("name") or "?"))
    symbol = e(str(data.get("symbol") or "?").upper())
    lines = [f"<b>{name} ({symbol})</b>"]
    cats = [c for c in (data.get("categories") or []) if c][:3]
    if cats:
        lines.append(f"{ui['cat']}: {e(', '.join(cats))}")
    desc = short_desc((data.get("description") or {}).get("en"))
    lines += ["", f"<b>{ui['what']}</b>", e(desc) if desc else ui["no_desc"]]
    if desc:
        lines.append(f"<i>{ui['src']}</i>")

    nums = [f"{ui['rank']}: #{data['market_cap_rank']}" if data.get("market_cap_rank") else f"{ui['rank']}: -"]
    nums.append(f"{ui['price']}: {price(usd('current_price'))}")
    nums.append(f"{ui['mcap']}: {money(usd('market_cap'))}")
    nums.append(f"{ui['vol']}: {money(usd('total_volume'))}")
    change = md.get("price_change_percentage_24h")
    if isinstance(change, (int, float)):
        nums.append(f"{ui['chg']}: {pct(change)}")
    ath = (md.get("ath_change_percentage") or {}).get("usd")
    if isinstance(ath, (int, float)):
        nums.append(f"{ui['ath']}: {pct(ath)}")
    circ, total, mx = md.get("circulating_supply"), md.get("total_supply"), md.get("max_supply")
    base = mx or total
    if isinstance(circ, (int, float)) and isinstance(base, (int, float)) and base > 0:
        nums.append(f"{ui['circ']}: {circ / base * 100:.0f}%")
    if data.get("genesis_date"):
        nums.append(f"{ui['age']}: {e(str(data['genesis_date']))}")
    nets = [n for n, a in (data.get("platforms") or {}).items() if n and a][:4]
    if nets:
        nums.append(f"{ui['nets']}: {e(', '.join(nets))}")
    lines += ["", f"<b>{ui['nums']}</b>"] + nums

    flags = flags_for(data, ui)
    lines += ["", f"<b>{ui['flags_title']}</b>"]
    lines += [f"• {e(f)}" for f in flags] if flags else [ui["nothing"]]
    lines += ["", f"<b>{ui['next_title']}</b>"] + [f"{i}. {e(s)}" for i, s in enumerate(ui["next"], 1)]
    lines += ["", f"<i>{ui['note']}</i>"]
    return "\n".join(lines)


# ------------------------------------------------------------------ сценарии для bot.py
# Кнопка: ("cb", текст, callback_data) или ("url", текст, адрес). Ряды: список списков.
def prompt_screen(lang: str) -> tuple[str, list]:
    return COIN_UI[lang]["prompt"], []


def clean_query(q: str) -> str:
    return re.sub(r"\s+", " ", q or "").strip()


async def lookup(q: str, lang: str, uid: int) -> tuple[str, list]:
    ui = COIN_UI[lang]
    q = clean_query(q)
    if not q or len(q) > MAX_QUERY:
        return ui["hint"], []
    if too_soon(uid):
        return ui["cooldown"], []
    try:
        found = await cg("/search", {"query": q}, ttl=600)
    except CoinError as exc:
        return ui[exc.kind], []
    coins = [c for c in ((found or {}).get("coins") or []) if c.get("id") and len(c["id"]) <= 60]
    coins.sort(key=lambda c: (c.get("market_cap_rank") is None, c.get("market_cap_rank") or 0))
    coins = coins[:5]
    if not coins:
        return ui["not_found"].format(q=html.escape(q)), []
    exact = [c for c in coins if str(c.get("symbol", "")).lower() == q.lower() or str(c.get("id", "")).lower() == q.lower()]
    if len(coins) == 1 or (exact and exact[0] is coins[0] and coins[0].get("market_cap_rank")):
        return await report(coins[0]["id"], lang, uid, skip_cooldown=True)
    rows = [[("cb", f"{c.get('name', '?')} ({str(c.get('symbol', '?')).upper()})"
              + (f" #{c['market_cap_rank']}" if c.get("market_cap_rank") else ""), f"cn:{c['id']}")] for c in coins]
    return ui["pick"].format(q=html.escape(q)), rows


async def report(coin_id: str, lang: str, uid: int, skip_cooldown: bool = False) -> tuple[str, list]:
    ui = COIN_UI[lang]
    if not skip_cooldown and too_soon(uid):
        return ui["cooldown"], []
    try:
        data = await cg(f"/coins/{coin_id}", {"localization": "false", "tickers": "false", "community_data": "false",
                                              "developer_data": "false", "sparkline": "false"})
    except CoinError as exc:
        return ui[exc.kind], []
    if not data or not data.get("id"):
        return ui["not_found"].format(q=html.escape(coin_id)), []
    rows = [
        [("url", ui["open_cg"], f"https://www.coingecko.com/en/coins/{data['id']}")],
        [("url", ui["tool"], f"{SITE_URL}/{lang}/check/")],
        [("cb", ui["guide"], "gd:token-check-checklist:0")],
    ]
    return report_text(data, lang), rows
