"""Simple English для инструкций «как начать» (12 инструментов). Короткие предложения, простые слова.
Подключается в конце howto.py."""

HOWTO_UI_SIMPLE = {
    "btn": "🧭 How to start",
    "title": "How to start with {tool}",
    "back": "◀️ Back to {tool}",
    "summary": "How to start (5 steps)",
}


def _h(steps, note):
    return {"steps": steps, "note": note}


HOWTO_SIMPLE = {
    "coingecko": _h(
        [
            "Open the CoinGecko website. Type the name of the token in the search box.",
            "Pick the result with the right name and symbol. Fake tokens copy names. So compare the contract address on the page with the one on the project's own website.",
            "Look at the market cap, the trading volume for 24 hours and the number of markets. Very low volume, or only one small market, means one trade can move the price.",
            "Use the official website and social links on the token page. Do not use links that someone sent you in a chat.",
            "Open the price chart with the longest time range. You will see the whole history. Also check which exchanges list the token.",
        ],
        "CoinGecko shows data. It does not tell you if a token is safe or if it will go up.",
    ),
    "goplus": _h(
        [
            "Open the GoPlus website. Find its token security checker.",
            "Choose the blockchain network of the token. For example Ethereum, BNB Chain, Solana or TRON.",
            "Paste the contract address. Copy it from the project's official website or from CoinGecko. Do not copy it from a chat message. Then run the check.",
            "Read the warnings first. A honeypot means you can buy but you cannot sell. Also look for a very high buy or sell tax, an owner who can make new tokens or change the rules, and hidden owners.",
            "If the report shows many risks, do not buy and do not approve anything. If it looks clean, remember that this is only one part of the picture.",
        ],
        "A clean scan is not a promise. New scams are made to pass checks. The tool cannot see the plans of the team.",
    ),
    "tokenmetrics": _h(
        [
            "Open Token Metrics. Search for the token you want to look at.",
            "Do not read only the big number. Read what the rating is made of. Open the details for each part.",
            "Compare it with two other sources. Use CoinGecko for market data and the project's own documents.",
            "Check the date of every report. Markets change fast, so an old rating can be wrong now.",
            "Before you pay, check which features need a paid plan. Also check what the free version gives you.",
        ],
        "An AI rating is the opinion of a model. It is not a forecast and it is not advice.",
    ),
    "kaito": _h(
        [
            "Open Kaito. Type a project or a topic in simple words.",
            "Read the sources behind each answer. Open the original posts and articles. Do not read only the summary.",
            "Look for topics that come back over many days. A real story is not one loud post.",
            "Check who is posting. Paid promotion and bot accounts can make attention look bigger than it is.",
            "Check every claim on the project's official website or on CoinGecko before you act on it.",
        ],
        "Attention is not value. A token that everyone talks about can still be a scam.",
    ),
    "messari": _h(
        [
            "Open Messari. Search for the project by name.",
            "Read the project profile and the research. Find out what it does, who is behind it, how it makes money and what the risks are.",
            "Use the AI assistant for specific questions. Then open the source links it gives you and check them.",
            "Check the date of the data. Also check which parts are free and which parts need a paid plan.",
            "Write three lines in your own words: what it does, how it earns money, and the main risk. If you cannot, you do not understand it yet.",
        ],
        "Reports describe projects. They do not tell you when to buy or sell.",
    ),
    "santiment": _h(
        [
            "Open Santiment. Search for an asset.",
            "Look at social volume and mood next to the price. Look at weeks, not hours.",
            "Notice sudden jumps in talk. Ask yourself: did the talk come before the price move or after it?",
            "Add one on-chain number, such as active addresses. It shows if real use matches the talk.",
            "Check which numbers need a paid plan. Also check if the free data comes late.",
        ],
        "The mood of the crowd is noisy and people can fake it. It is not a signal to trade.",
    ),
    "nansen": _h(
        [
            "Open Nansen. Start from a token page or a wallet address.",
            "Find the labelled wallets, such as exchanges and funds. See what they hold.",
            "Check if a big move is only one wallet moving money between its own addresses, or a real sale.",
            "Compare the money going to and from exchanges with the price in the same period.",
            "This is an advanced tool and most of it is paid. See what the free version shows before you pay.",
        ],
        "Labels are guesses and can be wrong. Following big wallets does not promise a gain.",
    ),
    "arkham": _h(
        [
            "Open Arkham. Paste a wallet address or search for a name.",
            "Open the visual explorer. It shows which addresses and groups the wallet works with.",
            "Read the labels with care. An address with no label is unknown. It is not safe.",
            "Follow the biggest transfers. See where the money went, for example to an exchange or to a new wallet.",
            "If alerts are available, set one for an address you want to watch.",
        ],
        "Linking an address to a real person or company can be wrong. Do not accuse anyone because of a label.",
    ),
    "glassnode": _h(
        [
            "Open Glassnode. Start with the free dashboards for Bitcoin and Ethereum.",
            "Learn one number at a time. Read its description first. For example: active addresses, or supply held by long-term holders.",
            "Look at long periods, such as several years. Do not look only at the last few days.",
            "Compare the number with the price in earlier cycles. See how it acted before.",
            "Check which numbers are paid before you subscribe. Most of the advanced ones are.",
        ],
        "On-chain numbers describe the past. They do not tell you what comes next.",
    ),
    "dune": _h(
        [
            "Open Dune. Search for a dashboard by the name of the project.",
            "Open a community dashboard. Read its title, its author and the date of the last update.",
            "Check which blockchain it covers and what exactly it counts. Dashboards can define things in different ways.",
            "Compare two dashboards for the same project. If the numbers are different, find out why.",
            "Only if you know SQL: copy a query to your own account. Change one thing at a time.",
        ],
        "Anyone can publish a dashboard. Check the author and the data before you trust a chart.",
    ),
    "defillama": _h(
        [
            "Open DefiLlama. Look at the DeFi ranking by TVL. TVL means total value locked.",
            "Click on a project. Check how its TVL changed over time and on which blockchains it runs.",
            "Watch for sudden drops. Also watch for TVL that is mostly the project's own token. It can look bigger than it is.",
            "Look for audit and past hack information on the page. Check the stablecoin and chain pages for more context.",
            "Be careful with very high yields. A high yield usually means high risk.",
        ],
        "TVL shows how much money is deposited. It does not show how safe a project is.",
    ),
    "tradingview": _h(
        [
            "Open TradingView. Search for a coin or a trading pair.",
            "Choose a time frame. Start with the daily chart. It is calmer than minute charts.",
            "Add only one or two indicators, such as volume and a moving average. More indicators do not make the chart clearer.",
            "Read ideas from other users as opinions only. Check who wrote them and if they were right before.",
            "Practise with paper trading. It uses no real money. Also check the limits of the free plan.",
        ],
        "Charts show the past. Ideas from other people are not advice.",
    ),
    "publicaml": _h(
        [
            "Type publicaml.org in your browser yourself. Do not use a link from a chat.",
            "Paste a public wallet address. Never paste a seed phrase or a private key.",
            "Read the risk score and the labels. Open the sources behind each label.",
            "If you will keep USDT or USDC, check if the address is frozen.",
            "Compare with a second tool. Keep a screenshot with the date.",
        ],
        "The risk score is the service's own guess. No flags does not mean the money is clean. The website does not say who runs it.",
    ),
}
