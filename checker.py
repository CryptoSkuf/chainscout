"""Страница «Проверка токена» (Token Check): тексты на 6 языках и скрипт, который работает в браузере читателя.

Браузер сам спрашивает бесплатные открытые API GoPlus и CoinGecko: своего сервера, ключей и расходов нет.
Итог никогда не говорит «безопасно»: только найденные предупреждения и пункты, которые читатель проверяет сам.
Пороги: STOP только для honeypot и налога 50% и выше; остальное предупреждения (см. CHECK_JS).
Данные токена (названия, адреса) приходят из сети и могут быть подделаны, поэтому в скрипте всё выводится через textContent.
"""

CHECK_UI = {
    "en": {
        "label_net": "Network", "label_addr": "Token contract address", "ph_addr": "0x...",
        "btn": "Check token", "btn_copy": "Copy link to this result", "copied": "Link copied",
        "privacy": "Your browser asks GoPlus and CoinGecko directly. We do not see or store what you type.",
        "scope": "Works for EVM networks (Ethereum, BNB Chain, Polygon, Arbitrum, Base, Optimism, Avalanche), and for Solana and TRON. For Solana and TRON the data is thinner, so more items show \"No data\".",
        "loading": "Checking... this can take a few seconds.",
        "err_addr": "This is not a valid address for this network. EVM: 0x and 42 characters. TRON: starts with T, 34 characters. Solana: 32 to 44 letters and numbers.",
        "err_api": "Could not reach the data sources. Try again later, or open the links below.",
        "err_rate": "The free data source is busy. Wait a minute and try again.",
        "no_gp": "GoPlus has no data for this token. The security checks below are unknown.",
        "token_title": "Token found", "not_found": "Token not found on CoinGecko",
        "cap": "Market cap", "vol": "24h volume", "site": "Website on CoinGecko",
        "open_cg": "Open on CoinGecko", "open_gp": "Open on GoPlus",
        "st": {"ok": "OK", "flag": "Warning", "stop": "STOP", "unknown": "No data", "manual": "You check"},
        "sum_title": "Result",
        "sum_stop": "{n} STOP item(s) found. Do not buy and do not approve anything.",
        "sum_flag": "{n} warning(s) found. Read each one before you go on.",
        "sum_ok": "These automatic checks found no red flags.",
        "sum_note": "This is not a guarantee. New scams are built to pass checks. The \"You check\" items need your own work.",
        "steps": ["Step 1. Is it the real token?", "Step 2. Security scan", "Step 3. Market data", "Step 4. Holders and the project", "Step 5. Before you spend"],
        "rules": {
            "cg": ["Listed on CoinGecko", "Not listed on CoinGecko. New or unknown tokens are much riskier. Make sure this is the official contract address."],
            "honeypot": ["Can be sold (not a honeypot)", "The scan says this token may be impossible to sell. Do not buy."],
            "sell_tax": ["Sell tax is low", "High sell tax ({v}). A big part of your money is taken when you sell."],
            "buy_tax": ["Buy tax is low", "High buy tax ({v}). A big part of your money is taken when you buy."],
            "mint": ["Owner cannot mint new tokens", "The owner can create new tokens. This can push the price down."],
            "owner": ["No hidden or dangerous owner powers", "The owner has special powers: a hidden owner, taking back ownership, or changing balances."],
            "code": ["Code is open and cannot be changed in secret", "The code is not verified, or the owner can change it later."],
            "limits": ["No pause, blacklist or trade limits", "The owner can stop trading, block wallets or change trade rules."],
            "lp": ["Liquidity is locked or burned", "Most of the liquidity is not locked ({v} locked). The creators may be able to take it out."],
            "volume": ["Trading volume is reasonable", "Very low trading volume compared with the market cap. One trade can move the price."],
            "markets": ["Trades on more than one market", "The token trades on very few markets."],
            "age": ["Not a brand-new token", "The token is only {v} days old."],
            "top": ["Supply is not held by a few wallets", "The 10 biggest wallets hold {v} of the supply."],
            "creator": ["Creator and owner hold a small share", "The creator or the owner holds a big share of the supply ({v})."],
            "holders": ["Enough holders", "Very few holders ({v})."],
        },
        "manual": {
            "m_site": "Open the project's official website yourself and compare its contract address with the one you checked.",
            "m_team": "The team is public and the project explains in simple words what it does.",
            "m_unlock": "Check if big token unlocks are coming soon. New supply can push the price down.",
            "m_limit": "Decide the most you can lose completely, and do not go above it.",
            "m_test": "Send a small test first. Check the network and the address.",
        },
        "how_title": "How the checks work",
        "how": [
            "STOP: the scan says you cannot sell, or a buy or sell tax of 50% or more.",
            "Warning: tax above 10%, new tokens can be minted, hidden or dangerous owner powers, code not verified or changeable, pause or blacklist functions, less than half of the liquidity locked, tiny volume, fewer than 2 markets, younger than 30 days, top 10 wallets hold more than half, creator or owner holds more than 10%, fewer than 100 holders.",
            "No data: the source did not give this information. That is not the same as OK.",
        ],
        "full_cta": "Read the full checklist guide",
    },
    "fr": {
        "label_net": "Réseau", "label_addr": "Adresse du contrat du token", "ph_addr": "0x...",
        "btn": "Vérifier le token", "btn_copy": "Copier le lien de ce résultat", "copied": "Lien copié",
        "privacy": "Votre navigateur interroge directement GoPlus et CoinGecko. Nous ne voyons ni ne stockons ce que vous saisissez.",
        "scope": "Fonctionne pour les réseaux EVM (Ethereum, BNB Chain, Polygon, Arbitrum, Base, Optimism, Avalanche), ainsi que pour Solana et TRON. Pour Solana et TRON, les données sont plus maigres : davantage de lignes affichent « Pas de données ».",
        "loading": "Vérification en cours... cela peut prendre quelques secondes.",
        "err_addr": "Adresse non valide pour ce réseau. EVM : 0x et 42 caractères. TRON : commence par T, 34 caractères. Solana : 32 à 44 lettres et chiffres.",
        "err_api": "Impossible de joindre les sources de données. Réessayez plus tard ou ouvrez les liens ci-dessous.",
        "err_rate": "La source de données gratuite est occupée. Attendez une minute et réessayez.",
        "no_gp": "GoPlus n'a pas de données sur ce token. Les contrôles de sécurité ci-dessous sont inconnus.",
        "token_title": "Token trouvé", "not_found": "Token introuvable sur CoinGecko",
        "cap": "Capitalisation", "vol": "Volume 24 h", "site": "Site indiqué sur CoinGecko",
        "open_cg": "Ouvrir sur CoinGecko", "open_gp": "Ouvrir sur GoPlus",
        "st": {"ok": "OK", "flag": "Alerte", "stop": "ARRÊT", "unknown": "Pas de données", "manual": "À vérifier vous-même"},
        "sum_title": "Résultat",
        "sum_stop": "{n} point(s) ARRÊT trouvé(s). N'achetez pas et n'autorisez rien.",
        "sum_flag": "{n} alerte(s) trouvée(s). Lisez chacune avant de continuer.",
        "sum_ok": "Ces contrôles automatiques n'ont trouvé aucun signal d'alerte.",
        "sum_note": "Ce n'est pas une garantie. Les nouvelles arnaques sont conçues pour passer les contrôles. Les points « À vérifier vous-même » demandent votre propre travail.",
        "steps": ["Étape 1. Est-ce le vrai token ?", "Étape 2. Analyse de sécurité", "Étape 3. Données de marché", "Étape 4. Détenteurs et projet", "Étape 5. Avant de dépenser"],
        "rules": {
            "cg": ["Référencé sur CoinGecko", "Non référencé sur CoinGecko. Les tokens récents ou inconnus sont bien plus risqués. Vérifiez que c'est l'adresse officielle."],
            "honeypot": ["Peut être vendu (pas un honeypot)", "L'analyse indique que ce token peut être impossible à vendre. N'achetez pas."],
            "sell_tax": ["Taxe de vente faible", "Taxe de vente élevée ({v}). Une grande partie de votre argent est prélevée à la vente."],
            "buy_tax": ["Taxe d'achat faible", "Taxe d'achat élevée ({v}). Une grande partie de votre argent est prélevée à l'achat."],
            "mint": ["Le propriétaire ne peut pas créer de nouveaux tokens", "Le propriétaire peut créer de nouveaux tokens. Cela peut faire baisser le prix."],
            "owner": ["Pas de pouvoirs cachés ou dangereux du propriétaire", "Le propriétaire a des pouvoirs spéciaux : propriétaire caché, reprise de propriété ou modification des soldes."],
            "code": ["Code ouvert et non modifiable en secret", "Le code n'est pas vérifié, ou le propriétaire peut le modifier plus tard."],
            "limits": ["Pas de pause, de liste noire ni de limites d'échange", "Le propriétaire peut arrêter les échanges, bloquer des portefeuilles ou changer les règles."],
            "lp": ["Liquidité verrouillée ou brûlée", "La majeure partie de la liquidité n'est pas verrouillée ({v} verrouillé). Les créateurs peuvent peut-être la retirer."],
            "volume": ["Volume d'échange raisonnable", "Volume très faible par rapport à la capitalisation. Un seul échange peut faire bouger le prix."],
            "markets": ["Échangé sur plus d'un marché", "Le token s'échange sur très peu de marchés."],
            "age": ["Pas un token tout neuf", "Le token a seulement {v} jours."],
            "top": ["L'offre n'est pas détenue par quelques portefeuilles", "Les 10 plus gros portefeuilles détiennent {v} de l'offre."],
            "creator": ["Le créateur et le propriétaire détiennent une petite part", "Le créateur ou le propriétaire détient une grande part de l'offre ({v})."],
            "holders": ["Assez de détenteurs", "Très peu de détenteurs ({v})."],
        },
        "manual": {
            "m_site": "Ouvrez vous-même le site officiel du projet et comparez son adresse de contrat avec celle que vous avez vérifiée.",
            "m_team": "L'équipe est publique et le projet explique en termes simples ce qu'il fait.",
            "m_unlock": "Vérifiez si de gros déblocages de tokens arrivent bientôt. Une nouvelle offre peut faire baisser le prix.",
            "m_limit": "Fixez le montant maximal que vous pouvez perdre entièrement, et ne le dépassez pas.",
            "m_test": "Envoyez d'abord un petit montant de test. Vérifiez le réseau et l'adresse.",
        },
        "how_title": "Comment fonctionnent les contrôles",
        "how": [
            "ARRÊT : l'analyse dit qu'on ne peut pas vendre, ou une taxe d'achat ou de vente de 50 % ou plus.",
            "Alerte : taxe supérieure à 10 %, création possible de nouveaux tokens, pouvoirs cachés ou dangereux du propriétaire, code non vérifié ou modifiable, fonctions de pause ou de liste noire, moins de la moitié de la liquidité verrouillée, volume minuscule, moins de 2 marchés, moins de 30 jours, 10 plus gros portefeuilles à plus de la moitié, créateur ou propriétaire à plus de 10 %, moins de 100 détenteurs.",
            "Pas de données : la source n'a pas donné cette information. Ce n'est pas la même chose que OK.",
        ],
        "full_cta": "Lire le guide complet de la checklist",
    },
    "id": {
        "label_net": "Jaringan", "label_addr": "Alamat kontrak token", "ph_addr": "0x...",
        "btn": "Periksa token", "btn_copy": "Salin tautan hasil ini", "copied": "Tautan disalin",
        "privacy": "Peramban Anda meminta data langsung ke GoPlus dan CoinGecko. Kami tidak melihat atau menyimpan yang Anda ketik.",
        "scope": "Berlaku untuk jaringan EVM (Ethereum, BNB Chain, Polygon, Arbitrum, Base, Optimism, Avalanche), juga Solana dan TRON. Untuk Solana dan TRON datanya lebih sedikit, jadi lebih banyak baris berstatus \"Tidak ada data\".",
        "loading": "Memeriksa... ini bisa memakan beberapa detik.",
        "err_addr": "Alamat tidak valid untuk jaringan ini. EVM: 0x dan 42 karakter. TRON: diawali T, 34 karakter. Solana: 32 sampai 44 huruf dan angka.",
        "err_api": "Tidak bisa menjangkau sumber data. Coba lagi nanti, atau buka tautan di bawah.",
        "err_rate": "Sumber data gratis sedang sibuk. Tunggu semenit lalu coba lagi.",
        "no_gp": "GoPlus tidak punya data untuk token ini. Pemeriksaan keamanan di bawah tidak diketahui.",
        "token_title": "Token ditemukan", "not_found": "Token tidak ditemukan di CoinGecko",
        "cap": "Kapitalisasi pasar", "vol": "Volume 24 jam", "site": "Situs di CoinGecko",
        "open_cg": "Buka di CoinGecko", "open_gp": "Buka di GoPlus",
        "st": {"ok": "OK", "flag": "Peringatan", "stop": "BERHENTI", "unknown": "Tanpa data", "manual": "Periksa sendiri"},
        "sum_title": "Hasil",
        "sum_stop": "{n} poin BERHENTI ditemukan. Jangan beli dan jangan beri izin apa pun.",
        "sum_flag": "{n} peringatan ditemukan. Baca masing-masing sebelum lanjut.",
        "sum_ok": "Pemeriksaan otomatis ini tidak menemukan tanda bahaya.",
        "sum_note": "Ini bukan jaminan. Penipuan baru dibuat untuk lolos pemeriksaan. Poin \"Periksa sendiri\" butuh kerja Anda sendiri.",
        "steps": ["Langkah 1. Apakah ini token yang asli?", "Langkah 2. Pemindaian keamanan", "Langkah 3. Data pasar", "Langkah 4. Pemegang dan proyek", "Langkah 5. Sebelum mengeluarkan uang"],
        "rules": {
            "cg": ["Terdaftar di CoinGecko", "Tidak terdaftar di CoinGecko. Token baru atau tak dikenal jauh lebih berisiko. Pastikan ini alamat kontrak resmi."],
            "honeypot": ["Bisa dijual (bukan honeypot)", "Pemindaian menyatakan token ini mungkin tidak bisa dijual. Jangan beli."],
            "sell_tax": ["Pajak jual rendah", "Pajak jual tinggi ({v}). Sebagian besar uang Anda diambil saat menjual."],
            "buy_tax": ["Pajak beli rendah", "Pajak beli tinggi ({v}). Sebagian besar uang Anda diambil saat membeli."],
            "mint": ["Pemilik tidak bisa mencetak token baru", "Pemilik bisa membuat token baru. Ini bisa menekan harga."],
            "owner": ["Tanpa kuasa pemilik yang tersembunyi atau berbahaya", "Pemilik punya kuasa khusus: pemilik tersembunyi, mengambil kembali kepemilikan, atau mengubah saldo."],
            "code": ["Kode terbuka dan tidak bisa diubah diam-diam", "Kode tidak terverifikasi, atau pemilik bisa mengubahnya nanti."],
            "limits": ["Tanpa jeda, daftar hitam, atau batas perdagangan", "Pemilik bisa menghentikan perdagangan, memblokir dompet, atau mengubah aturan."],
            "lp": ["Likuiditas dikunci atau dibakar", "Sebagian besar likuiditas tidak dikunci ({v} terkunci). Pembuat mungkin bisa menariknya."],
            "volume": ["Volume perdagangan wajar", "Volume sangat rendah dibanding kapitalisasi pasar. Satu transaksi bisa menggerakkan harga."],
            "markets": ["Diperdagangkan di lebih dari satu pasar", "Token diperdagangkan di sangat sedikit pasar."],
            "age": ["Bukan token yang baru lahir", "Token baru berusia {v} hari."],
            "top": ["Pasokan tidak dipegang segelintir dompet", "10 dompet terbesar memegang {v} dari pasokan."],
            "creator": ["Pembuat dan pemilik memegang bagian kecil", "Pembuat atau pemilik memegang bagian besar pasokan ({v})."],
            "holders": ["Pemegang cukup banyak", "Pemegang sangat sedikit ({v})."],
        },
        "manual": {
            "m_site": "Buka sendiri situs resmi proyek dan bandingkan alamat kontraknya dengan yang Anda periksa.",
            "m_team": "Tim bersifat publik dan proyek menjelaskan dengan kata sederhana apa yang dikerjakannya.",
            "m_unlock": "Periksa apakah ada pembukaan token besar dalam waktu dekat. Pasokan baru bisa menekan harga.",
            "m_limit": "Tetapkan jumlah maksimal yang sanggup Anda rugikan sepenuhnya, dan jangan melebihinya.",
            "m_test": "Kirim jumlah uji kecil dulu. Periksa jaringan dan alamatnya.",
        },
        "how_title": "Cara kerja pemeriksaan",
        "how": [
            "BERHENTI: pemindaian menyatakan tidak bisa dijual, atau pajak beli atau jual 50% atau lebih.",
            "Peringatan: pajak di atas 10%, token baru bisa dicetak, kuasa pemilik tersembunyi atau berbahaya, kode tidak terverifikasi atau bisa diubah, fungsi jeda atau daftar hitam, likuiditas terkunci kurang dari setengah, volume sangat kecil, kurang dari 2 pasar, berusia di bawah 30 hari, 10 dompet teratas memegang lebih dari setengah, pembuat atau pemilik memegang lebih dari 10%, pemegang kurang dari 100.",
            "Tanpa data: sumber tidak memberi informasi ini. Itu tidak sama dengan OK.",
        ],
        "full_cta": "Baca panduan checklist lengkap",
    },
    "vi": {
        "label_net": "Mạng", "label_addr": "Địa chỉ hợp đồng của token", "ph_addr": "0x...",
        "btn": "Kiểm tra token", "btn_copy": "Sao chép liên kết kết quả này", "copied": "Đã sao chép liên kết",
        "privacy": "Trình duyệt của bạn hỏi trực tiếp GoPlus và CoinGecko. Chúng tôi không thấy và không lưu những gì bạn nhập.",
        "scope": "Hỗ trợ các mạng EVM (Ethereum, BNB Chain, Polygon, Arbitrum, Base, Optimism, Avalanche), cùng Solana và TRON. Với Solana và TRON, dữ liệu ít hơn nên nhiều dòng hiện \"Không có dữ liệu\".",
        "loading": "Đang kiểm tra... có thể mất vài giây.",
        "err_addr": "Địa chỉ không hợp lệ cho mạng này. EVM: 0x và 42 ký tự. TRON: bắt đầu bằng T, 34 ký tự. Solana: 32 đến 44 chữ và số.",
        "err_api": "Không kết nối được tới nguồn dữ liệu. Hãy thử lại sau hoặc mở các liên kết bên dưới.",
        "err_rate": "Nguồn dữ liệu miễn phí đang bận. Hãy chờ một phút rồi thử lại.",
        "no_gp": "GoPlus không có dữ liệu về token này. Các kiểm tra bảo mật bên dưới là chưa biết.",
        "token_title": "Đã tìm thấy token", "not_found": "Không tìm thấy token trên CoinGecko",
        "cap": "Vốn hóa", "vol": "Khối lượng 24 giờ", "site": "Trang web trên CoinGecko",
        "open_cg": "Mở trên CoinGecko", "open_gp": "Mở trên GoPlus",
        "st": {"ok": "OK", "flag": "Cảnh báo", "stop": "DỪNG", "unknown": "Không có dữ liệu", "manual": "Tự kiểm tra"},
        "sum_title": "Kết quả",
        "sum_stop": "Tìm thấy {n} mục DỪNG. Đừng mua và đừng cấp quyền gì.",
        "sum_flag": "Tìm thấy {n} cảnh báo. Hãy đọc từng cảnh báo trước khi đi tiếp.",
        "sum_ok": "Các kiểm tra tự động này không thấy dấu hiệu cảnh báo.",
        "sum_note": "Đây không phải là đảm bảo. Các chiêu lừa mới được tạo ra để vượt qua kiểm tra. Các mục \"Tự kiểm tra\" cần bạn tự làm.",
        "steps": ["Bước 1. Đây có phải token thật không?", "Bước 2. Quét bảo mật", "Bước 3. Dữ liệu thị trường", "Bước 4. Người nắm giữ và dự án", "Bước 5. Trước khi chi tiền"],
        "rules": {
            "cg": ["Có trên CoinGecko", "Không có trên CoinGecko. Token mới hoặc không rõ rủi ro cao hơn nhiều. Hãy chắc đây là địa chỉ chính thức."],
            "honeypot": ["Bán được (không phải honeypot)", "Kết quả quét cho biết token này có thể không bán được. Đừng mua."],
            "sell_tax": ["Thuế bán thấp", "Thuế bán cao ({v}). Một phần lớn tiền của bạn bị lấy khi bán."],
            "buy_tax": ["Thuế mua thấp", "Thuế mua cao ({v}). Một phần lớn tiền của bạn bị lấy khi mua."],
            "mint": ["Chủ sở hữu không thể tạo thêm token", "Chủ sở hữu có thể tạo thêm token. Điều này có thể kéo giá xuống."],
            "owner": ["Không có quyền ẩn hoặc nguy hiểm của chủ sở hữu", "Chủ sở hữu có quyền đặc biệt: chủ sở hữu ẩn, lấy lại quyền sở hữu hoặc thay đổi số dư."],
            "code": ["Mã mở và không thể bị sửa ngầm", "Mã chưa được xác minh, hoặc chủ sở hữu có thể sửa sau này."],
            "limits": ["Không có tạm dừng, danh sách đen hay giới hạn giao dịch", "Chủ sở hữu có thể dừng giao dịch, chặn ví hoặc đổi quy tắc giao dịch."],
            "lp": ["Thanh khoản được khóa hoặc đốt", "Phần lớn thanh khoản không bị khóa ({v} được khóa). Người tạo có thể rút ra."],
            "volume": ["Khối lượng giao dịch hợp lý", "Khối lượng rất thấp so với vốn hóa. Một giao dịch cũng có thể làm giá biến động."],
            "markets": ["Giao dịch trên nhiều hơn một thị trường", "Token giao dịch trên rất ít thị trường."],
            "age": ["Không phải token mới tinh", "Token mới chỉ {v} ngày tuổi."],
            "top": ["Nguồn cung không nằm trong tay vài ví", "10 ví lớn nhất nắm {v} nguồn cung."],
            "creator": ["Người tạo và chủ sở hữu nắm phần nhỏ", "Người tạo hoặc chủ sở hữu nắm phần lớn nguồn cung ({v})."],
            "holders": ["Đủ số người nắm giữ", "Rất ít người nắm giữ ({v})."],
        },
        "manual": {
            "m_site": "Tự mở trang web chính thức của dự án và so sánh địa chỉ hợp đồng với địa chỉ bạn vừa kiểm tra.",
            "m_team": "Đội ngũ công khai và dự án giải thích bằng lời đơn giản việc họ làm.",
            "m_unlock": "Kiểm tra xem có đợt mở khóa token lớn sắp tới không. Nguồn cung mới có thể kéo giá xuống.",
            "m_limit": "Đặt số tiền tối đa bạn có thể mất hoàn toàn và đừng vượt quá.",
            "m_test": "Gửi thử một khoản nhỏ trước. Kiểm tra mạng và địa chỉ.",
        },
        "how_title": "Các kiểm tra hoạt động thế nào",
        "how": [
            "DỪNG: kết quả quét cho biết không thể bán, hoặc thuế mua hay bán từ 50% trở lên.",
            "Cảnh báo: thuế trên 10%, có thể tạo thêm token, quyền ẩn hoặc nguy hiểm của chủ sở hữu, mã chưa xác minh hoặc có thể sửa, chức năng tạm dừng hoặc danh sách đen, dưới một nửa thanh khoản được khóa, khối lượng rất nhỏ, dưới 2 thị trường, dưới 30 ngày tuổi, 10 ví lớn nhất nắm hơn một nửa, người tạo hoặc chủ sở hữu nắm trên 10%, dưới 100 người nắm giữ.",
            "Không có dữ liệu: nguồn không cung cấp thông tin này. Điều đó không giống với OK.",
        ],
        "full_cta": "Đọc hướng dẫn checklist đầy đủ",
    },
    "sw": {
        "label_net": "Mtandao", "label_addr": "Anwani ya mkataba wa tokeni", "ph_addr": "0x...",
        "btn": "Kagua tokeni", "btn_copy": "Nakili kiungo cha matokeo haya", "copied": "Kiungo kimenakiliwa",
        "privacy": "Kivinjari chako kinaomba data moja kwa moja kutoka GoPlus na CoinGecko. Hatuoni wala kuhifadhi unachoandika.",
        "scope": "Inafanya kazi kwa mitandao ya EVM (Ethereum, BNB Chain, Polygon, Arbitrum, Base, Optimism, Avalanche), pamoja na Solana na TRON. Kwa Solana na TRON data ni chache, kwa hiyo mistari mingi inaonyesha \"Hakuna data\".",
        "loading": "Inakagua... inaweza kuchukua sekunde chache.",
        "err_addr": "Anwani si sahihi kwa mtandao huu. EVM: 0x na herufi 42. TRON: huanza na T, herufi 34. Solana: herufi na namba 32 hadi 44.",
        "err_api": "Imeshindwa kufikia vyanzo vya data. Jaribu tena baadaye, au fungua viungo vilivyo chini.",
        "err_rate": "Chanzo cha data cha bure kina shughuli nyingi. Subiri dakika moja ujaribu tena.",
        "no_gp": "GoPlus haina data ya tokeni hii. Ukaguzi wa usalama ulio chini haujulikani.",
        "token_title": "Tokeni imepatikana", "not_found": "Tokeni haipo kwenye CoinGecko",
        "cap": "Thamani ya soko", "vol": "Kiasi cha saa 24", "site": "Tovuti kwenye CoinGecko",
        "open_cg": "Fungua kwenye CoinGecko", "open_gp": "Fungua kwenye GoPlus",
        "st": {"ok": "SAWA", "flag": "Onyo", "stop": "SIMAMA", "unknown": "Hakuna data", "manual": "Kagua mwenyewe"},
        "sum_title": "Matokeo",
        "sum_stop": "Vipengele {n} vya SIMAMA vimepatikana. Usinunue wala kuidhinisha chochote.",
        "sum_flag": "Maonyo {n} yamepatikana. Soma kila moja kabla ya kuendelea.",
        "sum_ok": "Ukaguzi huu wa kiotomatiki haukupata dalili za hatari.",
        "sum_note": "Hii si hakikisho. Ulaghai mpya hutengenezwa kupita ukaguzi. Vipengele vya \"Kagua mwenyewe\" vinahitaji kazi yako.",
        "steps": ["Hatua ya 1. Je, ni tokeni halisi?", "Hatua ya 2. Ukaguzi wa usalama", "Hatua ya 3. Data ya soko", "Hatua ya 4. Wamiliki na mradi", "Hatua ya 5. Kabla ya kutumia pesa"],
        "rules": {
            "cg": ["Imeorodheshwa kwenye CoinGecko", "Haipo kwenye CoinGecko. Tokeni mpya au zisizojulikana zina hatari kubwa zaidi. Hakikisha hii ni anwani rasmi."],
            "honeypot": ["Inaweza kuuzwa (si honeypot)", "Ukaguzi unasema tokeni hii inaweza kushindikana kuuzwa. Usinunue."],
            "sell_tax": ["Kodi ya kuuza ni ndogo", "Kodi kubwa ya kuuza ({v}). Sehemu kubwa ya pesa zako huchukuliwa unapouza."],
            "buy_tax": ["Kodi ya kununua ni ndogo", "Kodi kubwa ya kununua ({v}). Sehemu kubwa ya pesa zako huchukuliwa unaponunua."],
            "mint": ["Mmiliki hawezi kutengeneza tokeni mpya", "Mmiliki anaweza kutengeneza tokeni mpya. Hii inaweza kushusha bei."],
            "owner": ["Hakuna mamlaka yaliyofichwa au hatari ya mmiliki", "Mmiliki ana mamlaka maalum: mmiliki aliyefichwa, kurudisha umiliki, au kubadilisha salio."],
            "code": ["Msimbo uko wazi na hauwezi kubadilishwa kwa siri", "Msimbo haujathibitishwa, au mmiliki anaweza kuubadilisha baadaye."],
            "limits": ["Hakuna kusimamisha, orodha nyeusi wala vikomo vya biashara", "Mmiliki anaweza kusimamisha biashara, kuzuia pochi au kubadilisha sheria."],
            "lp": ["Ukwasi umefungwa au umeteketezwa", "Sehemu kubwa ya ukwasi haijafungwa ({v} imefungwa). Waundaji wanaweza kuutoa."],
            "volume": ["Kiasi cha biashara ni cha busara", "Kiasi kidogo sana ukilinganisha na thamani ya soko. Biashara moja inaweza kusogeza bei."],
            "markets": ["Inauzwa kwenye soko zaidi ya moja", "Tokeni inauzwa kwenye masoko machache sana."],
            "age": ["Si tokeni mpya kabisa", "Tokeni ina siku {v} tu."],
            "top": ["Ugavi haushikiliwi na pochi chache", "Pochi 10 kubwa zaidi zinashikilia {v} ya ugavi."],
            "creator": ["Muundaji na mmiliki wanashikilia sehemu ndogo", "Muundaji au mmiliki anashikilia sehemu kubwa ya ugavi ({v})."],
            "holders": ["Wamiliki wa kutosha", "Wamiliki wachache sana ({v})."],
        },
        "manual": {
            "m_site": "Fungua mwenyewe tovuti rasmi ya mradi na linganisha anwani yake ya mkataba na uliyoikagua.",
            "m_team": "Timu iko wazi kwa umma na mradi unaeleza kwa maneno rahisi unachofanya.",
            "m_unlock": "Angalia kama kufunguliwa kwa tokeni nyingi kunakuja hivi karibuni. Ugavi mpya unaweza kushusha bei.",
            "m_limit": "Amua kiasi cha juu unachoweza kupoteza kabisa, na usizidishe.",
            "m_test": "Tuma kiasi kidogo cha majaribio kwanza. Kagua mtandao na anwani.",
        },
        "how_title": "Ukaguzi unavyofanya kazi",
        "how": [
            "SIMAMA: ukaguzi unasema huwezi kuuza, au kodi ya kununua au kuuza ya 50% au zaidi.",
            "Onyo: kodi zaidi ya 10%, tokeni mpya zinaweza kutengenezwa, mamlaka yaliyofichwa au hatari ya mmiliki, msimbo haujathibitishwa au unaweza kubadilishwa, kazi za kusimamisha au orodha nyeusi, chini ya nusu ya ukwasi imefungwa, kiasi kidogo sana, masoko chini ya 2, umri chini ya siku 30, pochi 10 kubwa zinashikilia zaidi ya nusu, muundaji au mmiliki anashikilia zaidi ya 10%, wamiliki chini ya 100.",
            "Hakuna data: chanzo hakikutoa taarifa hii. Hiyo si sawa na SAWA.",
        ],
        "full_cta": "Soma mwongozo kamili wa orodha ya kukagua",
    },
    "simple": {
        "label_net": "Network", "label_addr": "Token contract address", "ph_addr": "0x...",
        "btn": "Check token", "btn_copy": "Copy link to this result", "copied": "Link copied",
        "privacy": "Your browser asks GoPlus and CoinGecko directly. We do not see or keep what you type.",
        "scope": "This works for EVM networks (Ethereum, BNB Chain, Polygon, Arbitrum, Base, Optimism, Avalanche), and for Solana and TRON. For Solana and TRON the data is thinner, so more items show \"No data\".",
        "loading": "Checking... this can take a few seconds.",
        "err_addr": "This address does not fit this network. EVM: 0x and 42 characters. TRON: starts with T, 34 characters. Solana: 32 to 44 letters and numbers.",
        "err_api": "We could not reach the data sources. Try again later, or open the links below.",
        "err_rate": "The free data source is busy. Wait one minute and try again.",
        "no_gp": "GoPlus has no data for this token. The security checks below are unknown.",
        "token_title": "Token found", "not_found": "Token not found on CoinGecko",
        "cap": "Market cap", "vol": "24-hour volume", "site": "Website on CoinGecko",
        "open_cg": "Open on CoinGecko", "open_gp": "Open on GoPlus",
        "st": {"ok": "OK", "flag": "Warning", "stop": "STOP", "unknown": "No data", "manual": "You check"},
        "sum_title": "Result",
        "sum_stop": "We found {n} STOP item(s). Do not buy. Do not approve anything.",
        "sum_flag": "We found {n} warning(s). Read each one before you go on.",
        "sum_ok": "These automatic checks found no red flags.",
        "sum_note": "This is not a promise. New scams are made to pass checks. The \"You check\" items need work from you.",
        "steps": ["Step 1. Is it the real token?", "Step 2. Security scan", "Step 3. Market data", "Step 4. Holders and the project", "Step 5. Before you spend"],
        "rules": {
            "cg": ["Listed on CoinGecko", "Not listed on CoinGecko. New or unknown tokens are much riskier. Make sure this is the official contract address."],
            "honeypot": ["Can be sold (not a honeypot)", "The scan says you may not be able to sell this token. Do not buy."],
            "sell_tax": ["Sell tax is low", "The sell tax is high ({v}). A big part of your money is taken when you sell."],
            "buy_tax": ["Buy tax is low", "The buy tax is high ({v}). A big part of your money is taken when you buy."],
            "mint": ["Owner cannot make new tokens", "The owner can make new tokens. This can push the price down."],
            "owner": ["No hidden or dangerous owner powers", "The owner has special powers: a hidden owner, taking back ownership, or changing balances."],
            "code": ["Code is open and cannot be changed in secret", "The code is not verified, or the owner can change it later."],
            "limits": ["No pause, blacklist or trade limits", "The owner can stop trading, block wallets or change the trade rules."],
            "lp": ["Liquidity is locked or burned", "Most of the liquidity is not locked ({v} locked). The creators may be able to take it out."],
            "volume": ["Trading volume is fine", "The trading volume is very low for the market cap. One trade can move the price."],
            "markets": ["Trades on more than one market", "The token trades on very few markets."],
            "age": ["Not a brand-new token", "The token is only {v} days old."],
            "top": ["A few wallets do not hold most of the supply", "The 10 biggest wallets hold {v} of the supply."],
            "creator": ["Creator and owner hold a small share", "The creator or the owner holds a big share of the supply ({v})."],
            "holders": ["Enough holders", "Very few holders ({v})."],
        },
        "manual": {
            "m_site": "Open the official website of the project yourself. Compare its contract address with the one you checked.",
            "m_team": "The team is public. The project says in simple words what it does.",
            "m_unlock": "Check if big token unlocks are coming soon. New supply can push the price down.",
            "m_limit": "Decide the most money you can lose completely. Do not go above it.",
            "m_test": "Send a small test first. Check the network and the address.",
        },
        "how_title": "How the checks work",
        "how": [
            "STOP: the scan says you cannot sell, or a buy or sell tax of 50% or more.",
            "Warning: tax above 10%, new tokens can be made, hidden or dangerous owner powers, code not verified or open to change, pause or blacklist functions, less than half of the liquidity locked, very small volume, fewer than 2 markets, younger than 30 days, top 10 wallets hold more than half, creator or owner holds more than 10%, fewer than 100 holders.",
            "No data: the source did not give this information. This is not the same as OK.",
        ],
        "full_cta": "Read the full checklist guide",
    },
}

# Карточка раздела на главной и в меню (SEC[lang]["check"] = [название, описание, h1, лид], "check_count").
CHECK_SEC = {
    "en": (["Token check", "Paste a token contract and get the checklist filled in from free data.", "Check a token", "Paste a contract address and see which steps of the checklist pass, which warn and which you must check yourself."], "Free, in your browser"),
    "fr": (["Vérifier un token", "Collez un contrat de token et obtenez la checklist remplie avec des données gratuites.", "Vérifier un token", "Collez une adresse de contrat et voyez quelles étapes de la checklist passent, lesquelles alertent et lesquelles vous devez vérifier vous-même."], "Gratuit, dans votre navigateur"),
    "id": (["Cek token", "Tempel kontrak token dan dapatkan checklist yang terisi dari data gratis.", "Periksa token", "Tempel alamat kontrak dan lihat langkah checklist mana yang lolos, mana yang memberi peringatan, dan mana yang harus Anda periksa sendiri."], "Gratis, di peramban Anda"),
    "vi": (["Kiểm tra token", "Dán hợp đồng token và nhận checklist được điền từ dữ liệu miễn phí.", "Kiểm tra token", "Dán địa chỉ hợp đồng và xem bước nào của checklist đạt, bước nào cảnh báo, bước nào bạn phải tự kiểm tra."], "Miễn phí, ngay trên trình duyệt"),
    "sw": (["Kagua tokeni", "Bandika mkataba wa tokeni upate orodha iliyojazwa kwa data ya bure.", "Kagua tokeni", "Bandika anwani ya mkataba uone hatua za orodha zipi zimepita, zipi zina onyo, na zipi lazima ukague mwenyewe."], "Bure, kwenye kivinjari chako"),
    "simple": (["Token check", "Paste a token contract. Get the checklist filled in from free data.", "Check a token", "Paste a contract address. See which steps pass, which give a warning, and which ones you must check yourself."], "Free, in your browser"),
}

# Скрипт страницы. __T__ заменяется JSON с текстами нужного языка, __BASE__ путём к корню сайта.
CHECK_JS = r"""
(function () {
  var T = __T__;
  var NETS = {
    "1": {cg: "ethereum", name: "Ethereum"}, "56": {cg: "binance-smart-chain", name: "BNB Chain"},
    "137": {cg: "polygon-pos", name: "Polygon"}, "42161": {cg: "arbitrum-one", name: "Arbitrum"},
    "8453": {cg: "base", name: "Base"}, "10": {cg: "optimistic-ethereum", name: "Optimism"},
    "43114": {cg: "avalanche", name: "Avalanche"},
    "solana": {cg: "solana", name: "Solana", kind: "sol"}, "tron": {cg: "tron", name: "TRON", kind: "tron"}
  };
  function kindOf(chain) { return (NETS[chain] && NETS[chain].kind) || "evm"; }
  function validAddr(chain, a) {
    var k = kindOf(chain);
    if (k === "sol") return /^[1-9A-HJ-NP-Za-km-z]{32,44}$/.test(a);
    if (k === "tron") return /^T[1-9A-HJ-NP-Za-km-z]{33}$/.test(a);
    return /^0x[0-9a-fA-F]{40}$/.test(a);
  }
  function pick(result, a, chain) {
    if (!result || typeof result !== "object") return null;
    var key = kindOf(chain) === "evm" ? a.toLowerCase() : a, g = result[key];
    if (!g) { Object.keys(result).forEach(function (k) { if (!g && k.toLowerCase() === a.toLowerCase()) g = result[k]; }); }
    return g && typeof g === "object" && Object.keys(g).length ? g : null;
  }
  function st01(x) { if (x && typeof x === "object") x = x.status; return flag01(x == null ? null : String(x)); }
  var DEAD = ["0x000000000000000000000000000000000000dead", "0x0000000000000000000000000000000000000000"];
  var form = document.getElementById("ck-form"), net = document.getElementById("ck-net"),
      addr = document.getElementById("ck-addr"), out = document.getElementById("ck-out"),
      err = document.getElementById("ck-err"), btn = document.getElementById("ck-btn");
  Object.keys(NETS).forEach(function (id) {
    var o = document.createElement("option"); o.value = id; o.textContent = NETS[id].name; net.appendChild(o);
  });

  function el(tag, cls, text) {
    var e = document.createElement(tag); if (cls) e.className = cls; if (text != null) e.textContent = text; return e;
  }
  function num(x) { var n = parseFloat(x); return isFinite(n) ? n : null; }
  function flag01(x) { return x === "1" ? true : (x === "0" ? false : null); }
  function pct(x) { return (x * 100).toFixed(x < 0.1 ? 1 : 0) + "%"; }
  function money(n) {
    if (n == null) return "-";
    if (n >= 1e9) return "$" + (n / 1e9).toFixed(2) + "B";
    if (n >= 1e6) return "$" + (n / 1e6).toFixed(2) + "M";
    if (n >= 1e3) return "$" + (n / 1e3).toFixed(1) + "K";
    return "$" + n.toFixed(0);
  }
  function getJson(url) {
    var ctl = new AbortController(), timer = setTimeout(function () { ctl.abort(); }, 15000);
    return fetch(url, {signal: ctl.signal}).then(function (r) {
      clearTimeout(timer);
      return r.json().catch(function () { return null; }).then(function (d) { return {status: r.status, data: d}; });
    }).catch(function () { clearTimeout(timer); return {status: 0, data: null}; });
  }

  // Solana: другие поля GoPlus, многие проверки недоступны (остаются "нет данных")
  function evaluateSol(g, cg, rows, add) {
    var nt = flag01(g.none_transferable == null ? g.non_transferable : g.none_transferable);
    add(1, "honeypot", nt === null ? "unknown" : (nt ? "stop" : "ok"));
    ["sell_tax", "buy_tax", "code", "lp"].forEach(function (id) { add(1, id, "unknown"); });
    var tf = g.transfer_fee, hasFee = tf && typeof tf === "object" && Object.keys(tf).length > 0;
    var mint = st01(g.mintable);
    add(1, "mint", mint === null ? "unknown" : (mint ? "flag" : "ok"));
    var bm = st01(g.balance_mutable_authority);
    add(1, "owner", bm === null ? "unknown" : (bm ? "flag" : "ok"));
    var fr = st01(g.freezable), cl = st01(g.closable);
    var lim = [fr, cl, hasFee ? true : null, (Array.isArray(g.transfer_hook) && g.transfer_hook.length) ? true : null];
    add(1, "limits", fr === null && cl === null && !hasFee ? "unknown" : (lim.some(function (x) { return x; }) ? "flag" : "ok"));
  }

  function evaluate(g, cg, kind) {
    var rows = [];
    function add(step, id, st, v) { rows.push({step: step, id: id, st: st, v: v}); }
    // Шаг 1
    add(0, "cg", cg ? "ok" : "flag");
    // Шаг 2: безопасность (GoPlus)
    if (!g) {
      ["honeypot", "sell_tax", "buy_tax", "mint", "owner", "code", "limits", "lp"].forEach(function (id) { add(1, id, "unknown"); });
    } else if (kind === "sol") {
      evaluateSol(g, cg, rows, add);
    } else {
      var hp = flag01(g.is_honeypot), cantSell = flag01(g.cannot_sell_all), cantBuy = flag01(g.cannot_buy);
      add(1, "honeypot", hp === null && cantSell === null && cantBuy === null ? "unknown" : (hp || cantBuy ? "stop" : (cantSell ? "flag" : "ok")));
      [["sell_tax", g.sell_tax], ["buy_tax", g.buy_tax]].forEach(function (p) {
        var t = num(p[1]);
        add(1, p[0], t === null ? "unknown" : (t >= 0.5 ? "stop" : (t > 0.1 ? "flag" : "ok")), t === null ? "" : pct(t));
      });
      var mint = flag01(g.is_mintable);
      add(1, "mint", mint === null ? "unknown" : (mint ? "flag" : "ok"));
      var ow = [flag01(g.hidden_owner), flag01(g.can_take_back_ownership), flag01(g.owner_change_balance)];
      add(1, "owner", ow.every(function (x) { return x === null; }) ? "unknown" : (ow.some(function (x) { return x; }) ? "flag" : "ok"));
      var os = flag01(g.is_open_source), px = flag01(g.is_proxy);
      add(1, "code", os === null && px === null ? "unknown" : ((os === false || px) ? "flag" : "ok"));
      var lim = [flag01(g.transfer_pausable), flag01(g.is_blacklisted), flag01(g.trading_cooldown), flag01(g.slippage_modifiable)];
      add(1, "limits", lim.every(function (x) { return x === null; }) ? "unknown" : (lim.some(function (x) { return x; }) ? "flag" : "ok"));
      var lps = Array.isArray(g.lp_holders) ? g.lp_holders : [];
      if (!lps.length) add(1, "lp", "unknown");
      else {
        var locked = 0;
        lps.forEach(function (h) {
          var a = String(h.address || "").toLowerCase();
          if (h.is_locked === 1 || h.is_locked === "1" || DEAD.indexOf(a) >= 0) locked += num(h.percent) || 0;
        });
        add(1, "lp", locked < 0.5 ? "flag" : "ok", pct(Math.min(locked, 1)));
      }
    }
    // Шаг 3: рынок (CoinGecko)
    var md = cg && cg.market_data;
    var mc = md && md.market_cap && num(md.market_cap.usd), vol = md && md.total_volume && num(md.total_volume.usd);
    add(2, "volume", (mc && vol !== null) ? (vol / mc < 0.001 ? "flag" : "ok") : "unknown");
    add(2, "markets", cg && Array.isArray(cg.tickers) ? (cg.tickers.length < 2 ? "flag" : "ok") : "unknown");
    var days = null;
    if (cg && cg.genesis_date) { var t0 = Date.parse(cg.genesis_date); if (!isNaN(t0)) days = Math.floor((Date.now() - t0) / 864e5); }
    add(2, "age", days === null ? "unknown" : (days < 30 ? "flag" : "ok"), String(days));
    // Шаг 4: держатели
    if (!g) { ["top", "creator", "holders"].forEach(function (id) { add(3, id, "unknown"); }); }
    else {
      var hs = Array.isArray(g.holders) ? g.holders : [];
      if (!hs.length) add(3, "top", "unknown");
      else {
        var top = 0;
        hs.slice(0, 10).forEach(function (h) {
          var a = String(h.address || h.account || "").toLowerCase();
          if (h.is_locked === 1 || h.is_locked === "1" || DEAD.indexOf(a) >= 0) return;
          var pc = num(h.percent) || 0;
          top += (kind === "sol" && pc > 1) ? pc / 100 : pc;
        });
        add(3, "top", top > 0.5 ? "flag" : "ok", pct(Math.min(top, 1)));
      }
      var cr = kind === "sol" ? null : num(g.creator_percent), own = kind === "sol" ? null : num(g.owner_percent), big = Math.max(cr || 0, own || 0);
      add(3, "creator", cr === null && own === null ? "unknown" : (big > 0.1 ? "flag" : "ok"), pct(big));
      var hc = parseInt(g.holder_count, 10);
      add(3, "holders", isNaN(hc) ? "unknown" : (hc < 100 ? "flag" : "ok"), isNaN(hc) ? "" : String(hc));
    }
    return rows;
  }

  function render(rows, g, cg, a, chain, hadGp, notFound) {
    out.textContent = "";
    var stops = rows.filter(function (r) { return r.st === "stop"; }).length,
        flags = rows.filter(function (r) { return r.st === "flag"; }).length;
    var sum = el("section", "ck-sum " + (stops ? "stop" : (flags ? "flag" : "ok")));
    sum.appendChild(el("h2", null, T.sum_title));
    sum.appendChild(el("p", "ck-big", stops ? T.sum_stop.replace("{n}", stops) : (flags ? T.sum_flag.replace("{n}", flags) : (g ? T.sum_ok : T.no_gp))));
    sum.appendChild(el("p", null, T.sum_note));
    out.appendChild(sum);

    var card = el("section", "ck-token");
    card.appendChild(el("h2", null, cg ? T.token_title : T.not_found));
    if (cg) {
      card.appendChild(el("p", "ck-name", (cg.name || "?") + " (" + String(cg.symbol || "?").toUpperCase() + ")"));
      var md = cg.market_data || {};
      var info = el("p", null, T.cap + ": " + money(md.market_cap && num(md.market_cap.usd)) + "  |  " + T.vol + ": " + money(md.total_volume && num(md.total_volume.usd)));
      card.appendChild(info);
      var hp = cg.links && cg.links.homepage && cg.links.homepage[0];
      if (hp) card.appendChild(el("p", null, T.site + ": " + String(hp).slice(0, 80)));
    }
    var links = el("p", "ck-links");
    if (cg && cg.id) {
      var l1 = el("a", null, T.open_cg); l1.href = "https://www.coingecko.com/en/coins/" + encodeURIComponent(cg.id);
      l1.rel = "noopener nofollow"; links.appendChild(l1);
    }
    var l2 = el("a", null, T.open_gp); l2.href = "https://gopluslabs.io/token-security/" + chain + "/" + a;
    l2.rel = "noopener nofollow"; links.appendChild(l2);
    card.appendChild(links);
    if (!hadGp) card.appendChild(el("p", "ck-note", T.no_gp));
    out.appendChild(card);

    T.steps.forEach(function (title, i) {
      var sec = el("section", "ck-step"); sec.appendChild(el("h2", null, title));
      var ul = el("ul", "ck-list");
      rows.filter(function (r) { return r.step === i; }).forEach(function (r) {
        var rule = T.rules[r.id], li = el("li", "ck-row " + r.st), badge = el("span", "ck-badge", T.st[r.st]);
        var body = el("span", "ck-text");
        if (r.st === "flag" || r.st === "stop") body.appendChild(el("strong", null, rule[1].replace("{v}", r.v || "")));
        else body.appendChild(el("strong", null, rule[0]));
        li.appendChild(badge); li.appendChild(body); ul.appendChild(li);
      });
      var manual = {0: ["m_site"], 3: ["m_team", "m_unlock"], 4: ["m_limit", "m_test"]}[i] || [];
      manual.forEach(function (k) {
        var li = el("li", "ck-row manual"); li.appendChild(el("span", "ck-badge", T.st.manual));
        var body = el("span", "ck-text"); body.appendChild(el("strong", null, T.manual[k])); li.appendChild(body); ul.appendChild(li);
      });
      sec.appendChild(ul); out.appendChild(sec);
    });

    var share = el("button", "btn ck-copy", T.btn_copy); share.type = "button";
    share.addEventListener("click", function () {
      var done = function () { share.textContent = T.copied; };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(location.href).then(done, function () {});
      else done();
    });
    out.appendChild(share);
    out.hidden = false;
  }

  function run(chain, a, pushState) {
    err.hidden = true; out.hidden = true;
    if (!NETS[chain] || !validAddr(chain, a)) { err.textContent = T.err_addr; err.hidden = false; return; }
    btn.disabled = true; err.textContent = T.loading; err.hidden = false;
    if (pushState && window.history && history.replaceState) {
      try { history.replaceState(null, "", "?n=" + chain + "&a=" + a); } catch (e) {}
    }
    var kind = kindOf(chain), low = kind === "evm" ? a.toLowerCase() : a;
    var gpUrl = kind === "sol" ? "https://api.gopluslabs.io/api/v1/solana/token_security?contract_addresses=" + encodeURIComponent(low)
      : "https://api.gopluslabs.io/api/v1/token_security/" + (kind === "tron" ? "tron" : chain) + "?contract_addresses=" + encodeURIComponent(low);
    Promise.all([
      getJson(gpUrl),
      getJson("https://api.coingecko.com/api/v3/coins/" + NETS[chain].cg + "/contract/" + encodeURIComponent(low))
    ]).then(function (res) {
      btn.disabled = false;
      var gp = res[0], cgr = res[1];
      var g = pick(gp.data && gp.data.result, a, chain);
      var cg = cgr.status === 200 && cgr.data && cgr.data.id ? cgr.data : null;
      if (gp.status === 0 && cgr.status === 0) { err.textContent = T.err_api; err.hidden = false; return; }
      if (gp.status === 429 && cgr.status === 429) { err.textContent = T.err_rate; err.hidden = false; return; }
      err.hidden = true;
      render(evaluate(g, cg, kindOf(chain)), g, cg, a, chain, !!g, !cg);
    });
  }

  form.addEventListener("submit", function (ev) { ev.preventDefault(); run(net.value, addr.value.trim(), true); });
  var qs = new URLSearchParams(location.search);
  if (qs.get("a") && qs.get("n")) { net.value = qs.get("n"); addr.value = qs.get("a"); run(qs.get("n"), qs.get("a"), false); }
})();
"""
