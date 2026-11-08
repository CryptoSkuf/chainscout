"""Red Flag Checker: человек присылает текст предложения или сообщения, бот ищет типичные признаки обмана.
Без сети и без ИИ: только правила. Не выносит вердикта «безопасно» и не повторяет присланный текст."""
import re
from typing import Optional

MAX_LEN = 3000

# id -> (уровень, регулярное выражение на 6 языках). Уровень "stop" — прекратить общение, "warn" — предупреждение.
RULES = {
    "seed": ("stop", r"seed\s*phrase|recovery\s*phrase|private\s*key|secret\s*phrase|12[\s-]*word|24[\s-]*word|phrase\s+secr[eè]te|cl[eé]\s+priv[eé]e|phrase\s+de\s+r[eé]cup|frasa\s+(pemulihan|rahasia)|kunci\s+(privat|pribadi)|c[uụ]m\s+t[uừ]\s+kh[oô]i\s+ph[uụ]c|kh[oó]a\s+ri[eê]ng|maneno\s+ya\s+siri|ufunguo\s+(wa\s+)?(binafsi|siri)"),
    "payfirst": ("stop", r"(pay|send|deposit|transfer)\b[^\n]{0,40}\b(to\s+(claim|receive|unlock|withdraw|release)|first)|(fee|tax|gas)\s+(to|before)\s+(claim|withdraw|unlock|receive)|double\s+your|multiply\s+your|(pay(er|ez)|envoy(er|ez)|envoie|d[eé]pos(er|ez))[^\n]{0,40}(pour\s+(r[eé]clamer|recevoir|d[eé]bloquer)|d'abord)|doubler\s+vos|(bayar|kirim)[^\n]{0,40}(untuk\s+(klaim|menerima|mencairkan)|dulu)|gandakan|(tr[aả]|g[uử]i|n[oộ]p)[^\n]{0,40}(tr[uư][oơ]́?c|[dđ][eể]\s+nh[aậ]n|[dđ][eể]\s+r[uú]t)|nh[aâ]n\s+[dđ][oô]i|(lipa|tuma)[^\n]{0,40}(kwanza|ili\s+(kupokea|kutoa))|mara\s+mbili"),
    "remote": ("stop", r"anydesk|team\s*viewer|rustdesk|screen\s*shar|remote\s+(access|control)|install\s+(this|the|our)\s+(app|apk|program)|\.apk\b|[tt][eé]l[eé]charger\s+(l'|cette\s+)?(app|application)|pasang\s+aplikasi|c[aà]i\s+[dđ][aặ]t\s+[uứ]ng\s+d[uụ]ng|sakinisha\s+programu"),
    "guarantee": ("warn", r"guarantee|risk[\s-]*free|no\s+risk|sure\s+profit|100\s*x|1000\s*x|garanti|sans\s+risque|b[eé]n[eé]fice\s+assur|pasti\s+(untung|profit)|tanpa\s+risiko|bebas\s+risiko|ch[aắ]c\s+ch[aắ]n\s+(l[aã]i|l[oờ]i)|kh[oô]ng\s+r[uủ]i\s+ro|uhakika|hakuna\s+hatari|bila\s+hatari|faida\s+ya\s+uhakika"),
    "daily": ("warn", r"\d+\s*%\s*(per|a|every|/|par|sehari|setiap|m[oỗ]i|kwa)?\s*(day|daily|week|jour|semaine|hari|minggu|ng[aà]y|tu[aầ]n|siku|wiki)|(daily|weekly|passive)\s+(income|profit|returns?)|revenu\s+passif|gain\s+quotidien|pendapatan\s+pasif|thu\s+nh[aậ]p\s+th[uụ]\s+[dđ][oộ]ng|mapato\s+ya\s+kila\s+siku"),
    "urgent": ("warn", r"last\s+chance|limited\s+(time|spots|slots)|only\s+today|hurry|act\s+now|expires?\s+(soon|today|in)|derni[eè]re\s+chance|places?\s+limit[eé]es|d[eé]p[eê]chez|buruan|segera|kesempatan\s+terakhir|terbatas|nhanh\s+tay|c[oơ]\s+h[oộ]i\s+cu[oố]i|s[oố]\s+l[uư][oơ]ng\s+c[oó]\s+h[aạ]n|haraka|nafasi\s+chache|nafasi\s+ya\s+mwisho"),
    "recruit": ("warn", r"invite\s+(your\s+)?friends|referral|recruit|downline|team\s+commission|parrain|invitez\s+vos|ajak\s+teman|undang\s+teman|m[oờ]i\s+b[aạ]n\s+b[eè]|gi[oớ]i\s+thi[eệ]u\s+b[aạ]n|waalike\s+marafiki|alika\s+marafiki"),
    "dm": ("warn", r"\bdm\s+me\b|message\s+me|contact\s+(me|@)|whats\s*app|support\s+(team|agent)|customer\s+(service|support)|\badmin\b|[eé]cris[- ]moi\s+en\s+priv|hubungi\s+(saya|admin)|chat\s+pribadi|nh[aắ]n\s+tin\s+ri[eê]ng|li[eê]n\s+h[eệ]\s+admin|nitumie\s+ujumbe|wasiliana\s+na\s+(mimi|admin)"),
    "connect": ("warn", r"(connect|validate|verify|sync|synchronize|rectify|restore)\s+(your\s+)?wallet|wallet\s+(validation|sync|verification)|connecte[rz]?\s+(votre\s+)?portefeuille|hubungkan\s+dompet|k[eế]t\s+n[oố]i\s+v[ií]|unganisha\s+pochi"),
    "link": ("warn", r"bit\.ly|tinyurl|cutt\.ly|t\.co/|is\.gd|rb\.gy|shorturl|goo\.gl|wa\.me/|t\.me/\+|xn--"),
    "feeout": ("warn", r"withdraw(al)?\s+(fee|tax)|release\s+(fee|tax)|unlock\s+fee|tax\s+to\s+withdraw|frais\s+de\s+retrait|biaya\s+penarikan|ph[ií]\s+r[uú]t|ada\s+pajak\s+penarikan|ada\s+ya\s+kutoa"),
    "easy": ("warn", r"no\s+experience|easy\s+money|get\s+rich|work\s+from\s+home|earn\s+\$?\d+[\d,]*\s*(a|per|/)\s*(day|hour|week)|sans\s+exp[eé]rience|argent\s+facile|tanpa\s+pengalaman|uang\s+mudah|kh[oô]ng\s+c[aầ]n\s+kinh\s+nghi[eệ]m|ki[eế]m\s+ti[eề]n\s+d[eễ]|bila\s+uzoefu|pesa\s+rahisi"),
}

UI = {
    "en": {
        "btn": "🚩 Red flag check",
        "prompt": "🚩 <b>Red flag check</b>\n\nPaste the text of an offer, a message or a post (up to 3000 characters). I will look for the usual signs of a scam.\n\nI do not send your text anywhere. I do not say if something is safe.",
        "hint": "Send the text as a message (up to 3000 characters).",
        "title": "Red flag check", "stop": "STOP signs", "warn": "Warnings",
        "none": "I did not find the usual red flags in this text. This does not mean it is safe. Scams change fast. Check the other steps.",
        "next_stop": "Do not send money, do not share anything and do not install anything. Stop talking to this person.",
        "next_warn": "Slow down. Check the sender and the website yourself, from official sources.",
        "next": "What to do next",
        "steps": "1. Find the official website yourself. Do not use links from the message.\n2. Never share your seed phrase. Nobody real needs it.\n3. Go through the checklist before you spend anything.",
        "note": "Information only. I look at words, not at the real project.",
        "another": "🚩 Check another text", "guide": "📋 Safe airdrops guide", "tool": "✅ Token check tool",
        "flags": {
            "seed": "It mentions a seed phrase or private key. Nobody real needs them. Never share them.",
            "payfirst": "It asks you to pay or send money first, or promises to double what you send. This is the classic scam.",
            "remote": "It asks you to install an app or to share your screen. This lets a scammer control your phone or computer.",
            "guarantee": "It promises guaranteed profit or no risk. Real investments always have risk.",
            "daily": "It promises a fixed return every day or week. Real returns are not steady like this.",
            "urgent": "It pushes you to hurry. Scammers use pressure so you do not think.",
            "recruit": "It asks you to bring in friends or build a team. Many scams pay people only from new members.",
            "dm": "It asks you to talk in private, or to contact an admin or support. Real support does not message you first.",
            "connect": "It asks you to connect, verify or sync your wallet. This can empty the wallet.",
            "link": "It has a short link or a link that hides the real website. Open only the official website that you found yourself.",
            "feeout": "It asks for a fee or a tax before you can take your money out. Real services take fees from the balance.",
            "easy": "It promises easy money with no skills. If it were true, everybody would do it.",
        },
    },
    "fr": {
        "btn": "🚩 Détecteur d'arnaque",
        "prompt": "🚩 <b>Détecteur d'arnaque</b>\n\nColle le texte d'une offre, d'un message ou d'une publication (3000 caractères maximum). Je cherche les signes habituels d'arnaque.\n\nJe n'envoie ton texte nulle part. Je ne dis pas si quelque chose est sûr.",
        "hint": "Envoie le texte dans un message (3000 caractères maximum).",
        "title": "Détecteur d'arnaque", "stop": "Signes d'ARRÊT", "warn": "Alertes",
        "none": "Je n'ai pas trouvé les signaux d'alerte habituels dans ce texte. Cela ne veut pas dire que c'est sûr. Les arnaques changent vite. Vérifie les autres étapes.",
        "next_stop": "N'envoie pas d'argent, ne partage rien et n'installe rien. Arrête de parler à cette personne.",
        "next_warn": "Ralentis. Vérifie toi-même l'expéditeur et le site, avec des sources officielles.",
        "next": "Que faire ensuite",
        "steps": "1. Trouve toi-même le site officiel. N'utilise pas les liens du message.\n2. Ne partage jamais ta phrase secrète. Personne de sérieux n'en a besoin.\n3. Passe la checklist avant de dépenser quoi que ce soit.",
        "note": "Information seulement. J'analyse des mots, pas le vrai projet.",
        "another": "🚩 Vérifier un autre texte", "guide": "📋 Guide airdrops sûrs", "tool": "✅ Outil de vérification",
        "flags": {
            "seed": "Il parle d'une phrase secrète ou d'une clé privée. Personne de sérieux n'en a besoin. Ne les partage jamais.",
            "payfirst": "Il demande de payer ou d'envoyer de l'argent d'abord, ou promet de doubler ce que tu envoies. C'est l'arnaque classique.",
            "remote": "Il demande d'installer une appli ou de partager ton écran. Un escroc peut ainsi prendre le contrôle de ton appareil.",
            "guarantee": "Il promet un gain garanti ou sans risque. Un vrai investissement a toujours un risque.",
            "daily": "Il promet un rendement fixe chaque jour ou chaque semaine. Un vrai rendement n'est pas aussi régulier.",
            "urgent": "Il te pousse à te dépêcher. Les escrocs utilisent la pression pour que tu ne réfléchisses pas.",
            "recruit": "Il demande de ramener des amis ou de former une équipe. Beaucoup d'arnaques ne paient qu'avec l'argent des nouveaux.",
            "dm": "Il demande de parler en privé ou de contacter un admin ou le support. Le vrai support ne t'écrit pas en premier.",
            "connect": "Il demande de connecter, vérifier ou synchroniser ton portefeuille. Cela peut le vider.",
            "link": "Il contient un lien raccourci ou qui cache le vrai site. Ouvre seulement le site officiel trouvé par toi-même.",
            "feeout": "Il demande des frais ou une taxe avant de retirer ton argent. Un vrai service prélève ses frais sur le solde.",
            "easy": "Il promet de l'argent facile sans compétence. Si c'était vrai, tout le monde le ferait.",
        },
    },
    "id": {
        "btn": "🚩 Cek tanda bahaya",
        "prompt": "🚩 <b>Cek tanda bahaya</b>\n\nTempel teks penawaran, pesan, atau postingan (maksimal 3000 karakter). Saya cari tanda-tanda penipuan yang umum.\n\nTeks Anda tidak saya kirim ke mana pun. Saya tidak bilang apakah sesuatu aman.",
        "hint": "Kirim teksnya sebagai pesan (maksimal 3000 karakter).",
        "title": "Cek tanda bahaya", "stop": "Tanda BERHENTI", "warn": "Peringatan",
        "none": "Saya tidak menemukan tanda bahaya yang umum di teks ini. Ini tidak berarti aman. Penipuan cepat berubah. Periksa langkah lainnya.",
        "next_stop": "Jangan kirim uang, jangan bagikan apa pun, dan jangan pasang apa pun. Berhenti berbicara dengan orang ini.",
        "next_warn": "Pelan-pelan. Periksa sendiri pengirim dan situsnya dari sumber resmi.",
        "next": "Langkah berikutnya",
        "steps": "1. Cari sendiri situs resminya. Jangan pakai tautan dari pesan.\n2. Jangan pernah bagikan frasa pemulihan. Orang yang asli tidak membutuhkannya.\n3. Ikuti checklist sebelum mengeluarkan uang.",
        "note": "Hanya informasi. Saya membaca kata-kata, bukan proyek aslinya.",
        "another": "🚩 Cek teks lain", "guide": "📋 Panduan airdrop aman", "tool": "✅ Alat cek token",
        "flags": {
            "seed": "Teks menyebut frasa pemulihan atau kunci privat. Orang yang asli tidak membutuhkannya. Jangan pernah dibagikan.",
            "payfirst": "Teks meminta Anda bayar atau kirim uang dulu, atau berjanji menggandakan kiriman Anda. Ini penipuan klasik.",
            "remote": "Teks meminta Anda memasang aplikasi atau membagikan layar. Penipu bisa mengendalikan ponsel atau komputer Anda.",
            "guarantee": "Teks menjanjikan untung pasti atau tanpa risiko. Investasi yang asli selalu ada risikonya.",
            "daily": "Teks menjanjikan hasil tetap tiap hari atau minggu. Hasil yang asli tidak setetap itu.",
            "urgent": "Teks mendesak Anda untuk buru-buru. Penipu memakai tekanan agar Anda tidak berpikir.",
            "recruit": "Teks meminta Anda mengajak teman atau membangun tim. Banyak penipuan hanya membayar dari uang anggota baru.",
            "dm": "Teks meminta Anda bicara secara pribadi, atau menghubungi admin atau dukungan. Dukungan yang asli tidak menghubungi Anda lebih dulu.",
            "connect": "Teks meminta Anda menghubungkan, memverifikasi, atau menyinkronkan dompet. Ini bisa menguras dompet.",
            "link": "Ada tautan pendek atau tautan yang menyembunyikan situs aslinya. Buka hanya situs resmi yang Anda temukan sendiri.",
            "feeout": "Teks meminta biaya atau pajak sebelum Anda bisa menarik uang. Layanan yang asli memotong biaya dari saldo.",
            "easy": "Teks menjanjikan uang mudah tanpa keahlian. Kalau benar, semua orang akan melakukannya.",
        },
    },
    "vi": {
        "btn": "🚩 Kiểm tra dấu hiệu lừa đảo",
        "prompt": "🚩 <b>Kiểm tra dấu hiệu lừa đảo</b>\n\nDán nội dung một lời mời, tin nhắn hoặc bài đăng (tối đa 3000 ký tự). Tôi sẽ tìm các dấu hiệu lừa đảo thường gặp.\n\nTôi không gửi văn bản của bạn đi đâu cả. Tôi không nói điều gì đó có an toàn hay không.",
        "hint": "Gửi nội dung dưới dạng tin nhắn (tối đa 3000 ký tự).",
        "title": "Kiểm tra dấu hiệu lừa đảo", "stop": "Dấu hiệu DỪNG LẠI", "warn": "Cảnh báo",
        "none": "Tôi không thấy các dấu hiệu cảnh báo thường gặp trong văn bản này. Điều đó không có nghĩa là an toàn. Chiêu lừa thay đổi rất nhanh. Hãy kiểm tra các bước khác.",
        "next_stop": "Đừng chuyển tiền, đừng chia sẻ gì và đừng cài gì. Hãy ngừng nói chuyện với người này.",
        "next_warn": "Hãy chậm lại. Tự kiểm tra người gửi và trang web từ nguồn chính thức.",
        "next": "Việc cần làm tiếp theo",
        "steps": "1. Tự tìm trang web chính thức. Đừng dùng liên kết trong tin nhắn.\n2. Không bao giờ chia sẻ cụm từ khôi phục. Người thật không cần nó.\n3. Đi qua checklist trước khi tiêu bất kỳ khoản tiền nào.",
        "note": "Chỉ là thông tin. Tôi đọc chữ, không đánh giá dự án thật.",
        "another": "🚩 Kiểm tra văn bản khác", "guide": "📋 Hướng dẫn airdrop an toàn", "tool": "✅ Công cụ kiểm tra token",
        "flags": {
            "seed": "Văn bản nhắc đến cụm từ khôi phục hoặc khóa riêng. Người thật không cần chúng. Đừng bao giờ chia sẻ.",
            "payfirst": "Văn bản yêu cầu bạn trả hoặc gửi tiền trước, hoặc hứa nhân đôi số tiền bạn gửi. Đây là chiêu lừa kinh điển.",
            "remote": "Văn bản yêu cầu bạn cài ứng dụng hoặc chia sẻ màn hình. Kẻ lừa đảo có thể điều khiển điện thoại hoặc máy tính của bạn.",
            "guarantee": "Văn bản hứa lợi nhuận chắc chắn hoặc không rủi ro. Đầu tư thật luôn có rủi ro.",
            "daily": "Văn bản hứa lợi nhuận cố định mỗi ngày hoặc mỗi tuần. Lợi nhuận thật không đều như vậy.",
            "urgent": "Văn bản thúc ép bạn làm nhanh. Kẻ lừa đảo tạo áp lực để bạn không kịp suy nghĩ.",
            "recruit": "Văn bản yêu cầu bạn mời bạn bè hoặc lập nhóm. Nhiều vụ lừa chỉ trả tiền từ người mới vào.",
            "dm": "Văn bản yêu cầu nói chuyện riêng hoặc liên hệ admin hay hỗ trợ. Hỗ trợ thật không nhắn cho bạn trước.",
            "connect": "Văn bản yêu cầu kết nối, xác minh hoặc đồng bộ ví. Việc này có thể làm sạch ví của bạn.",
            "link": "Có liên kết rút gọn hoặc liên kết che giấu trang web thật. Chỉ mở trang chính thức do chính bạn tìm ra.",
            "feeout": "Văn bản đòi phí hoặc thuế trước khi bạn rút tiền. Dịch vụ thật trừ phí từ số dư.",
            "easy": "Văn bản hứa kiếm tiền dễ dàng, không cần kỹ năng. Nếu đúng vậy thì ai cũng làm.",
        },
    },
    "sw": {
        "btn": "🚩 Kagua dalili za utapeli",
        "prompt": "🚩 <b>Kagua dalili za utapeli</b>\n\nBandika maandishi ya ofa, ujumbe au chapisho (hadi herufi 3000). Nitatafuta dalili za kawaida za utapeli.\n\nSitumi maandishi yako popote. Sisemi kama kitu ni salama.",
        "hint": "Tuma maandishi kama ujumbe (hadi herufi 3000).",
        "title": "Kagua dalili za utapeli", "stop": "Dalili za KUSIMAMA", "warn": "Maonyo",
        "none": "Sikuona dalili za kawaida za hatari kwenye maandishi haya. Hii haimaanishi ni salama. Utapeli hubadilika haraka. Kagua hatua nyingine.",
        "next_stop": "Usitume pesa, usishiriki chochote na usisakinishe chochote. Acha kuzungumza na mtu huyu.",
        "next_warn": "Punguza kasi. Kagua mtumaji na tovuti mwenyewe kupitia vyanzo rasmi.",
        "next": "Cha kufanya baadaye",
        "steps": "1. Tafuta tovuti rasmi mwenyewe. Usitumie viungo vya ujumbe.\n2. Usishiriki maneno ya siri ya pochi. Mtu halali hayahitaji.\n3. Pitia orodha ya ukaguzi kabla ya kutumia pesa yoyote.",
        "note": "Taarifa tu. Ninasoma maneno, si mradi halisi.",
        "another": "🚩 Kagua maandishi mengine", "guide": "📋 Mwongozo wa airdrop salama", "tool": "✅ Zana ya kukagua tokeni",
        "flags": {
            "seed": "Inataja maneno ya siri ya pochi au ufunguo binafsi. Mtu halali hayahitaji. Usiyashiriki kamwe.",
            "payfirst": "Inakutaka ulipe au utume pesa kwanza, au inaahidi kuzidisha pesa unayotuma mara mbili. Huu ni utapeli wa kawaida.",
            "remote": "Inakutaka usakinishe programu au ushiriki skrini. Tapeli anaweza kudhibiti simu au kompyuta yako.",
            "guarantee": "Inaahidi faida ya uhakika au bila hatari. Uwekezaji halisi daima una hatari.",
            "daily": "Inaahidi faida ile ile kila siku au wiki. Faida halisi si thabiti hivyo.",
            "urgent": "Inakusukuma ufanye haraka. Matapeli hutumia presha ili usifikirie.",
            "recruit": "Inakutaka ualike marafiki au ujenge timu. Utapeli mwingi hulipa kwa pesa za wanachama wapya tu.",
            "dm": "Inakutaka uzungumze faragha, au uwasiliane na admin au msaada. Msaada halali hauanzi kukutumia ujumbe.",
            "connect": "Inakutaka uunganishe, uthibitishe au usawazishe pochi. Hii inaweza kuimaliza pochi.",
            "link": "Ina kiungo kifupi au kiungo kinachoficha tovuti halisi. Fungua tovuti rasmi uliyoipata mwenyewe tu.",
            "feeout": "Inadai ada au kodi kabla ya kutoa pesa zako. Huduma halali hukata ada kwenye salio.",
            "easy": "Inaahidi pesa rahisi bila ujuzi. Kama ingekuwa kweli, kila mtu angefanya.",
        },
    },
    "simple": {
        "btn": "🚩 Red flag check",
        "prompt": "🚩 <b>Red flag check</b>\n\nPaste the text of an offer, a message or a post (up to 3000 characters). I look for the usual signs of a scam.\n\nI do not send your text anywhere. I do not say if something is safe.",
        "hint": "Send the text as a message (up to 3000 characters).",
        "title": "Red flag check", "stop": "STOP signs", "warn": "Warnings",
        "none": "I did not find the usual red flags in this text. This does not mean it is safe. Scams change fast. Check the other steps.",
        "next_stop": "Do not send money. Do not share anything. Do not install anything. Stop talking to this person.",
        "next_warn": "Slow down. Check the sender and the website yourself. Use official sources.",
        "next": "What to do next",
        "steps": "1. Find the official website yourself. Do not use links from the message.\n2. Never share your seed phrase. A real person never needs it.\n3. Go through the checklist before you spend any money.",
        "note": "Information only. I read the words. I do not check the real project.",
        "another": "🚩 Check another text", "guide": "📋 Safe airdrops guide", "tool": "✅ Token check tool",
        "flags": {
            "seed": "It talks about a seed phrase or a private key. Nobody real needs them. Never share them.",
            "payfirst": "It asks you to pay or send money first. Or it says it will double the money you send. This is a very old scam.",
            "remote": "It asks you to install an app or share your screen. Then a scammer can control your phone or computer.",
            "guarantee": "It promises a sure profit or no risk. Real investing always has risk.",
            "daily": "It promises the same profit every day or week. Real profit is not steady like this.",
            "urgent": "It tells you to hurry. Scammers use pressure so you do not think.",
            "recruit": "It asks you to bring friends or build a team. Many scams pay old members only with money from new members.",
            "dm": "It asks you to talk in private, or to contact an admin or support. Real support does not write to you first.",
            "connect": "It asks you to connect, check or sync your wallet. This can empty your wallet.",
            "link": "It has a short link, or a link that hides the real website. Open only the official website that you found yourself.",
            "feeout": "It asks for a fee or a tax before you can take your money out. Real services take their fee from your balance.",
            "easy": "It promises easy money with no skills. If this were true, everybody would do it.",
        },
    },
}

_COMPILED = {k: (lvl, re.compile(rx, re.I)) for k, (lvl, rx) in RULES.items()}


def scan(text: str) -> list:
    """Список id сработавших правил в порядке: сначала STOP, потом предупреждения."""
    hits = [(0 if lvl == "stop" else 1, k) for k, (lvl, rx) in _COMPILED.items() if rx.search(text)]
    return [k for _, k in sorted(hits)]


def prompt_screen(lang: str) -> tuple:
    return UI[lang]["prompt"], []


def analyze(text: str, lang: str, site_url: str = "https://chainscout.app") -> tuple:
    ui = UI[lang]
    text = (text or "").strip()
    if not text or len(text) > MAX_LEN:
        return ui["hint"], []
    hits = scan(text)
    stops = [k for k in hits if RULES[k][0] == "stop"]
    warns = [k for k in hits if RULES[k][0] == "warn"]
    out = [f"<b>{ui['title']}</b>\n"]
    if not hits:
        out.append(ui["none"])
    if stops:
        out.append(f"<b>🛑 {ui['stop']}</b>")
        out += [f"• {ui['flags'][k]}" for k in stops]
        out.append("")
    if warns:
        out.append(f"<b>⚠️ {ui['warn']}</b>")
        out += [f"• {ui['flags'][k]}" for k in warns]
        out.append("")
    if hits:
        out.append(f"<b>{ui['next']}</b>")
        out.append(ui["next_stop"] if stops else ui["next_warn"])
        out.append(ui["steps"])
    out.append(f"\n<i>{ui['note']}</i>")
    rows = [
        [("cb", ui["guide"], "gd:join-airdrops-safely:0")],
        [("url", ui["tool"], f"{site_url}/{lang}/check/")],
    ]
    return "\n".join(out), rows
