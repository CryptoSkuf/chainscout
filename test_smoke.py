"""Быстрая проверка без токена и сети: python test_smoke.py"""
import os
import re
import sys
import tempfile

os.environ.setdefault("DATA_FILE", os.path.join(tempfile.mkdtemp(), "state.json"))

import devstubs  # noqa: E402

devstubs.install_if_needed()

import bot  # noqa: E402
from guides import GUIDE_UI, GUIDES  # noqa: E402
from locales import LANGS, STRINGS  # noqa: E402


def main() -> None:
    en_keys = set(STRINGS["en"])
    assert set(STRINGS) == set(LANGS), "языки в LANGS и STRINGS не совпадают"
    for lang, table in STRINGS.items():
        missing = en_keys - set(table)
        extra = set(table) - en_keys
        assert not missing and not extra, f"{lang}: нет {missing}, лишние {extra}"
        for key, text in table.items():
            leftovers = re.sub(r"\{name\}", "", text)
            assert "{" not in leftovers and "}" not in leftovers, f"{lang}.{key}: лишние скобки"
            assert text.count("<b>") == text.count("</b>"), f"{lang}.{key}: теги <b>"

    for tool in bot.CATALOG:
        for lang in LANGS:
            assert bot.tool_desc(tool, lang), f"{tool['id']}/{lang}: нет описания"
            text = bot.tool_text(tool, lang)
            assert text.count("<i>") == text.count("</i>")
            bot.kb_tool(lang, tool, "menu")
    for lang in LANGS:
        bot.t(lang, "welcome")
        bot.kb_menu(lang, False)
        bot.kb_cats(lang)
        bot.kb_tools(lang, bot.visible_tools(), "all", "menu")
        bot.kb_guides(lang)

    # гиды: все языки, короткие названия для кнопок, страницы влезают в сообщение Telegram
    assert set(GUIDE_UI) == set(LANGS), "GUIDE_UI: языки не совпадают"
    for slug, guide in GUIDES.items():
        assert set(guide["lang"]) == set(LANGS) and set(guide["short"]) == set(LANGS), slug
        assert all(tool_id in bot.BY_ID for tool_id in guide["tools"]), f"{slug}: неизвестный инструмент"
        for lang in LANGS:
            assert len(guide["short"][lang]) <= 40, f"{slug}/{lang}: короткое название длиннее 40"
            for page in bot.guide_pages(slug, lang):
                assert len(page) <= 4000, f"{slug}/{lang}: страница {len(page)} символов"

    # лимит Telegram на callback_data: 64 байта
    longest = max(len(f"tool:{x['id']}:g:{slug}") for x in bot.CATALOG for slug in GUIDES)
    assert longest <= 64

    print(bot.build_report())
    print(f"OK: {len(bot.CATALOG)} инструментов, {len(GUIDES)} гидов, {len(LANGS)} языков")


if __name__ == "__main__":
    sys.exit(main())
