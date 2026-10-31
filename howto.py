"""Короткие инструкции «как начать» для инструментов каталога (5 языков).

Формат: HOWTO[id инструмента]["lang"][язык] = {"steps": [...], "note": "..."}.
Их показывают и сайт (раскрывашка в карточке), и бот (кнопка «Как начать»).
Шаги описаны общими словами, без названий кнопок и меню, потому что интерфейс сервисов меняется.
Добавить инструкцию: новый ключ с id из catalog.json и тексты на всех 5 языках (5-6 шагов).
"""

HOWTO_UI = {
    "en": {"btn": "🧭 How to start", "title": "How to start with {tool}", "back": "◀️ Back to {tool}", "summary": "How to start (5 steps)"},
    "fr": {"btn": "🧭 Comment commencer", "title": "Comment commencer avec {tool}", "back": "◀️ Retour à {tool}", "summary": "Comment commencer (5 étapes)"},
    "id": {"btn": "🧭 Cara memulai", "title": "Cara memulai dengan {tool}", "back": "◀️ Kembali ke {tool}", "summary": "Cara memulai (5 langkah)"},
    "vi": {"btn": "🧭 Cách bắt đầu", "title": "Cách bắt đầu với {tool}", "back": "◀️ Quay lại {tool}", "summary": "Cách bắt đầu (5 bước)"},
    "sw": {"btn": "🧭 Jinsi ya kuanza", "title": "Jinsi ya kuanza na {tool}", "back": "◀️ Rudi kwa {tool}", "summary": "Jinsi ya kuanza (hatua 5)"},
}

HOWTO = {
    "coingecko": {
        "lang": {
            "en": {
                "steps": [
                    "Open the CoinGecko website and type the token's name or ticker in the search box.",
                    "Pick the result with the right name and symbol. Fake tokens copy names, so compare the contract address on the page with the one the project publishes on its own website.",
                    "Look at market cap, 24-hour trading volume and the number of markets. Very low volume, or one tiny market, means a single trade can move the price.",
                    "Use the official website and social links listed on the token page, not links sent to you in a chat.",
                    "Open the price chart with the longest range to see the whole history, and check which exchanges list the token.",
                ],
                "note": "CoinGecko shows data. It does not tell you whether a token is safe or will rise.",
            },
            "fr": {
                "steps": [
                    "Ouvrez le site de CoinGecko et saisissez le nom ou le symbole du token dans la recherche.",
                    "Choisissez le résultat avec le bon nom et le bon symbole. Les faux tokens copient les noms : comparez l'adresse du contrat sur la page avec celle que le projet publie sur son propre site.",
                    "Regardez la capitalisation, le volume d'échange sur 24 heures et le nombre de marchés. Un volume très faible, ou un seul petit marché, signifie qu'un seul échange peut faire bouger le prix.",
                    "Utilisez le site officiel et les réseaux sociaux indiqués sur la page du token, pas les liens reçus dans une conversation.",
                    "Ouvrez le graphique sur la période la plus longue pour voir tout l'historique, et vérifiez sur quelles plateformes le token est coté.",
                ],
                "note": "CoinGecko affiche des données. Il ne dit pas si un token est sûr ni s'il va monter.",
            },
            "id": {
                "steps": [
                    "Buka situs CoinGecko dan ketik nama atau ticker token di kotak pencarian.",
                    "Pilih hasil dengan nama dan simbol yang benar. Token palsu meniru nama, jadi bandingkan alamat kontrak di halaman itu dengan yang diumumkan proyek di situs resminya.",
                    "Lihat kapitalisasi pasar, volume perdagangan 24 jam, dan jumlah pasar. Volume sangat kecil, atau hanya satu pasar kecil, berarti satu transaksi bisa menggerakkan harga.",
                    "Gunakan situs resmi dan tautan media sosial yang tercantum di halaman token, bukan tautan yang dikirim lewat obrolan.",
                    "Buka grafik harga dengan rentang terpanjang untuk melihat seluruh riwayat, dan cek bursa mana yang mencatatkan token itu.",
                ],
                "note": "CoinGecko menampilkan data. Ia tidak menyatakan apakah token aman atau akan naik.",
            },
            "vi": {
                "steps": [
                    "Mở trang web CoinGecko và nhập tên hoặc mã của token vào ô tìm kiếm.",
                    "Chọn kết quả có đúng tên và ký hiệu. Token giả thường sao chép tên, vì vậy hãy so sánh địa chỉ hợp đồng trên trang với địa chỉ mà dự án công bố trên trang web chính thức của mình.",
                    "Xem vốn hóa thị trường, khối lượng giao dịch 24 giờ và số lượng thị trường. Khối lượng rất thấp, hoặc chỉ có một thị trường nhỏ, nghĩa là một giao dịch cũng có thể làm giá biến động.",
                    "Dùng trang web chính thức và liên kết mạng xã hội ghi trên trang token, không dùng liên kết được gửi qua tin nhắn.",
                    "Mở biểu đồ giá với khoảng thời gian dài nhất để xem toàn bộ lịch sử và kiểm tra những sàn nào niêm yết token.",
                ],
                "note": "CoinGecko chỉ hiển thị dữ liệu. Nó không cho biết token có an toàn hay sẽ tăng giá hay không.",
            },
            "sw": {
                "steps": [
                    "Fungua tovuti ya CoinGecko na andika jina au alama ya tokeni kwenye kisanduku cha kutafuta.",
                    "Chagua matokeo yenye jina na alama sahihi. Tokeni bandia hunakili majina, kwa hiyo linganisha anwani ya mkataba kwenye ukurasa na ile ambayo mradi huchapisha kwenye tovuti yake rasmi.",
                    "Angalia thamani ya soko, kiasi cha biashara cha saa 24 na idadi ya masoko. Kiasi kidogo sana, au soko moja dogo, humaanisha biashara moja inaweza kusogeza bei.",
                    "Tumia tovuti rasmi na viungo vya mitandao ya kijamii vilivyo kwenye ukurasa wa tokeni, si viungo ulivyotumiwa kwenye gumzo.",
                    "Fungua chati ya bei yenye muda mrefu zaidi kuona historia nzima, na angalia ni mabadilishano gani yanayoorodhesha tokeni hiyo.",
                ],
                "note": "CoinGecko huonyesha data. Haikuambii kama tokeni ni salama au itapanda.",
            },
        }
    },
    "goplus": {
        "lang": {
            "en": {
                "steps": [
                    "Open the GoPlus website and find its token security checker.",
                    "Choose the blockchain network the token lives on, such as Ethereum, BNB Chain, Solana or TRON.",
                    "Paste the contract address. Copy it from the project's official website or from CoinGecko, not from a chat message, then run the check.",
                    "Read the warnings first: honeypot (you can buy but not sell), very high buy or sell tax, an owner who can mint new tokens or change the rules, and hidden owners.",
                    "If the report shows several risks, do not buy or approve anything. If it looks clean, remember that is only one input.",
                ],
                "note": "A clean scan is not a guarantee. New scams are built to pass checks, and the tool cannot see the team's plans.",
            },
            "fr": {
                "steps": [
                    "Ouvrez le site de GoPlus et trouvez son analyseur de sécurité de token.",
                    "Choisissez le réseau blockchain du token, par exemple Ethereum, BNB Chain, Solana ou TRON.",
                    "Collez l'adresse du contrat. Copiez-la depuis le site officiel du projet ou depuis CoinGecko, pas depuis un message, puis lancez l'analyse.",
                    "Lisez d'abord les alertes : honeypot (on peut acheter mais pas vendre), taxe d'achat ou de vente très élevée, propriétaire qui peut créer des tokens ou changer les règles, propriétaires cachés.",
                    "Si le rapport montre plusieurs risques, n'achetez et n'autorisez rien. S'il semble propre, rappelez-vous que ce n'est qu'un élément parmi d'autres.",
                ],
                "note": "Une analyse sans alerte n'est pas une garantie. Les nouvelles arnaques sont conçues pour passer les contrôles, et l'outil ne voit pas les plans de l'équipe.",
            },
            "id": {
                "steps": [
                    "Buka situs GoPlus dan cari pemeriksa keamanan token.",
                    "Pilih jaringan blockchain tempat token berada, misalnya Ethereum, BNB Chain, Solana, atau TRON.",
                    "Tempel alamat kontrak. Salin dari situs resmi proyek atau dari CoinGecko, bukan dari pesan obrolan, lalu jalankan pemeriksaan.",
                    "Baca peringatan lebih dulu: honeypot (bisa beli tetapi tidak bisa jual), pajak beli atau jual sangat tinggi, pemilik yang bisa mencetak token baru atau mengubah aturan, dan pemilik tersembunyi.",
                    "Jika laporan menunjukkan beberapa risiko, jangan membeli atau memberi izin apa pun. Jika tampak bersih, ingat bahwa itu hanya satu bahan pertimbangan.",
                ],
                "note": "Hasil bersih bukan jaminan. Penipuan baru dibuat untuk lolos pemeriksaan, dan alat ini tidak bisa melihat rencana tim.",
            },
            "vi": {
                "steps": [
                    "Mở trang web GoPlus và tìm công cụ kiểm tra bảo mật token.",
                    "Chọn mạng blockchain mà token đang chạy, ví dụ Ethereum, BNB Chain, Solana hoặc TRON.",
                    "Dán địa chỉ hợp đồng. Hãy sao chép từ trang web chính thức của dự án hoặc từ CoinGecko, không lấy từ tin nhắn, rồi chạy kiểm tra.",
                    "Đọc cảnh báo trước: honeypot (mua được nhưng không bán được), thuế mua hoặc bán rất cao, chủ sở hữu có thể tạo thêm token hoặc đổi quy tắc, và chủ sở hữu ẩn.",
                    "Nếu báo cáo cho thấy nhiều rủi ro, đừng mua hay cấp quyền gì cả. Nếu trông sạch, hãy nhớ đó chỉ là một yếu tố tham khảo.",
                ],
                "note": "Kết quả sạch không phải là đảm bảo. Các chiêu lừa mới được tạo ra để vượt qua kiểm tra, và công cụ không thấy được kế hoạch của đội ngũ.",
            },
            "sw": {
                "steps": [
                    "Fungua tovuti ya GoPlus na utafute kikagua usalama wa tokeni.",
                    "Chagua mtandao wa blockchain ambao tokeni ipo, kama Ethereum, BNB Chain, Solana au TRON.",
                    "Bandika anwani ya mkataba. Inakili kutoka tovuti rasmi ya mradi au CoinGecko, si kutoka ujumbe wa gumzo, kisha endesha ukaguzi.",
                    "Soma maonyo kwanza: honeypot (unaweza kununua lakini huwezi kuuza), kodi kubwa sana ya kununua au kuuza, mmiliki anayeweza kutengeneza tokeni mpya au kubadilisha sheria, na wamiliki waliofichwa.",
                    "Ripoti ikionyesha hatari kadhaa, usinunue wala kuidhinisha kitu chochote. Ikionekana safi, kumbuka hiyo ni kipengele kimoja tu.",
                ],
                "note": "Matokeo safi si hakikisho. Ulaghai mpya hutengenezwa kupita ukaguzi, na zana haiwezi kuona mipango ya timu.",
            },
        }
    },
}


# Остальные инструкции лежат в отдельных файлах, чтобы этот не разрастался.
from howto_more_a import HOWTO_A  # noqa: E402
from howto_more_b import HOWTO_B  # noqa: E402

HOWTO.update(HOWTO_A)
HOWTO.update(HOWTO_B)
