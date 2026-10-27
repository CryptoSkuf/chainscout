"""Тексты интерфейса бота: en, fr, id, vi, sw.

Плейсхолдер {name} подставляется именем бота (BOT_NAME). Других фигурных скобок в строках быть не должно.
Теги <b> используются, потому что бот отправляет сообщения с parse_mode=HTML.
"""

LANGS = {
    "en": "English",
    "fr": "Français",
    "id": "Bahasa Indonesia",
    "vi": "Tiếng Việt",
    "sw": "Kiswahili",
}

STRINGS = {
    # ------------------------------------------------------------------ English
    "en": {
        "welcome": (
            "Hi! I'm <b>{name}</b> 👋\n"
            "I help you find AI-powered tools for researching and analysing crypto, "
            "from beginner-friendly to advanced.\n\n"
            "⚠️ I only share information about tools. This is not financial advice. "
            "Crypto is high-risk and nobody can guarantee a profit. "
            "Never share your seed phrase or private keys with anyone."
        ),
        "menu_title": "What would you like to do?",
        "btn_find": "🔎 Find a tool by goal",
        "btn_all": "🧰 All tools",
        "btn_sub": "🔔 Get weekly tips",
        "btn_unsub": "🔕 Stop weekly tips",
        "btn_about": "ℹ️ About",
        "btn_lang": "🌐 Language",
        "btn_back": "⬅️ Back",
        "btn_guides": "📚 Guides",
        "pick_guide": "Which guide do you want to read?",
        "btn_prev": "◀️ Previous",
        "btn_next": "Next ▶️",
        "btn_open": "🔗 Open website",
        "pick_cat": "What do you want to do?",
        "pick_tool": "Choose a tool:",
        "all_title": "All tools:",
        "category": "Category",
        "level": "Level",
        "lvl_beginner": "Beginner",
        "lvl_intermediate": "Intermediate",
        "lvl_advanced": "Advanced",
        "pricing_note": "Pricing and free plans change, so check the official site.",
        "disclaimer": "Information only, not financial advice.",
        "affiliate_note": "Disclosure: this link may earn us a commission at no extra cost to you.",
        "sponsored_tag": "Ad",
        "sponsored_note": "This listing is sponsored.",
        "subscribed": "✅ Done! You will get occasional tips about new tools. Send /stop to unsubscribe.",
        "unsubscribed": "🔕 You are unsubscribed.",
        "about": (
            "<b>{name}</b> is an independent directory of AI-powered and data tools for crypto research.\n\n"
            "• Information only: not financial advice, and we never give buy/sell signals.\n"
            "• Some links are affiliate links, and we mark them.\n"
            "• We store only your Telegram ID, language and tips subscription to run the bot."
        ),
        "nl_footer": "Not financial advice. Send /stop to unsubscribe.",
        "cat_market": "📈 Prices & charts",
        "cat_onchain": "⛓ On-chain analytics",
        "cat_sentiment": "📰 News & sentiment",
        "cat_research": "🧠 AI research",
        "cat_safety": "🛡 Scam & safety checks",
    },
    # ------------------------------------------------------------------ Français
    "fr": {
        "welcome": (
            "Salut ! Je suis <b>{name}</b> 👋\n"
            "Je t'aide à trouver des outils basés sur l'IA pour rechercher et analyser les cryptomonnaies, "
            "du niveau débutant au niveau avancé.\n\n"
            "⚠️ Je partage uniquement des informations sur les outils. Ce n'est pas un conseil financier. "
            "Les cryptos sont très risquées et personne ne peut garantir un gain. "
            "Ne communique jamais ta phrase secrète (seed) ni tes clés privées."
        ),
        "menu_title": "Que veux-tu faire ?",
        "btn_find": "🔎 Trouver un outil selon l'objectif",
        "btn_all": "🧰 Tous les outils",
        "btn_sub": "🔔 Recevoir des conseils hebdo",
        "btn_unsub": "🔕 Arrêter les conseils",
        "btn_about": "ℹ️ À propos",
        "btn_lang": "🌐 Langue",
        "btn_back": "⬅️ Retour",
        "btn_guides": "📚 Guides",
        "pick_guide": "Quel guide veux-tu lire ?",
        "btn_prev": "◀️ Précédent",
        "btn_next": "Suivant ▶️",
        "btn_open": "🔗 Ouvrir le site",
        "pick_cat": "Que veux-tu faire ?",
        "pick_tool": "Choisis un outil :",
        "all_title": "Tous les outils :",
        "category": "Catégorie",
        "level": "Niveau",
        "lvl_beginner": "Débutant",
        "lvl_intermediate": "Intermédiaire",
        "lvl_advanced": "Avancé",
        "pricing_note": "Les tarifs et offres gratuites changent : vérifie le site officiel.",
        "disclaimer": "Information uniquement, pas un conseil financier.",
        "affiliate_note": "Transparence : ce lien peut nous rapporter une commission, sans frais pour toi.",
        "sponsored_tag": "Pub",
        "sponsored_note": "Cette fiche est sponsorisée.",
        "subscribed": "✅ C'est fait ! Tu recevras de temps en temps des conseils sur de nouveaux outils. Envoie /stop pour te désabonner.",
        "unsubscribed": "🔕 Tu es désabonné.",
        "about": (
            "<b>{name}</b> est un annuaire indépendant d'outils d'IA et de données pour la recherche crypto.\n\n"
            "• Information uniquement : pas de conseil financier, et jamais de signaux d'achat/vente.\n"
            "• Certains liens sont des liens d'affiliation, et nous les signalons.\n"
            "• Nous ne stockons que ton identifiant Telegram, ta langue et ton abonnement aux conseils."
        ),
        "nl_footer": "Pas un conseil financier. Envoie /stop pour te désabonner.",
        "cat_market": "📈 Prix et graphiques",
        "cat_onchain": "⛓ Analyse on-chain",
        "cat_sentiment": "📰 Actualités et sentiment",
        "cat_research": "🧠 Recherche par IA",
        "cat_safety": "🛡 Anti-arnaque et sécurité",
    },
    # ------------------------------------------------------------------ Bahasa Indonesia
    "id": {
        "welcome": (
            "Halo! Saya <b>{name}</b> 👋\n"
            "Saya membantu Anda menemukan alat berbasis AI untuk meneliti dan menganalisis kripto, "
            "dari pemula hingga mahir.\n\n"
            "⚠️ Saya hanya membagikan informasi tentang alat. Ini bukan nasihat keuangan. "
            "Kripto berisiko tinggi dan tidak ada yang bisa menjamin keuntungan. "
            "Jangan pernah membagikan seed phrase atau private key Anda kepada siapa pun."
        ),
        "menu_title": "Apa yang ingin Anda lakukan?",
        "btn_find": "🔎 Cari alat sesuai tujuan",
        "btn_all": "🧰 Semua alat",
        "btn_sub": "🔔 Terima tips mingguan",
        "btn_unsub": "🔕 Berhenti tips mingguan",
        "btn_about": "ℹ️ Tentang",
        "btn_lang": "🌐 Bahasa",
        "btn_back": "⬅️ Kembali",
        "btn_guides": "📚 Panduan",
        "pick_guide": "Panduan mana yang ingin Anda baca?",
        "btn_prev": "◀️ Sebelumnya",
        "btn_next": "Berikutnya ▶️",
        "btn_open": "🔗 Buka situs",
        "pick_cat": "Apa yang ingin Anda lakukan?",
        "pick_tool": "Pilih alat:",
        "all_title": "Semua alat:",
        "category": "Kategori",
        "level": "Tingkat",
        "lvl_beginner": "Pemula",
        "lvl_intermediate": "Menengah",
        "lvl_advanced": "Mahir",
        "pricing_note": "Harga dan paket gratis bisa berubah, jadi cek situs resminya.",
        "disclaimer": "Hanya informasi, bukan nasihat keuangan.",
        "affiliate_note": "Pengungkapan: tautan ini bisa memberi kami komisi tanpa biaya tambahan bagi Anda.",
        "sponsored_tag": "Iklan",
        "sponsored_note": "Daftar ini disponsori.",
        "subscribed": "✅ Beres! Anda akan sesekali menerima tips tentang alat baru. Kirim /stop untuk berhenti.",
        "unsubscribed": "🔕 Anda sudah berhenti berlangganan.",
        "about": (
            "<b>{name}</b> adalah direktori independen alat AI dan data untuk riset kripto.\n\n"
            "• Hanya informasi: bukan nasihat keuangan, dan kami tidak pernah memberi sinyal beli/jual.\n"
            "• Sebagian tautan adalah tautan afiliasi, dan kami menandainya.\n"
            "• Kami hanya menyimpan ID Telegram, bahasa, dan status langganan tips Anda."
        ),
        "nl_footer": "Bukan nasihat keuangan. Kirim /stop untuk berhenti berlangganan.",
        "cat_market": "📈 Harga & grafik",
        "cat_onchain": "⛓ Analitik on-chain",
        "cat_sentiment": "📰 Berita & sentimen",
        "cat_research": "🧠 Riset dengan AI",
        "cat_safety": "🛡 Cek penipuan & keamanan",
    },
    # ------------------------------------------------------------------ Tiếng Việt
    "vi": {
        "welcome": (
            "Xin chào! Mình là <b>{name}</b> 👋\n"
            "Mình giúp bạn tìm các công cụ AI để nghiên cứu và phân tích tiền mã hóa, "
            "từ người mới đến nâng cao.\n\n"
            "⚠️ Mình chỉ chia sẻ thông tin về công cụ. Đây không phải lời khuyên tài chính. "
            "Tiền mã hóa có rủi ro cao và không ai đảm bảo được lợi nhuận. "
            "Tuyệt đối không chia sẻ cụm từ khôi phục (seed phrase) hay khóa riêng với bất kỳ ai."
        ),
        "menu_title": "Bạn muốn làm gì?",
        "btn_find": "🔎 Tìm công cụ theo mục tiêu",
        "btn_all": "🧰 Tất cả công cụ",
        "btn_sub": "🔔 Nhận mẹo hằng tuần",
        "btn_unsub": "🔕 Dừng nhận mẹo",
        "btn_about": "ℹ️ Giới thiệu",
        "btn_lang": "🌐 Ngôn ngữ",
        "btn_back": "⬅️ Quay lại",
        "btn_guides": "📚 Hướng dẫn",
        "pick_guide": "Bạn muốn đọc hướng dẫn nào?",
        "btn_prev": "◀️ Trước",
        "btn_next": "Tiếp ▶️",
        "btn_open": "🔗 Mở trang web",
        "pick_cat": "Bạn muốn làm gì?",
        "pick_tool": "Chọn một công cụ:",
        "all_title": "Tất cả công cụ:",
        "category": "Danh mục",
        "level": "Mức độ",
        "lvl_beginner": "Người mới",
        "lvl_intermediate": "Trung cấp",
        "lvl_advanced": "Nâng cao",
        "pricing_note": "Giá và gói miễn phí có thể thay đổi, hãy kiểm tra trang chính thức.",
        "disclaimer": "Chỉ là thông tin, không phải lời khuyên tài chính.",
        "affiliate_note": "Công khai: liên kết này có thể mang lại hoa hồng cho chúng mình, bạn không phải trả thêm.",
        "sponsored_tag": "QC",
        "sponsored_note": "Mục này được tài trợ.",
        "subscribed": "✅ Xong! Thỉnh thoảng bạn sẽ nhận mẹo về công cụ mới. Gửi /stop để hủy.",
        "unsubscribed": "🔕 Bạn đã hủy đăng ký.",
        "about": (
            "<b>{name}</b> là danh mục độc lập các công cụ AI và dữ liệu cho nghiên cứu tiền mã hóa.\n\n"
            "• Chỉ là thông tin: không phải lời khuyên tài chính, và chúng mình không bao giờ đưa tín hiệu mua/bán.\n"
            "• Một số liên kết là liên kết tiếp thị liên kết và đều được ghi rõ.\n"
            "• Chúng mình chỉ lưu ID Telegram, ngôn ngữ và trạng thái đăng ký nhận mẹo của bạn."
        ),
        "nl_footer": "Không phải lời khuyên tài chính. Gửi /stop để hủy đăng ký.",
        "cat_market": "📈 Giá & biểu đồ",
        "cat_onchain": "⛓ Phân tích on-chain",
        "cat_sentiment": "📰 Tin tức & tâm lý thị trường",
        "cat_research": "🧠 Nghiên cứu bằng AI",
        "cat_safety": "🛡 Kiểm tra lừa đảo & an toàn",
    },
    # ------------------------------------------------------------------ Kiswahili
    "sw": {
        "welcome": (
            "Habari! Mimi ni <b>{name}</b> 👋\n"
            "Nakusaidia kupata zana za AI za kutafiti na kuchambua sarafu za kidijitali (crypto), "
            "kuanzia wanaoanza hadi wataalamu.\n\n"
            "⚠️ Ninashiriki taarifa kuhusu zana tu. Huu si ushauri wa kifedha. "
            "Crypto ina hatari kubwa na hakuna anayeweza kuhakikisha faida. "
            "Usimpe mtu yeyote seed phrase wala funguo zako za siri."
        ),
        "menu_title": "Ungependa kufanya nini?",
        "btn_find": "🔎 Tafuta zana kulingana na lengo",
        "btn_all": "🧰 Zana zote",
        "btn_sub": "🔔 Pata vidokezo vya kila wiki",
        "btn_unsub": "🔕 Acha vidokezo",
        "btn_about": "ℹ️ Kuhusu",
        "btn_lang": "🌐 Lugha",
        "btn_back": "⬅️ Rudi",
        "btn_guides": "📚 Miongozo",
        "pick_guide": "Ungependa kusoma mwongozo upi?",
        "btn_prev": "◀️ Nyuma",
        "btn_next": "Mbele ▶️",
        "btn_open": "🔗 Fungua tovuti",
        "pick_cat": "Ungependa kufanya nini?",
        "pick_tool": "Chagua zana:",
        "all_title": "Zana zote:",
        "category": "Kundi",
        "level": "Kiwango",
        "lvl_beginner": "Anayeanza",
        "lvl_intermediate": "Wa kati",
        "lvl_advanced": "Mtaalamu",
        "pricing_note": "Bei na mipango ya bure hubadilika, kwa hiyo angalia tovuti rasmi.",
        "disclaimer": "Taarifa tu, si ushauri wa kifedha.",
        "affiliate_note": "Ufafanuzi: kiungo hiki kinaweza kutupa kamisheni bila gharama ya ziada kwako.",
        "sponsored_tag": "Tangazo",
        "sponsored_note": "Orodha hii imedhaminiwa.",
        "subscribed": "✅ Tayari! Utapokea vidokezo kuhusu zana mpya mara kwa mara. Tuma /stop kujiondoa.",
        "unsubscribed": "🔕 Umejiondoa.",
        "about": (
            "<b>{name}</b> ni orodha huru ya zana za AI na data za utafiti wa crypto.\n\n"
            "• Taarifa tu: si ushauri wa kifedha, na hatutoi kamwe ishara za kununua/kuuza.\n"
            "• Baadhi ya viungo ni vya ushirika (affiliate) na tunaviweka alama.\n"
            "• Tunahifadhi tu ID yako ya Telegram, lugha na usajili wa vidokezo."
        ),
        "nl_footer": "Si ushauri wa kifedha. Tuma /stop kujiondoa.",
        "cat_market": "📈 Bei na chati",
        "cat_onchain": "⛓ Uchambuzi wa on-chain",
        "cat_sentiment": "📰 Habari na hisia za soko",
        "cat_research": "🧠 Utafiti kwa AI",
        "cat_safety": "🛡 Ukaguzi wa ulaghai na usalama",
    },
}
