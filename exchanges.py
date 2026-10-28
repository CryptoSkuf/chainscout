"""Биржи для сайта ChainScout: ссылки на популярные платформы Африки и ЮВА.

Источники статусов: обзор Datawallet «Best Crypto Exchanges in Africa for 2026» и
обзор Les Afriques (октябрь 2026); для Индонезии, Филиппин и Вьетнама отметка
«проверьте регистрацию» без утверждений о лицензиях. Все записи нужно перепроверить
вручную (поле checked) перед публикацией: статусы бирж меняются быстро.

Поле affiliate_url пустое. Когда появится партнёрская ссылка, впишите её сюда:
кнопка поведёт по ней, появится метка «Partner link» и rel="sponsored nofollow".
Логотипы бирж не рисуем: это товарные знаки. Если нужны, берите официальные
материалы из партнёрской программы биржи.
"""

# regions: africa | sea. countries: коды стран, язык не нужен.
# tags: ключи из TAGS ниже.
EXCHANGES = [
    {"id": "binance", "name": "Binance", "url": "https://www.binance.com/", "affiliate_url": "", "checked": None,
     "regions": ["africa", "sea"], "countries": ["KE", "ZA", "GH", "VN", "ID"],
     "tags": ["p2p", "mobile", "no_afr", "ng_ended"]},
    {"id": "bybit", "name": "Bybit", "url": "https://www.bybit.com/", "affiliate_url": "", "checked": None,
     "regions": ["africa", "sea"], "countries": ["NG", "KE", "ZA", "GH", "VN"],
     "tags": ["p2p", "no_afr"]},
    {"id": "okx", "name": "OKX", "url": "https://www.okx.com/", "affiliate_url": "", "checked": None,
     "regions": ["africa", "sea"], "countries": ["NG", "KE", "ZA", "VN"],
     "tags": ["p2p", "no_afr"]},
    {"id": "bitget", "name": "Bitget", "url": "https://www.bitget.com/", "affiliate_url": "", "checked": None,
     "regions": ["africa", "sea"], "countries": ["NG", "KE", "ZA", "ET", "VN"],
     "tags": ["p2p", "mobile", "no_afr"]},
    {"id": "yellowcard", "name": "Yellow Card", "url": "https://yellowcard.io/", "affiliate_url": "", "checked": None,
     "regions": ["africa"], "countries": ["NG", "KE", "ZA", "GH"],
     "tags": ["many_africa", "lic_za"]},
    {"id": "luno", "name": "Luno", "url": "https://www.luno.com/", "affiliate_url": "", "checked": None,
     "regions": ["africa"], "countries": ["ZA", "NG"],
     "tags": ["lic_za"]},
    {"id": "quidax", "name": "Quidax", "url": "https://www.quidax.com/", "affiliate_url": "", "checked": None,
     "regions": ["africa"], "countries": ["NG"],
     "tags": ["local", "prov_ng"]},
    {"id": "indodax", "name": "Indodax", "url": "https://indodax.com/", "affiliate_url": "", "checked": None,
     "regions": ["sea"], "countries": ["ID"], "tags": ["local", "check_reg"]},
    {"id": "tokocrypto", "name": "Tokocrypto", "url": "https://www.tokocrypto.com/", "affiliate_url": "", "checked": None,
     "regions": ["sea"], "countries": ["ID"], "tags": ["local", "check_reg"]},
    {"id": "pintu", "name": "Pintu", "url": "https://pintu.co.id/", "affiliate_url": "", "checked": None,
     "regions": ["sea"], "countries": ["ID"], "tags": ["local", "check_reg"]},
    {"id": "coinsph", "name": "Coins.ph", "url": "https://coins.ph/", "affiliate_url": "", "checked": None,
     "regions": ["sea"], "countries": ["PH"], "tags": ["local", "check_reg"]},
    {"id": "pdax", "name": "PDAX", "url": "https://pdax.ph/", "affiliate_url": "", "checked": None,
     "regions": ["sea"], "countries": ["PH"], "tags": ["local", "check_reg"]},
    {"id": "remitano", "name": "Remitano", "url": "https://remitano.com/", "affiliate_url": "", "checked": None,
     "regions": ["sea"], "countries": ["VN"], "tags": ["p2p", "check_reg"]},
]

TAGS = {
    "en": {
        "p2p": "P2P market",
        "mobile": "Mobile money",
        "local": "Local platform",
        "many_africa": "20+ African countries",
        "lic_za": "South Africa: licensed (FSCA)",
        "prov_ng": "Nigeria: provisional SEC approval",
        "no_afr": "No African licence (2026 reviews)",
        "ng_ended": "Naira services ended in 2024",
        "check_reg": "Check local registration",
    },
    "fr": {
        "p2p": "Marché P2P",
        "mobile": "Mobile money",
        "local": "Plateforme locale",
        "many_africa": "Plus de 20 pays africains",
        "lic_za": "Afrique du Sud : agréée (FSCA)",
        "prov_ng": "Nigeria : accord provisoire de la SEC",
        "no_afr": "Pas de licence africaine (avis 2026)",
        "ng_ended": "Services en naira arrêtés en 2024",
        "check_reg": "Vérifiez l'enregistrement local",
    },
    "id": {
        "p2p": "Pasar P2P",
        "mobile": "Uang seluler",
        "local": "Platform lokal",
        "many_africa": "20+ negara Afrika",
        "lic_za": "Afrika Selatan: berlisensi (FSCA)",
        "prov_ng": "Nigeria: persetujuan sementara SEC",
        "no_afr": "Tanpa lisensi Afrika (ulasan 2026)",
        "ng_ended": "Layanan naira dihentikan pada 2024",
        "check_reg": "Cek pendaftaran lokal",
    },
    "vi": {
        "p2p": "Chợ P2P",
        "mobile": "Tiền di động",
        "local": "Nền tảng trong nước",
        "many_africa": "Hơn 20 nước châu Phi",
        "lic_za": "Nam Phi: có giấy phép (FSCA)",
        "prov_ng": "Nigeria: SEC chấp thuận tạm thời",
        "no_afr": "Không có giấy phép ở châu Phi (đánh giá 2026)",
        "ng_ended": "Ngừng dịch vụ naira từ 2024",
        "check_reg": "Kiểm tra đăng ký tại địa phương",
    },
    "sw": {
        "p2p": "Soko la P2P",
        "mobile": "Pesa za simu",
        "local": "Jukwaa la ndani",
        "many_africa": "Nchi 20+ za Afrika",
        "lic_za": "Afrika Kusini: ina leseni (FSCA)",
        "prov_ng": "Nigeria: idhini ya muda ya SEC",
        "no_afr": "Haina leseni Afrika (hakiki za 2026)",
        "ng_ended": "Huduma za naira zilisitishwa 2024",
        "check_reg": "Angalia usajili wa ndani",
    },
}

UI = {
    "en": {
        "title": "Exchanges people use in Africa and Southeast Asia",
        "intro": "A starting list, not a recommendation. Availability, licences and local rules change often and differ by country. Check that a platform is allowed where you live before you sign up. Never send money to someone who contacted you first.",
        "all": "All", "africa": "Africa", "sea": "Southeast Asia",
        "open": "Open {name}", "partner": "Partner link", "countries": "Countries",
    },
    "fr": {
        "title": "Plateformes utilisées en Afrique et en Asie du Sud-Est",
        "intro": "Une liste de départ, pas une recommandation. La disponibilité, les licences et les règles locales changent souvent selon les pays. Vérifiez qu'une plateforme est autorisée là où vous vivez avant de vous inscrire. N'envoyez jamais d'argent à quelqu'un qui vous a contacté en premier.",
        "all": "Tout", "africa": "Afrique", "sea": "Asie du Sud-Est",
        "open": "Ouvrir {name}", "partner": "Lien partenaire", "countries": "Pays",
    },
    "id": {
        "title": "Platform yang dipakai di Afrika dan Asia Tenggara",
        "intro": "Daftar awal, bukan rekomendasi. Ketersediaan, lisensi, dan aturan setempat sering berubah dan berbeda di tiap negara. Pastikan platform diizinkan di tempat Anda tinggal sebelum mendaftar. Jangan pernah mengirim uang kepada orang yang menghubungi Anda lebih dulu.",
        "all": "Semua", "africa": "Afrika", "sea": "Asia Tenggara",
        "open": "Buka {name}", "partner": "Tautan mitra", "countries": "Negara",
    },
    "vi": {
        "title": "Các nền tảng được dùng ở châu Phi và Đông Nam Á",
        "intro": "Đây là danh sách để bắt đầu, không phải lời khuyên. Việc cung cấp dịch vụ, giấy phép và quy định địa phương thay đổi thường xuyên và khác nhau theo từng nước. Hãy kiểm tra nền tảng có được phép nơi bạn sống trước khi đăng ký. Đừng bao giờ chuyển tiền cho người đã chủ động liên hệ với bạn.",
        "all": "Tất cả", "africa": "Châu Phi", "sea": "Đông Nam Á",
        "open": "Mở {name}", "partner": "Liên kết đối tác", "countries": "Quốc gia",
    },
    "sw": {
        "title": "Majukwaa yanayotumika Afrika na Kusini-Mashariki mwa Asia",
        "intro": "Orodha ya kuanzia, si pendekezo. Upatikanaji, leseni na sheria za ndani hubadilika mara kwa mara na hutofautiana kati ya nchi. Hakikisha jukwaa linaruhusiwa unapoishi kabla ya kujisajili. Usitume pesa kwa mtu aliyekuwasiliana nawe kwanza.",
        "all": "Yote", "africa": "Afrika", "sea": "Asia ya Kusini-Mashariki",
        "open": "Fungua {name}", "partner": "Kiungo cha mshirika", "countries": "Nchi",
    },
}
