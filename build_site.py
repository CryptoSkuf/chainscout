#!/usr/bin/env python3
"""Генератор сайта-каталога ChainScout: catalog.json -> статические страницы на 5 языках.

Запуск:
    python3 build_site.py                       # результат в dist/
    python3 build_site.py --out /tmp/preview --bot-username my_bot

Только стандартная библиотека Python 3.9+. Данные берутся из catalog.json
(тот же файл, что использует Telegram-бот), тексты категорий и уровней из locales.py.
"""
from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path[:0] = [str(HERE), str(HERE.parent)]
from guides import GUIDE_UI, GUIDES  # noqa: E402
from locales import LANGS, STRINGS  # noqa: E402

DEFAULT_BASE = "https://example.com"
# Порядок разделов: сначала безопасность, потом всё остальное от простого к сложному.
ORDER = ["safety", "market", "research", "sentiment", "onchain"]
LEVEL_DOTS = {"beginner": 1, "intermediate": 2, "advanced": 3}
OG_LOCALE = {"en": "en_US", "fr": "fr_FR", "id": "id_ID", "vi": "vi_VN", "sw": "sw_KE"}

# --------------------------------------------------------------------------- тексты сайта
SITE = {
    "en": {
        "title": "{name}: AI and data tools for crypto research",
        "description": "A beginner-friendly directory of AI-powered and data tools for researching crypto: scam checks, prices, on-chain data, news sentiment. Information only, no trading signals.",
        "h1": "What do you want to check?",
        "lede": "Pick a question and see the tools that answer it. This site gives information only, never buy or sell signals.",
        "search_label": "Search tools",
        "search_ph": "Search by name or topic",
        "no_results": "No tool matches that search. Try a shorter word.",
        "start_here": "Start here",
        "tools_one": "1 tool",
        "tools_many": "{n} tools",
        "open": "Open {tool}",
        "new_tab": " (opens in a new tab)",
        "partner": "Partner link",
        "checked_on": "Checked {date}",
        "skip": "Skip to content",
        "lang_label": "Language",
        "q": {
            "safety": "Is this token or link safe?",
            "market": "What is it worth right now?",
            "research": "What is this project really about?",
            "sentiment": "What is everyone saying?",
            "onchain": "What are big wallets doing?",
        },
        "safety_title": "Before you use any crypto tool",
        "tips": [
            "Never share your seed phrase or private keys. No real tool, support agent or admin will ask for them.",
            "Nobody can promise a profit. Be careful with anyone who does, even in a friendly chat.",
            "Open tools by typing the address yourself or from this list. Fake sites copy real ones.",
            "Try a free plan first, and check the price on the official site before you pay.",
        ],
        "join_title": "Hear about new tools",
        "join_text": "Short updates when we add or change a tool. Unsubscribe any time.",
        "tg_button": "Open the Telegram bot",
        "email_label": "Email address",
        "email_button": "Subscribe",
        "disclosure_title": "How this site works",
        "disclosure": "This is an independent directory. Some links are partner links, and we may earn a commission if you sign up, at no extra cost to you. Partner and sponsored listings are marked. Prices and free plans change, so check each official site. Nothing here is financial advice, and crypto is high-risk.",
        "not_found": "Page not found",
        "not_found_text": "Choose a language to go back to the directory.",
    },
    "fr": {
        "title": "{name} : outils d'IA et de données pour la recherche crypto",
        "description": "Un annuaire accessible aux débutants d'outils d'IA et de données pour la recherche crypto : anti-arnaque, prix, données on-chain, sentiment. Information uniquement, aucun signal de trading.",
        "h1": "Que voulez-vous vérifier ?",
        "lede": "Choisissez une question et découvrez les outils qui y répondent. Ce site donne uniquement des informations, jamais de signaux d'achat ou de vente.",
        "search_label": "Rechercher un outil",
        "search_ph": "Nom ou sujet",
        "no_results": "Aucun outil ne correspond. Essayez un mot plus court.",
        "start_here": "Commencez ici",
        "tools_one": "1 outil",
        "tools_many": "{n} outils",
        "open": "Ouvrir {tool}",
        "new_tab": " (s'ouvre dans un nouvel onglet)",
        "partner": "Lien partenaire",
        "checked_on": "Vérifié le {date}",
        "skip": "Aller au contenu",
        "lang_label": "Langue",
        "q": {
            "safety": "Ce token ou ce lien est-il sûr ?",
            "market": "Combien ça vaut en ce moment ?",
            "research": "De quoi parle vraiment ce projet ?",
            "sentiment": "Que dit tout le monde ?",
            "onchain": "Que font les gros portefeuilles ?",
        },
        "safety_title": "Avant d'utiliser un outil crypto",
        "tips": [
            "Ne communiquez jamais votre phrase secrète ni vos clés privées. Aucun vrai outil, support ou administrateur ne les demandera.",
            "Personne ne peut promettre un gain. Méfiez-vous de quiconque le fait, même dans une conversation amicale.",
            "Ouvrez les outils en tapant l'adresse vous-même ou depuis cette liste. Les faux sites imitent les vrais.",
            "Essayez d'abord une offre gratuite et vérifiez le prix sur le site officiel avant de payer.",
        ],
        "join_title": "Soyez prévenu des nouveaux outils",
        "join_text": "De courtes nouvelles quand nous ajoutons ou modifions un outil. Désabonnement à tout moment.",
        "tg_button": "Ouvrir le bot Telegram",
        "email_label": "Adresse e-mail",
        "email_button": "S'abonner",
        "disclosure_title": "Comment fonctionne ce site",
        "disclosure": "Ceci est un annuaire indépendant. Certains liens sont des liens partenaires, et nous pouvons recevoir une commission si vous vous inscrivez, sans frais supplémentaires pour vous. Les fiches partenaires et sponsorisées sont signalées. Les tarifs et offres gratuites changent : vérifiez chaque site officiel. Rien ici n'est un conseil financier, et les cryptos sont très risquées.",
        "not_found": "Page introuvable",
        "not_found_text": "Choisissez une langue pour revenir à l'annuaire.",
    },
    "id": {
        "title": "{name}: alat AI dan data untuk riset kripto",
        "description": "Direktori ramah pemula untuk alat AI dan data riset kripto: cek penipuan, harga, data on-chain, sentimen berita. Hanya informasi, tanpa sinyal trading.",
        "h1": "Apa yang ingin Anda periksa?",
        "lede": "Pilih pertanyaan dan lihat alat yang menjawabnya. Situs ini hanya memberi informasi, tidak pernah sinyal beli atau jual.",
        "search_label": "Cari alat",
        "search_ph": "Cari nama atau topik",
        "no_results": "Tidak ada alat yang cocok. Coba kata yang lebih pendek.",
        "start_here": "Mulai dari sini",
        "tools_one": "1 alat",
        "tools_many": "{n} alat",
        "open": "Buka {tool}",
        "new_tab": " (terbuka di tab baru)",
        "partner": "Tautan mitra",
        "checked_on": "Dicek {date}",
        "skip": "Langsung ke konten",
        "lang_label": "Bahasa",
        "q": {
            "safety": "Apakah token atau tautan ini aman?",
            "market": "Berapa harganya sekarang?",
            "research": "Proyek ini sebenarnya tentang apa?",
            "sentiment": "Apa kata orang-orang?",
            "onchain": "Apa yang dilakukan dompet besar?",
        },
        "safety_title": "Sebelum memakai alat kripto apa pun",
        "tips": [
            "Jangan pernah membagikan seed phrase atau private key. Alat, tim dukungan, atau admin yang asli tidak akan memintanya.",
            "Tidak ada yang bisa menjanjikan keuntungan. Waspadai siapa pun yang menjanjikannya, bahkan dalam obrolan yang ramah.",
            "Buka alat dengan mengetik alamatnya sendiri atau dari daftar ini. Situs palsu meniru situs asli.",
            "Coba paket gratis dulu dan cek harga di situs resmi sebelum membayar.",
        ],
        "join_title": "Dapatkan kabar alat baru",
        "join_text": "Kabar singkat saat kami menambah atau mengubah alat. Berhenti kapan saja.",
        "tg_button": "Buka bot Telegram",
        "email_label": "Alamat email",
        "email_button": "Berlangganan",
        "disclosure_title": "Cara kerja situs ini",
        "disclosure": "Ini adalah direktori independen. Sebagian tautan adalah tautan mitra, dan kami bisa mendapat komisi jika Anda mendaftar, tanpa biaya tambahan bagi Anda. Daftar mitra dan sponsor ditandai. Harga dan paket gratis bisa berubah, jadi cek setiap situs resmi. Tidak ada yang di sini merupakan nasihat keuangan, dan kripto berisiko tinggi.",
        "not_found": "Halaman tidak ditemukan",
        "not_found_text": "Pilih bahasa untuk kembali ke direktori.",
    },
    "vi": {
        "title": "{name}: công cụ AI và dữ liệu để nghiên cứu tiền mã hóa",
        "description": "Danh mục thân thiện với người mới về công cụ AI và dữ liệu để nghiên cứu tiền mã hóa: kiểm tra lừa đảo, giá, dữ liệu on-chain, tâm lý tin tức. Chỉ là thông tin, không có tín hiệu giao dịch.",
        "h1": "Bạn muốn kiểm tra điều gì?",
        "lede": "Chọn một câu hỏi và xem các công cụ trả lời nó. Trang này chỉ cung cấp thông tin, không bao giờ đưa tín hiệu mua hoặc bán.",
        "search_label": "Tìm công cụ",
        "search_ph": "Tên hoặc chủ đề",
        "no_results": "Không có công cụ phù hợp. Hãy thử từ ngắn hơn.",
        "start_here": "Bắt đầu từ đây",
        "tools_one": "1 công cụ",
        "tools_many": "{n} công cụ",
        "open": "Mở {tool}",
        "new_tab": " (mở trong tab mới)",
        "partner": "Liên kết đối tác",
        "checked_on": "Đã kiểm tra {date}",
        "skip": "Bỏ qua đến nội dung",
        "lang_label": "Ngôn ngữ",
        "q": {
            "safety": "Token hoặc liên kết này có an toàn không?",
            "market": "Bây giờ nó có giá bao nhiêu?",
            "research": "Dự án này thật sự là gì?",
            "sentiment": "Mọi người đang nói gì?",
            "onchain": "Ví lớn đang làm gì?",
        },
        "safety_title": "Trước khi dùng bất kỳ công cụ crypto nào",
        "tips": [
            "Không bao giờ chia sẻ cụm từ khôi phục (seed phrase) hoặc khóa riêng. Công cụ, bộ phận hỗ trợ hay quản trị viên thật sẽ không hỏi.",
            "Không ai có thể hứa chắc có lợi nhuận. Hãy cẩn thận với người nào hứa vậy, kể cả trong cuộc trò chuyện thân thiện.",
            "Hãy tự gõ địa chỉ hoặc mở từ danh sách này. Trang giả thường sao chép trang thật.",
            "Dùng thử gói miễn phí trước và kiểm tra giá trên trang chính thức trước khi trả tiền.",
        ],
        "join_title": "Nhận tin về công cụ mới",
        "join_text": "Bản tin ngắn khi chúng mình thêm hoặc thay đổi công cụ. Hủy bất cứ lúc nào.",
        "tg_button": "Mở bot Telegram",
        "email_label": "Địa chỉ email",
        "email_button": "Đăng ký",
        "disclosure_title": "Cách trang này hoạt động",
        "disclosure": "Đây là danh mục độc lập. Một số liên kết là liên kết đối tác, và chúng mình có thể nhận hoa hồng nếu bạn đăng ký, bạn không phải trả thêm. Mục đối tác và tài trợ đều được đánh dấu. Giá và gói miễn phí có thể thay đổi, hãy kiểm tra từng trang chính thức. Không nội dung nào ở đây là lời khuyên tài chính, và tiền mã hóa có rủi ro cao.",
        "not_found": "Không tìm thấy trang",
        "not_found_text": "Chọn một ngôn ngữ để quay lại danh mục.",
    },
    "sw": {
        "title": "{name}: zana za AI na data za utafiti wa crypto",
        "description": "Orodha rafiki kwa wanaoanza ya zana za AI na data za kutafiti crypto: ukaguzi wa ulaghai, bei, data za on-chain, hisia za habari. Taarifa tu, hakuna ishara za biashara.",
        "h1": "Unataka kukagua nini?",
        "lede": "Chagua swali uone zana zinazolijibu. Tovuti hii inatoa taarifa tu, haitoi kamwe ishara za kununua au kuuza.",
        "search_label": "Tafuta zana",
        "search_ph": "Jina au mada",
        "no_results": "Hakuna zana inayolingana. Jaribu neno fupi zaidi.",
        "start_here": "Anzia hapa",
        "tools_one": "zana 1",
        "tools_many": "zana {n}",
        "open": "Fungua {tool}",
        "new_tab": " (inafunguka kwenye kichupo kipya)",
        "partner": "Kiungo cha mshirika",
        "checked_on": "Imekaguliwa {date}",
        "skip": "Ruka hadi maudhui",
        "lang_label": "Lugha",
        "q": {
            "safety": "Je, tokeni au kiungo hiki ni salama?",
            "market": "Thamani yake sasa ni kiasi gani?",
            "research": "Mradi huu unahusu nini hasa?",
            "sentiment": "Watu wanasema nini?",
            "onchain": "Pochi kubwa zinafanya nini?",
        },
        "safety_title": "Kabla ya kutumia zana yoyote ya crypto",
        "tips": [
            "Usishiriki kamwe seed phrase au funguo za siri. Zana halisi, msaada au msimamizi hawataziomba.",
            "Hakuna anayeweza kuahidi faida. Kuwa mwangalifu na yeyote anayeahidi, hata kwenye mazungumzo ya kirafiki.",
            "Fungua zana kwa kuandika anwani mwenyewe au kutoka orodha hii. Tovuti bandia hunakili za kweli.",
            "Jaribu mpango wa bure kwanza na angalia bei kwenye tovuti rasmi kabla ya kulipa.",
        ],
        "join_title": "Pata habari za zana mpya",
        "join_text": "Habari fupi tunapoongeza au kubadilisha zana. Jiondoe wakati wowote.",
        "tg_button": "Fungua bot ya Telegram",
        "email_label": "Barua pepe",
        "email_button": "Jiunge",
        "disclosure_title": "Jinsi tovuti hii inavyofanya kazi",
        "disclosure": "Hii ni orodha huru. Baadhi ya viungo ni vya washirika, na tunaweza kupata kamisheni ukijisajili, bila gharama ya ziada kwako. Orodha za washirika na zilizodhaminiwa zimewekwa alama. Bei na mipango ya bure hubadilika, kwa hiyo angalia kila tovuti rasmi. Hakuna kilicho hapa ni ushauri wa kifedha, na crypto ina hatari kubwa.",
        "not_found": "Ukurasa haupatikani",
        "not_found_text": "Chagua lugha ili kurudi kwenye orodha.",
    },
}

# --------------------------------------------------------------------------- оформление
CSS = """
:root{color-scheme:light dark;--paper:#eef1f8;--surface:#fff;--ink:#161c40;--muted:#4b537d;--line:#dde1f0;--hover:#e3e8f6;--btn-bg:#2a3a9e;--btn-fg:#fff;--ring:#2a3a9e;--focus:#2a3a9e;--mark:#f0a500;--mark-bg:#fff2cc;--mark-ink:#5c3f00}
@media (prefers-color-scheme:dark){:root{--paper:#0e1230;--surface:#161b45;--ink:#eceffc;--muted:#aab2dd;--line:#2b3274;--hover:#1d2358;--btn-bg:#a3b0ff;--btn-fg:#0e1230;--ring:#a3b0ff;--focus:#ffc23d;--mark:#ffc23d;--mark-bg:#3a2d08;--mark-ink:#ffd98a}}
*{box-sizing:border-box}
[hidden]{display:none!important}
html{-webkit-text-size-adjust:100%}
@media (prefers-reduced-motion:no-preference){html{scroll-behavior:smooth}}
body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.6 system-ui,-apple-system,"Segoe UI",Roboto,"Noto Sans",sans-serif}
a{color:inherit}
:focus-visible{outline:3px solid var(--focus);outline-offset:3px;border-radius:6px}
.wrap{max-width:50rem;margin:0 auto;padding:0 16px}
.sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
.skip{position:absolute;left:-999px;top:8px;z-index:10;padding:10px 14px;border-radius:8px;background:var(--btn-bg);color:var(--btn-fg)}
.skip:focus{left:16px}
.top{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:10px 20px;padding:18px 0 6px}
.brand{display:inline-flex;align-items:center;gap:10px;font-weight:800;font-size:1.15rem;letter-spacing:-.01em;text-decoration:none}
.logo{flex:none}
.langs{display:flex;flex-wrap:wrap;gap:2px}
.langs a{padding:6px 10px;border-radius:8px;font-size:.95rem;text-decoration:none;color:var(--muted)}
.langs a:hover{background:var(--hover);color:var(--ink)}
.langs a[aria-current]{background:var(--ink);color:var(--paper);font-weight:650}
h1{max-width:16ch;margin:44px 0 18px;font-size:clamp(2.5rem,9.5vw,4.75rem);line-height:1.02;letter-spacing:-.035em;font-weight:800;text-wrap:balance}
.lede{max-width:60ch;margin:0 0 26px;font-size:1.1rem;color:var(--muted)}
input[type=search],input[type=email]{width:100%;min-height:52px;padding:0 16px;border:2px solid var(--line);border-radius:12px;background:var(--surface);color:var(--ink);font:inherit}
input[type=search]:focus-visible,input[type=email]:focus-visible{border-color:var(--focus)}
.asks{display:grid;gap:10px;margin:22px 0 0;padding:0;list-style:none}
.ask{display:flex;align-items:center;justify-content:space-between;gap:14px;padding:16px 18px 16px 22px;border-radius:14px;background:var(--surface);box-shadow:inset 5px 0 0 var(--ring);font-size:1.2rem;font-weight:700;line-height:1.3;text-decoration:none}
.ask.first{box-shadow:inset 5px 0 0 var(--mark)}
.ask:hover{background:var(--hover)}
.ask small{flex:none;font-size:.9rem;font-weight:500;color:var(--muted)}
.start{display:block;width:max-content;margin-top:6px;padding:2px 8px;border-radius:6px;background:var(--mark-bg);color:var(--mark-ink);font-size:.8rem;font-weight:700}
.empty{margin:28px 0 0;color:var(--muted)}
section{margin-top:56px;scroll-margin-top:12px}
h2{max-width:24ch;margin:0 0 16px;font-size:clamp(1.55rem,5vw,2.1rem);line-height:1.15;letter-spacing:-.02em;font-weight:800;text-wrap:balance}
.panel{margin:0;padding:0;list-style:none;overflow:hidden;border-radius:18px;background:var(--surface)}
.tool{display:grid;gap:14px;padding:20px;border-top:1px solid var(--line)}
.tool:first-child{border-top:0}
.tool h3{margin:0;font-size:1.2rem;line-height:1.3;font-weight:750}
.tool p{max-width:60ch;margin:4px 0 0}
.tool .meta{display:flex;flex-wrap:wrap;align-items:center;gap:6px 18px;margin-top:10px;font-size:.9rem;color:var(--muted)}
.lvl{display:inline-flex;align-items:center;gap:8px}
.dots{display:inline-flex;gap:4px}
.dots i{display:block;width:11px;height:11px;border:2px solid var(--ring);border-radius:50%}
.dots i.on{background:var(--ring)}
.tag{display:inline-block;margin-left:8px;padding:1px 8px;border-radius:6px;background:var(--mark-bg);color:var(--mark-ink);font-size:.75rem;font-weight:700;vertical-align:middle}
.btn{display:inline-flex;align-items:center;justify-content:center;min-height:46px;padding:8px 18px;border:0;border-radius:10px;background:var(--btn-bg);color:var(--btn-fg);font:inherit;font-weight:650;line-height:1.25;text-align:center;text-decoration:none;cursor:pointer}
.btn:hover{filter:brightness(1.1)}
@media (min-width:640px){.tool{grid-template-columns:1fr auto;align-items:center;gap:24px}.tool .btn{min-width:13rem}}
.safe{padding-left:20px;border-left:5px solid var(--mark)}
.safe h2{font-size:clamp(1.3rem,4vw,1.6rem)}
.safe ul{max-width:60ch;margin:0;padding-left:1.2em}
.safe li+li{margin-top:10px}
.join{padding:24px 20px;border-radius:18px;background:var(--surface)}
.join h2{margin-bottom:8px}
.join p{max-width:56ch;margin:0 0 18px;color:var(--muted)}
.mail{display:grid;gap:10px;max-width:28rem;margin-top:18px}
.mail label{font-weight:650}
.fine{margin-top:56px;padding:24px 0 40px;border-top:1px solid var(--line);color:var(--muted);font-size:.9rem}
.fine h2{margin:0 0 8px;font-size:1rem;color:var(--ink)}
.fine p{max-width:68ch;margin:0 0 14px}
.tool h3 a{text-decoration-thickness:2px;text-underline-offset:3px}
.safe .more{max-width:60ch;margin:16px 0 0}
.g h1{max-width:22ch;margin:22px 0 18px;font-size:clamp(2rem,7.5vw,3.3rem);line-height:1.08}
.back{display:inline-block;margin-top:14px;padding:6px 0;color:var(--muted)}
.prose{max-width:60ch}
.prose .lead{margin:0 0 8px;font-size:1.15rem;color:var(--muted)}
.prose h2{max-width:none;margin:40px 0 12px;font-size:1.45rem}
.prose p{margin:0 0 16px}
.prose ul,.prose ol{margin:0;padding-left:1.35em}
.prose li+li{margin-top:12px}
.prose li::marker{color:var(--ring);font-weight:700}
.g .tools-box{max-width:none}
"""

SEARCH_JS = """
(function(){
  var q=document.getElementById('q');if(!q)return;
  var rows=[].slice.call(document.querySelectorAll('[data-tool]'));
  var groups=[].slice.call(document.querySelectorAll('[data-group]'));
  var asks=document.getElementById('asks'),empty=document.getElementById('empty'),gd=document.getElementById('guides');
  function norm(s){return s.toLowerCase().replace(/\\u0111/g,'d').normalize('NFD').replace(/[\\u0300-\\u036f]/g,'');}
  q.addEventListener('input',function(){
    var v=norm(q.value.trim()),shown=0;
    rows.forEach(function(r){var m=!v||r.getAttribute('data-search').indexOf(v)>-1;r.hidden=!m;if(m)shown++;});
    groups.forEach(function(g){g.hidden=!g.querySelector('[data-tool]:not([hidden])');});
    if(asks)asks.hidden=!!v;
    if(gd)gd.hidden=!!v;
    empty.hidden=shown>0;
  });
})();
"""

ROOT_JS = """
(function(){
  var map={en:'en',fr:'fr',id:'id','in':'id',vi:'vi',sw:'sw'};
  var l=navigator.languages||[navigator.language||'en'];
  for(var i=0;i<l.length;i++){var c=String(l[i]).slice(0,2).toLowerCase();if(map[c]){location.replace(map[c]+'/');break;}}
})();
"""

LOGO = (
    '<svg class="logo" width="28" height="28" viewBox="0 0 32 32" aria-hidden="true">'
    '<circle cx="16" cy="16" r="12" fill="none" stroke="currentColor" stroke-width="3"/>'
    '<circle cx="16" cy="16" r="4.5" fill="#f0a500"/></svg>'
)
FAVICON = (
    '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32">'
    '<rect width="32" height="32" rx="8" fill="#2a3a9e"/>'
    '<circle cx="16" cy="16" r="9" fill="none" stroke="#fff" stroke-width="3"/>'
    '<circle cx="16" cy="16" r="3.5" fill="#f0a500"/></svg>\n'
)

esc = html.escape


def norm(text: str) -> str:
    """Та же нормализация, что и в SEARCH_JS: без регистра и диакритики (đ -> d)."""
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    return "".join(c for c in text if not unicodedata.combining(c))


def json_ld(data: dict) -> str:
    return json.dumps(data, ensure_ascii=False).replace("</", "<\\/")


# --------------------------------------------------------------------------- страницы
def tool_row(tool: dict, lang: str, S: dict, L: dict) -> str:
    name = tool["name"]
    desc = tool["desc"].get(lang) or tool["desc"]["en"]
    affiliate = bool(tool.get("affiliate_url"))
    sponsor = bool(tool.get("sponsor"))
    href = tool.get("affiliate_url") or tool["url"]
    rel = "sponsored nofollow noopener" if (affiliate or sponsor) else "noopener"
    tags = ""
    if sponsor:
        tags += f'<span class="tag">{esc(L["sponsored_tag"])}</span>'
    if affiliate:
        tags += f'<span class="tag">{esc(S["partner"])}</span>'
    dots = "".join('<i class="on"></i>' if k < LEVEL_DOTS[tool["level"]] else "<i></i>" for k in range(3))
    checked = ""
    if tool.get("checked"):
        checked = f'<span>{esc(S["checked_on"].format(date=tool["checked"]))}</span>'
    search = norm(f"{name} {desc} {S['q'][tool['category']]}")
    return (
        f'<li class="tool" data-tool data-search="{esc(search)}">'
        f'<div><h3>{esc(name)}{tags}</h3><p>{esc(desc)}</p>'
        f'<div class="meta"><span class="lvl"><span class="dots" aria-hidden="true">{dots}</span>'
        f'<span><span class="sr">{esc(L["level"])}: </span>{esc(L["lvl_" + tool["level"]])}</span></span>{checked}</div></div>'
        f'<a class="btn" href="{esc(href)}" target="_blank" rel="{rel}">'
        f'{esc(S["open"].format(tool=name))}<span class="sr">{esc(S["new_tab"])}</span></a></li>'
    )


def render_page(lang: str, tools: list[dict], cfg: dict, year: int) -> str:
    S, L = SITE[lang], STRINGS[lang]
    name, base = cfg["site_name"], cfg["base_url"]
    title = S["title"].format(name=name)
    url = f"{base}/{lang}/"

    groups = [(c, [x for x in tools if x["category"] == c]) for c in ORDER]
    groups = [(c, items) for c, items in groups if items]

    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{base}/{code}/">' for code in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{base}/">'

    ld = json_ld(
        {
            "@context": "https://schema.org",
            "@type": "ItemList",
            "name": title,
            "inLanguage": lang,
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i,
                    "item": {
                        "@type": "SoftwareApplication",
                        "name": t["name"],
                        "description": t["desc"].get(lang) or t["desc"]["en"],
                        "url": t["url"],
                        "applicationCategory": "FinanceApplication",
                    },
                }
                for i, t in enumerate(tools, 1)
            ],
        }
    )

    langs_nav = "".join(
        f'<a href="../{code}/" lang="{code}" hreflang="{code}"'
        + (' aria-current="page"' if code == lang else "")
        + f">{esc(label)}</a>"
        for code, label in LANGS.items()
    )

    asks = []
    for i, (cat, items) in enumerate(groups):
        count = S["tools_one"] if len(items) == 1 else S["tools_many"].format(n=len(items))
        start = f'<span class="start">{esc(S["start_here"])}</span>' if cat == "safety" else ""
        asks.append(
            f'<li><a class="ask{" first" if cat == "safety" else ""}" href="#q-{cat}">'
            f'<span>{esc(S["q"][cat])}{start}</span><small>{esc(count)}</small></a></li>'
        )

    sections = []
    for cat, items in groups:
        rows = "".join(tool_row(t, lang, S, L) for t in items)
        sections.append(
            f'<section id="q-{cat}" data-group aria-labelledby="h-{cat}">'
            f'<h2 id="h-{cat}">{esc(S["q"][cat])}</h2><ul class="panel">{rows}</ul></section>'
        )

    tips = "".join(f"<li>{esc(tip)}</li>" for tip in S["tips"])
    G = GUIDE_UI[lang]
    scam = GUIDES["check-token-scams"]["lang"][lang]
    safe = (
        f'<section class="safe" id="safe"><h2>{esc(S["safety_title"])}</h2><ul>{tips}</ul>'
        f'<p class="more">{esc(G["full_guide"])} <a href="guides/check-token-scams/">{esc(scam["title"])}</a></p></section>'
    )
    guide_items = "".join(
        f'<li class="tool"><div><h3><a href="guides/{slug}/">{esc(g["lang"][lang]["title"])}</a></h3>'
        f'<p>{esc(g["lang"][lang]["description"])}</p></div></li>'
        for slug, g in GUIDES.items()
    )
    guides_html = (
        f'<section id="guides" aria-labelledby="h-guides"><h2 id="h-guides">{esc(G["guides_title"])}</h2>'
        f'<ul class="panel">{guide_items}</ul></section>'
    )

    join = ""
    actions = ""
    if cfg.get("bot_username"):
        actions += f'<a class="btn" href="https://t.me/{esc(cfg["bot_username"])}" rel="noopener">{esc(S["tg_button"])}</a>'
    if cfg.get("newsletter_action"):
        actions += (
            f'<form class="mail" action="{esc(cfg["newsletter_action"])}" method="post">'
            f'<label for="email">{esc(S["email_label"])}</label>'
            f'<input id="email" name="email" type="email" autocomplete="email" required>'
            f'<button class="btn" type="submit">{esc(S["email_button"])}</button></form>'
        )
    if actions:
        join = (
            f'<section class="join" id="join"><h2>{esc(S["join_title"])}</h2>'
            f'<p>{esc(S["join_text"])}</p>{actions}</section>'
        )

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(S["description"])}">
<link rel="canonical" href="{url}">
{alternates}
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(name)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(S["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#eef1f8">
<link rel="icon" href="../favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">{esc(S["skip"])}</a>
<div class="wrap">
<header class="top">
<a class="brand" href="./">{LOGO}<span>{esc(name)}</span></a>
<nav class="langs" aria-label="{esc(S["lang_label"])}">{langs_nav}</nav>
</header>
<main id="main">
<h1>{esc(S["h1"])}</h1>
<p class="lede">{esc(S["lede"])}</p>
<div><label class="sr" for="q">{esc(S["search_label"])}</label>
<input id="q" type="search" placeholder="{esc(S["search_ph"])}" autocomplete="off"></div>
<ul class="asks" id="asks">{"".join(asks)}</ul>
<p class="empty" id="empty" role="status" hidden>{esc(S["no_results"])}</p>
{"".join(sections)}
{guides_html}
{safe}
{join}
</main>
<footer class="fine">
<h2>{esc(S["disclosure_title"])}</h2>
<p>{esc(S["disclosure"])}</p>
<p>&copy; {year} {esc(name)}</p>
</footer>
</div>
<script>{SEARCH_JS}</script>
</body>
</html>
"""


def rich(text: str) -> str:
    """Экранирует текст и превращает **выделение** в <strong>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", esc(text))


def render_blocks(blocks: list) -> str:
    out = []
    for kind, value in blocks:
        if kind == "h":
            out.append(f"<h2>{esc(value)}</h2>")
        elif kind == "p":
            out.append(f"<p>{rich(value)}</p>")
        elif kind in ("ul", "ol"):
            items = "".join(f"<li>{rich(item)}</li>" for item in value)
            out.append(f"<{kind}>{items}</{kind}>")
        else:
            raise ValueError(f"неизвестный тип блока: {kind}")
    return "\n".join(out)


def render_guide(lang: str, slug: str, by_id: dict, cfg: dict) -> str:
    S, L, G = SITE[lang], STRINGS[lang], GUIDE_UI[lang]
    guide = GUIDES[slug]
    g = guide["lang"][lang]
    name, base = cfg["site_name"], cfg["base_url"]
    title = f"{g['title']} | {name}"
    url = f"{base}/{lang}/guides/{slug}/"

    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{base}/{code}/guides/{slug}/">' for code in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{base}/en/guides/{slug}/">'

    ld = json_ld(
        {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": g["title"],
            "description": g["description"],
            "inLanguage": lang,
            "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": name},
            "publisher": {"@type": "Organization", "name": name},
        }
    )

    langs_nav = "".join(
        f'<a href="../../../{code}/guides/{slug}/" lang="{code}" hreflang="{code}"'
        + (' aria-current="page"' if code == lang else "")
        + f">{esc(label)}</a>"
        for code, label in LANGS.items()
    )

    rows = "".join(tool_row(by_id[i], lang, S, L) for i in guide["tools"] if i in by_id)
    tools_box = (
        f'<section class="tools-box" aria-labelledby="h-tools"><h2 id="h-tools">{esc(G["tools_title"])}</h2>'
        f'<ul class="panel">{rows}</ul></section>'
        if rows
        else ""
    )

    return f"""<!doctype html>
<html lang="{lang}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(g["description"])}">
<link rel="canonical" href="{url}">
{alternates}
<meta property="og:type" content="article">
<meta property="og:site_name" content="{esc(name)}">
<meta property="og:title" content="{esc(g["title"])}">
<meta property="og:description" content="{esc(g["description"])}">
<meta property="og:url" content="{url}">
<meta property="og:locale" content="{OG_LOCALE[lang]}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#eef1f8">
<link rel="icon" href="../../../favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
<script type="application/ld+json">{ld}</script>
</head>
<body>
<a class="skip" href="#main">{esc(S["skip"])}</a>
<div class="wrap">
<header class="top">
<a class="brand" href="../../">{LOGO}<span>{esc(name)}</span></a>
<nav class="langs" aria-label="{esc(S["lang_label"])}">{langs_nav}</nav>
</header>
<main id="main" class="g">
<a class="back" href="../../">{esc(G["back"])}</a>
<h1>{esc(g["title"])}</h1>
<article class="prose">
<p class="lead">{esc(g["intro"])}</p>
{render_blocks(g["blocks"])}
</article>
{tools_box}
</main>
<footer class="fine">
<h2>{esc(S["disclosure_title"])}</h2>
<p>{esc(G["disclaimer"])} {esc(S["disclosure"])}</p>
<p>&copy; {dt.datetime.now(dt.timezone.utc).year} {esc(name)}</p>
</footer>
</div>
</body>
</html>
"""


def render_root(cfg: dict) -> str:
    name, base = cfg["site_name"], cfg["base_url"]
    alternates = "".join(
        f'<link rel="alternate" hreflang="{code}" href="{base}/{code}/">' for code in LANGS
    ) + f'<link rel="alternate" hreflang="x-default" href="{base}/">'
    links = "".join(
        f'<li><a class="ask" href="{code}/" lang="{code}" hreflang="{code}">{esc(label)}</a></li>'
        for code, label in LANGS.items()
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(name)}</title>
<meta name="description" content="{esc(SITE["en"]["description"])}">
<link rel="canonical" href="{base}/">
{alternates}
<link rel="icon" href="favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
</head>
<body>
<div class="wrap">
<header class="top"><span class="brand">{LOGO}<span>{esc(name)}</span></span></header>
<main>
<h1>{esc(name)}</h1>
<ul class="asks">{links}</ul>
</main>
</div>
<script>{ROOT_JS}</script>
</body>
</html>
"""


def render_404(cfg: dict) -> str:
    links = "".join(
        f'<li><a class="ask" href="/{code}/" lang="{code}">{esc(label)}</a></li>' for code, label in LANGS.items()
    )
    blocks = "".join(
        f'<p lang="{code}"><strong>{esc(SITE[code]["not_found"])}</strong><br>{esc(SITE[code]["not_found_text"])}</p>'
        for code in LANGS
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>404 {esc(cfg["site_name"])}</title>
<link rel="icon" href="/favicon.svg" type="image/svg+xml">
<style>{CSS}</style>
</head>
<body>
<div class="wrap"><main>
<h1>404</h1>
{blocks}
<ul class="asks">{links}</ul>
</main></div>
</body>
</html>
"""


def render_sitemap(cfg: dict, today: str) -> str:
    base = cfg["base_url"]
    entries = [f"<url><loc>{base}/</loc><lastmod>{today}</lastmod></url>"]
    for lang in LANGS:
        alts = "".join(
            f'<xhtml:link rel="alternate" hreflang="{c}" href="{base}/{c}/"/>' for c in LANGS
        ) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{base}/"/>'
        entries.append(f"<url><loc>{base}/{lang}/</loc><lastmod>{today}</lastmod>{alts}</url>")
    for slug in GUIDES:
        alts = "".join(
            f'<xhtml:link rel="alternate" hreflang="{c}" href="{base}/{c}/guides/{slug}/"/>' for c in LANGS
        ) + f'<xhtml:link rel="alternate" hreflang="x-default" href="{base}/en/guides/{slug}/"/>'
        for lang in LANGS:
            entries.append(
                f"<url><loc>{base}/{lang}/guides/{slug}/</loc><lastmod>{today}</lastmod>{alts}</url>"
            )
    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + "\n".join(entries)
        + "\n</urlset>\n"
    )


# --------------------------------------------------------------------------- сборка
def load_config(args: argparse.Namespace) -> dict:
    cfg = {
        "site_name": "ChainScout",
        "base_url": DEFAULT_BASE,
        "bot_username": "",
        "newsletter_action": "",
        "approved_sponsors": [],
    }
    path = HERE / "site.config.json"
    if path.exists():
        cfg.update(json.loads(path.read_text("utf-8")))
    if args.base_url:
        cfg["base_url"] = args.base_url
    if args.bot_username is not None:
        cfg["bot_username"] = args.bot_username
    if args.newsletter_action is not None:
        cfg["newsletter_action"] = args.newsletter_action
    cfg["base_url"] = cfg["base_url"].rstrip("/")
    if not cfg["base_url"].startswith("https://"):
        sys.exit("base_url должен начинаться с https://")
    if cfg["bot_username"] and not re.fullmatch(r"[A-Za-z0-9_]{5,32}", cfg["bot_username"]):
        sys.exit("bot_username: только латиница, цифры и _, 5-32 символа, без @")
    if cfg["newsletter_action"] and not cfg["newsletter_action"].startswith("https://"):
        sys.exit("newsletter_action должен начинаться с https://")
    return cfg


def load_tools(cfg: dict) -> list[dict]:
    for path in (HERE / "catalog.json", HERE.parent / "catalog.json"):
        if path.exists():
            catalog = json.loads(path.read_text("utf-8"))
            break
    else:
        sys.exit("catalog.json не найден рядом со скриптом")
    approved = set(cfg["approved_sponsors"])
    # Как в боте: спонсорские записи не показываются, пока владелец их не одобрил.
    return [x for x in catalog if not x.get("sponsor") or x["id"] in approved]


def main() -> None:
    parser = argparse.ArgumentParser(description="Сборка сайта ChainScout")
    parser.add_argument("--out", default=str(HERE / "dist"))
    parser.add_argument("--base-url")
    parser.add_argument("--bot-username")
    parser.add_argument("--newsletter-action")
    args = parser.parse_args()

    cfg = load_config(args)
    tools = load_tools(cfg)
    today = dt.datetime.now(dt.timezone.utc)
    out = Path(args.out)
    if out.exists():
        shutil.rmtree(out)
    out.mkdir(parents=True)

    for lang in LANGS:
        (out / lang).mkdir()
        (out / lang / "index.html").write_text(render_page(lang, tools, cfg, today.year), "utf-8")
    by_id = {t["id"]: t for t in tools}
    for slug in GUIDES:
        for lang in LANGS:
            gdir = out / lang / "guides" / slug
            gdir.mkdir(parents=True)
            (gdir / "index.html").write_text(render_guide(lang, slug, by_id, cfg), "utf-8")
    (out / "index.html").write_text(render_root(cfg), "utf-8")
    (out / "404.html").write_text(render_404(cfg), "utf-8")
    (out / "favicon.svg").write_text(FAVICON, "utf-8")
    (out / "sitemap.xml").write_text(render_sitemap(cfg, today.strftime("%Y-%m-%d")), "utf-8")
    (out / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {cfg['base_url']}/sitemap.xml\n", "utf-8")

    print(f"Готово: {len(tools)} инструментов, {len(GUIDES)} гидов, {len(LANGS)} языков -> {out}")
    if cfg["base_url"] == DEFAULT_BASE:
        print("Внимание: base_url всё ещё https://example.com. Впишите свой домен в site.config.json до публикации.")
    if not cfg["bot_username"] and not cfg["newsletter_action"]:
        print("Подсказка: раздел подписки скрыт. Укажите bot_username или newsletter_action в site.config.json.")


if __name__ == "__main__":
    main()
