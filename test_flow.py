"""Прогон бота по всем кнопкам без токена и сети: python test_flow.py

Для каждого языка заводит нового пользователя, нажимает все кнопки, до которых можно дойти,
и проверяет: нет ли «мёртвых» кнопок, влезают ли сообщения в лимиты Telegram и корректна ли HTML-разметка.
"""
import asyncio
import os
import re
import sys
import tempfile
from types import SimpleNamespace

os.environ["DATA_FILE"] = os.path.join(tempfile.mkdtemp(), "state.json")
os.environ["ADMIN_IDS"] = ""

import devstubs  # noqa: E402

devstubs.install_if_needed()

import bot  # noqa: E402
from guides import GUIDES  # noqa: E402
from locales import LANGS  # noqa: E402


class Screen:
    def __init__(self, text, markup):
        self.text, self.markup = text, markup


class FakeMessage:
    def __init__(self, sink):
        self.sink = sink

    async def reply_text(self, text, reply_markup=None, **kwargs):
        self.sink.append(Screen(text, reply_markup))


class FakeQuery:
    def __init__(self, uid, data, sink):
        self.data, self.from_user, self.sink = data, SimpleNamespace(id=uid), sink

    async def answer(self, *args, **kwargs):
        pass

    async def edit_message_text(self, text, reply_markup=None, **kwargs):
        self.sink.append(Screen(text, reply_markup))


def command(uid, sink):
    message = FakeMessage(sink)
    return SimpleNamespace(callback_query=None, effective_user=SimpleNamespace(id=uid), effective_message=message, message=message)


def press(uid, data, sink):
    query = FakeQuery(uid, data, sink)
    return SimpleNamespace(callback_query=query, effective_user=query.from_user, effective_message=None)


TAGS = re.compile(r"</?(b|i)>")


def check_screen(where, screen):
    text = screen.text
    assert 0 < len(text) <= 4096, f"{where}: длина сообщения {len(text)}"
    assert text.count("<b>") == text.count("</b>") and text.count("<i>") == text.count("</i>"), f"{where}: теги не парные"
    assert "<" not in TAGS.sub("", text), f"{where}: посторонний тег или неэкранированный символ <"
    for row in screen.markup.inline_keyboard:
        assert 1 <= len(row) <= 3, f"{where}: в ряду {len(row)} кнопок"
        for button in row:
            assert button.text.strip(), f"{where}: пустая кнопка"
            if button.url:
                assert button.url.startswith("https://"), f"{where}: ссылка не https"
            else:
                assert len(button.callback_data.encode()) <= 64, f"{where}: callback_data {button.callback_data} длиннее 64 байт"


async def crawl(lang, uid):
    sink = []
    await bot.on_button(press(uid, f"lang:{lang}", sink), None)
    queue, seen, clicks = [sink[-1]], set(), 0
    while queue:
        screen = queue.pop()
        check_screen(f"{lang}/старт", screen)
        for row in screen.markup.inline_keyboard:
            for button in row:
                data = button.callback_data
                if button.url or data in seen or data.startswith("lang:"):
                    continue
                seen.add(data)
                out = []
                await bot.on_button(press(uid, data, out), None)
                clicks += 1
                assert out or data == "noop", f"{lang}: кнопка {data} ничего не показала"
                for screen_out in out:
                    check_screen(f"{lang}/{data}", screen_out)
                    queue.append(screen_out)
    return clicks, seen


async def main():
    for index, lang in enumerate(LANGS, start=1):
        clicks, seen = await crawl(lang, 1000 + index)
        for slug, guide in GUIDES.items():
            pages = bot.guide_pages(slug, lang)
            for page in range(len(pages)):
                assert f"gd:{slug}:{page}" in seen, f"{lang}: гид {slug}, страница {page} недостижима"
            assert f"gd:{slug}:last" in seen, f"{lang}: из инструмента нельзя вернуться в гид {slug}"
            for tool_id in guide["tools"]:
                assert f"tool:{tool_id}:g:{slug}" in seen, f"{lang}: инструмент {tool_id} не показан в гиде {slug}"
        sizes = {slug: len(bot.guide_pages(slug, lang)) for slug in GUIDES}
        print(f"{lang}: нажато {clicks} кнопок, страниц в гидах {sizes}")

    # крайние случаи
    uid, out = 2000, []
    await bot.cmd_guides(command(uid, out), None)
    assert "Choose your language" in out[-1].text, "/guides без языка должен предложить выбрать язык"
    await bot.on_button(press(uid, "lang:vi", out), None)
    await bot.cmd_guides(command(uid, out), None)
    assert out[-1].markup.inline_keyboard[0][0].callback_data.startswith("gd:"), "/guides: нет списка гидов"
    slug = next(iter(GUIDES))
    out.clear()
    await bot.on_button(press(uid, f"gd:{slug}:99", out), None)
    assert out and not any(b.callback_data.startswith("gd:") and b.text.startswith("Tiếp") for r in out[-1].markup.inline_keyboard for b in r), "страница 99 должна свестись к последней"
    out.clear()
    await bot.on_button(press(uid, f"gd:{slug}:abc", out), None)
    assert out, "нечисловая страница должна открыть первую"
    out.clear()
    await bot.on_button(press(uid, "gd:no-such-guide:0", out), None)
    assert not out, "несуществующий гид должен игнорироваться"
    out.clear()
    await bot.on_button(press(uid, "tool:coingecko:g:no-such-guide", out), None)
    assert out and out[-1].markup.inline_keyboard[-1][0].callback_data.startswith("cat:"), "неверный источник должен вести в категорию"
    print("крайние случаи: OK")


if __name__ == "__main__":
    asyncio.run(main())
    print("OK: бот прошёл по всем кнопкам на всех языках")
    sys.exit(0)
