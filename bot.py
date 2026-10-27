#!/usr/bin/env python3
"""ChainScout: Telegram-бот, который предлагает ИИ-инструменты для анализа криптовалют.

Устроен по схеме из видео («бот-CEO агентного бизнеса»):
  * каталог инструментов на 5 языках (en, fr, id, vi, sw) для Африки и ЮВА;
  * ежедневная рутина: проверка ссылок каталога, по понедельникам отчёт владельцу;
  * рассылки и спонсорские размещения уходят только после подтверждения владельцем.

Запуск: см. README.md
"""
from __future__ import annotations

import asyncio
import datetime as dt
import functools
import html
import json
import logging
import os
import re
from collections import Counter
from pathlib import Path

import httpx
from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LinkPreviewOptions,
    Update,
)
from telegram.constants import ParseMode
from telegram.error import BadRequest, Forbidden, TelegramError
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
)

from guides import GUIDE_UI, GUIDES
from locales import LANGS, STRINGS

try:  # необязательная зависимость: читает .env рядом с ботом
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

log = logging.getLogger("chainscout")
UTC = dt.timezone.utc
BASE = Path(__file__).parent

BOT_NAME = os.getenv("BOT_NAME", "ChainScout")
ADMIN_IDS = {int(x) for x in os.getenv("ADMIN_IDS", "").replace(" ", "").split(",") if x}
DATA_FILE = Path(os.getenv("DATA_FILE", BASE / "state.json"))
ROUTINE_TIME = os.getenv("ROUTINE_TIME_UTC", "06:00")
STALE_DAYS = 45

CATEGORIES = ["market", "onchain", "sentiment", "research", "safety"]
LEVELS = ["beginner", "intermediate", "advanced"]
LANG_PROMPT = (
    "🌍 Choose your language · Choisissez votre langue · Pilih bahasa · "
    "Chọn ngôn ngữ · Chagua lugha"
)

NO_PREVIEW = LinkPreviewOptions(is_disabled=True)
PAGE_CHARS = 3200  # длина страницы гида; лимит одного сообщения Telegram: 4096 символов


# --------------------------------------------------------------------- catalog
def load_catalog() -> list[dict]:
    items = json.loads((BASE / "catalog.json").read_text("utf-8"))
    seen = set()
    for x in items:
        assert x["id"] not in seen, f"duplicate id {x['id']}"
        seen.add(x["id"])
        assert x["category"] in CATEGORIES, f"{x['id']}: bad category"
        assert x["level"] in LEVELS, f"{x['id']}: bad level"
        assert x["url"].startswith("https://"), f"{x['id']}: url must be https"
        assert x["desc"].get("en"), f"{x['id']}: english description required"
    return items


CATALOG = load_catalog()
BY_ID = {x["id"]: x for x in CATALOG}


# ----------------------------------------------------------------------- state
def now() -> dt.datetime:
    return dt.datetime.now(UTC)


class Store:
    """Крошечное JSON-хранилище: пользователи, просмотры, одобренные спонсоры, черновик рассылки."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.data = {"users": {}, "views_week": {}, "approved_sponsors": [], "draft": None}
        if self.path.exists():
            try:
                self.data.update(json.loads(self.path.read_text("utf-8")))
            except json.JSONDecodeError:
                backup = self.path.with_suffix(".broken")
                self.path.replace(backup)
                log.error("state file is corrupted, moved to %s", backup)

    def save(self) -> None:
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False, indent=2), "utf-8")
        tmp.replace(self.path)


store = Store(DATA_FILE)


def get_user(uid: int) -> dict | None:
    return store.data["users"].get(str(uid))


def new_user(uid: int, lang: str) -> dict:
    user = {"lang": lang, "sub": False, "joined": now().isoformat()}
    store.data["users"][str(uid)] = user
    return user


def t(lang: str, key: str, **kw) -> str:
    table = STRINGS.get(lang) or STRINGS["en"]
    text = table.get(key) or STRINGS["en"][key]
    return text.format(name=html.escape(BOT_NAME), **kw)


def visible_tools() -> list[dict]:
    """Спонсорские записи видны только после одобрения владельцем (/approve_sponsor)."""
    approved = set(store.data["approved_sponsors"])
    return [x for x in CATALOG if not x.get("sponsor") or x["id"] in approved]


def tool_desc(tool: dict, lang: str) -> str:
    return tool["desc"].get(lang) or tool["desc"]["en"]


def tool_link(tool: dict) -> str:
    return tool.get("affiliate_url") or tool["url"]


# ------------------------------------------------------------------- keyboards
def btn(text: str, data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text, callback_data=data)


def kb_langs() -> InlineKeyboardMarkup:
    items = [btn(name, f"lang:{code}") for code, name in LANGS.items()]
    return InlineKeyboardMarkup([items[i : i + 2] for i in range(0, len(items), 2)])


def kb_menu(lang: str, subscribed: bool) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [btn(t(lang, "btn_find"), "cats")],
            [btn(t(lang, "btn_all"), "all")],
            [btn(t(lang, "btn_guides"), "guides")],
            [btn(t(lang, "btn_unsub" if subscribed else "btn_sub"), "sub:0" if subscribed else "sub:1")],
            [btn(t(lang, "btn_about"), "about"), btn(t(lang, "btn_lang"), "chlang")],
        ]
    )


def kb_back(lang: str, to: str = "menu") -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup([[btn(t(lang, "btn_back"), to)]])


def kb_cats(lang: str) -> InlineKeyboardMarkup:
    present = {x["category"] for x in visible_tools()}
    rows = [[btn(t(lang, f"cat_{c}"), f"cat:{c}")] for c in CATEGORIES if c in present]
    rows.append([btn(t(lang, "btn_back"), "menu")])
    return InlineKeyboardMarkup(rows)


def kb_tools(lang: str, tools: list[dict], origin: str, back_to: str) -> InlineKeyboardMarkup:
    rows = []
    for tool in tools:
        label = tool["name"]
        if tool.get("sponsor"):
            label += f" · {t(lang, 'sponsored_tag')}"
        rows.append([btn(label, f"tool:{tool['id']}:{origin}")])
    rows.append([btn(t(lang, "btn_back"), back_to)])
    return InlineKeyboardMarkup(rows)


def kb_tool(lang: str, tool: dict, back_to: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton(t(lang, "btn_open"), url=tool_link(tool))],
            [btn(t(lang, "btn_back"), back_to)],
        ]
    )


def tool_text(tool: dict, lang: str) -> str:
    esc = html.escape
    lines = [
        f"<b>{esc(tool['name'])}</b>",
        esc(tool_desc(tool, lang)),
        "",
        f"{t(lang, 'category')}: {esc(t(lang, 'cat_' + tool['category']))}",
        f"{t(lang, 'level')}: {t(lang, 'lvl_' + tool['level'])}",
        "",
        f"<i>{t(lang, 'pricing_note')}</i>",
        f"<i>{t(lang, 'disclaimer')}</i>",
    ]
    if tool.get("sponsor"):
        lines.append(f"<i>{t(lang, 'sponsored_note')}</i>")
    if tool.get("affiliate_url") or tool.get("sponsor"):
        lines.append(f"<i>{t(lang, 'affiliate_note')}</i>")
    return "\n".join(lines)


# --------------------------------------------------------------------- guides
def rich_html(text: str) -> str:
    """Экранирует текст и превращает **выделение** в <b>."""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", html.escape(text))


def guide_block(kind: str, value) -> str:
    if kind == "h":
        return f"<b>{html.escape(value)}</b>"
    if kind == "p":
        return rich_html(value)
    if kind == "ul":
        return "\n\n".join(f"• {rich_html(item)}" for item in value)
    return "\n\n".join(f"{n}. {rich_html(item)}" for n, item in enumerate(value, 1))


@functools.lru_cache(maxsize=None)
def guide_pages(slug: str, lang: str) -> tuple[str, ...]:
    """Режет гид на страницы по разделам, чтобы каждая влезала в одно сообщение."""
    g = GUIDES[slug]["lang"][lang]
    sections = [f"<b>{html.escape(g['title'])}</b>\n\n{html.escape(g['intro'])}"]
    for kind, value in g["blocks"]:
        if kind == "h":
            sections.append(guide_block(kind, value))
        else:
            sections[-1] += "\n\n" + guide_block(kind, value)
    pages, current = [], ""
    for section in sections:
        if current and len(current) + 2 + len(section) > PAGE_CHARS:
            pages.append(current)
            current = section
        else:
            current = f"{current}\n\n{section}" if current else section
    pages.append(current)
    return tuple(pages)


def kb_guides(lang: str) -> InlineKeyboardMarkup:
    rows = [[btn(g["short"].get(lang) or g["short"]["en"], f"gd:{slug}:0")] for slug, g in GUIDES.items()]
    rows.append([btn(t(lang, "btn_back"), "menu")])
    return InlineKeyboardMarkup(rows)


def guide_screen(lang: str, slug: str, page: str) -> tuple[str, InlineKeyboardMarkup]:
    pages = guide_pages(slug, lang)
    last = len(pages) - 1
    if page == "last":
        index = last
    else:
        try:
            index = min(max(int(page), 0), last)
        except ValueError:
            index = 0
    text = pages[index]
    if index == last:
        text += f"\n\n<i>{html.escape(GUIDE_UI[lang]['disclaimer'])} {t(lang, 'disclaimer')}</i>"

    rows = []
    nav = []
    if index > 0:
        nav.append(btn(t(lang, "btn_prev"), f"gd:{slug}:{index - 1}"))
    if last > 0:
        nav.append(btn(f"{index + 1}/{last + 1}", "noop"))
    if index < last:
        nav.append(btn(t(lang, "btn_next"), f"gd:{slug}:{index + 1}"))
    if nav:
        rows.append(nav)
    if index == last:  # инструменты из гида показываем в конце
        shown = visible_tools()
        for tool_id in GUIDES[slug]["tools"]:
            tool = BY_ID.get(tool_id)
            if tool is not None and tool in shown:
                rows.append([btn(tool["name"], f"tool:{tool_id}:g:{slug}")])
    rows.append([btn(t(lang, "btn_back"), "guides")])
    return text, InlineKeyboardMarkup(rows)


async def render(update: Update, text: str, markup: InlineKeyboardMarkup) -> None:
    query = update.callback_query
    try:
        if query:
            await query.edit_message_text(
                text, reply_markup=markup, parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW
            )
        else:
            await update.effective_message.reply_text(
                text, reply_markup=markup, parse_mode=ParseMode.HTML, link_preview_options=NO_PREVIEW
            )
    except BadRequest as exc:
        if "not modified" not in str(exc).lower():
            raise


# ------------------------------------------------------------- user handlers
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update.effective_user.id)
    if user is None:
        await render(update, LANG_PROMPT, kb_langs())
    else:
        await render(update, t(user["lang"], "welcome"), kb_menu(user["lang"], user["sub"]))


async def cmd_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update.effective_user.id)
    if user is None:
        await render(update, LANG_PROMPT, kb_langs())
    else:
        await render(update, t(user["lang"], "menu_title"), kb_menu(user["lang"], user["sub"]))


async def cmd_guides(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update.effective_user.id)
    if user is None:
        await render(update, LANG_PROMPT, kb_langs())
    else:
        await render(update, t(user["lang"], "pick_guide"), kb_guides(user["lang"]))


async def cmd_stop(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    user = get_user(update.effective_user.id)
    if user is None:
        return
    user["sub"] = False
    store.save()
    await render(update, t(user["lang"], "unsubscribed"), kb_menu(user["lang"], False))


async def on_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id
    kind, _, rest = query.data.partition(":")

    if kind == "noop":  # счётчик страниц «1/2»
        return

    if kind == "nl":
        await on_newsletter_button(update, ctx, rest)
        return

    if kind == "lang":
        if rest not in LANGS:
            return
        user = get_user(uid) or new_user(uid, rest)
        user["lang"] = rest
        store.save()
        await render(update, t(rest, "welcome"), kb_menu(rest, user["sub"]))
        return

    user = get_user(uid)
    if user is None:
        await render(update, LANG_PROMPT, kb_langs())
        return
    lang = user["lang"]

    if kind == "menu":
        await render(update, t(lang, "menu_title"), kb_menu(lang, user["sub"]))
    elif kind == "chlang":
        await render(update, LANG_PROMPT, kb_langs())
    elif kind == "cats":
        await render(update, t(lang, "pick_cat"), kb_cats(lang))
    elif kind == "cat":
        tools = [x for x in visible_tools() if x["category"] == rest]
        await render(update, t(lang, "pick_tool"), kb_tools(lang, tools, rest, "cats"))
    elif kind == "all":
        await render(update, t(lang, "all_title"), kb_tools(lang, visible_tools(), "all", "menu"))
    elif kind == "tool":
        tool_id, _, origin = rest.partition(":")
        tool = BY_ID.get(tool_id)
        if tool is None or tool not in visible_tools():
            return
        views = store.data["views_week"]
        views[tool_id] = views.get(tool_id, 0) + 1
        store.save()
        if origin == "all":
            back_to = "all"
        elif origin.startswith("g:") and origin[2:] in GUIDES:  # пришли из гида: вернёмся на его последнюю страницу
            back_to = f"gd:{origin[2:]}:last"
        else:
            back_to = f"cat:{tool['category']}"
        await render(update, tool_text(tool, lang), kb_tool(lang, tool, back_to))
    elif kind == "guides":
        await render(update, t(lang, "pick_guide"), kb_guides(lang))
    elif kind == "gd":
        slug, _, page = rest.partition(":")
        if slug not in GUIDES:
            return
        text, markup = guide_screen(lang, slug, page)
        await render(update, text, markup)
    elif kind == "sub":
        user["sub"] = rest == "1"
        store.save()
        text = t(lang, "subscribed" if user["sub"] else "unsubscribed")
        await render(update, text, kb_menu(lang, user["sub"]))
    elif kind == "about":
        await render(update, t(lang, "about"), kb_back(lang))


# ------------------------------------------------------------- admin handlers
def admin_only(fn):
    @functools.wraps(fn)
    async def wrapper(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
        if update.effective_user and update.effective_user.id in ADMIN_IDS:
            return await fn(update, ctx)

    return wrapper


def is_stale(tool: dict) -> bool:
    checked = tool.get("checked")
    if not checked:
        return True
    return (now() - dt.datetime.fromisoformat(checked).replace(tzinfo=UTC)).days > STALE_DAYS


def build_report() -> str:
    users = store.data["users"].values()
    week_ago = now() - dt.timedelta(days=7)
    new_week = sum(1 for u in users if dt.datetime.fromisoformat(u["joined"]) >= week_ago)
    subs = sum(1 for u in users if u.get("sub"))
    by_lang = Counter(u["lang"] for u in users)
    top = Counter(store.data["views_week"]).most_common(5)
    stale = [x["name"] for x in CATALOG if is_stale(x)]
    lines = [
        "📊 Отчёт по боту",
        f"Пользователей: {len(users)} (новых за неделю: {new_week})",
        f"Подписчиков на советы: {subs}",
        "По языкам: " + (", ".join(f"{k}: {v}" for k, v in by_lang.most_common()) or "пока никого"),
        "",
        "Топ инструментов за неделю: "
        + (", ".join(f"{BY_ID[k]['name']} ({v})" for k, v in top if k in BY_ID) or "нет просмотров"),
        f"Записей без свежей проверки (>{STALE_DAYS} дн.): {len(stale)}",
    ]
    if stale:
        lines.append("Проверить вручную: " + ", ".join(stale))
    return "\n".join(lines)


async def check_links() -> list[str]:
    """Возвращает список проблем. 401/403/429 считаем «жив, но не пускает бота»."""
    problems = []
    headers = {"User-Agent": "Mozilla/5.0 (compatible; ChainScoutLinkCheck/1.0)"}
    async with httpx.AsyncClient(follow_redirects=True, timeout=15, headers=headers) as client:
        for tool in CATALOG:
            try:
                resp = await client.get(tool["url"])
                if resp.status_code >= 400 and resp.status_code not in (401, 403, 429):
                    problems.append(f"{tool['name']}: HTTP {resp.status_code}")
            except httpx.HTTPError as exc:
                problems.append(f"{tool['name']}: {type(exc).__name__}")
    return problems


def count_recipients(lang: str) -> int:
    return sum(
        1
        for u in store.data["users"].values()
        if u.get("sub") and (lang == "all" or u["lang"] == lang)
    )


async def send_newsletter(ctx: ContextTypes.DEFAULT_TYPE, lang: str, text: str) -> tuple[int, int]:
    ok = failed = 0
    for uid, user in list(store.data["users"].items()):
        if not user.get("sub") or (lang != "all" and user["lang"] != lang):
            continue
        try:
            await ctx.bot.send_message(int(uid), f"{text}\n\n{t(user['lang'], 'nl_footer')}")
            ok += 1
        except Forbidden:  # пользователь заблокировал бота
            user["sub"] = False
            failed += 1
        except TelegramError:
            failed += 1
        await asyncio.sleep(0.05)  # укладываемся в лимит Telegram (~30 сообщений/сек)
    store.save()
    return ok, failed


@admin_only
async def cmd_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(build_report())


@admin_only
async def cmd_check(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    msg = await update.message.reply_text("Проверяю ссылки каталога…")
    problems = await check_links()
    await msg.edit_text("✅ Все ссылки отвечают." if not problems else "⚠️ Проблемы:\n" + "\n".join(problems))


@admin_only
async def cmd_draft(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    parts = (update.message.text or "").split(None, 2)
    if len(parts) < 3 or (parts[1] not in LANGS and parts[1] != "all"):
        await update.message.reply_text(
            "Формат: /draft <en|fr|id|vi|sw|all> <текст рассылки>\n"
            "Ничего не уйдёт, пока вы не нажмёте «Отправить» под предпросмотром."
        )
        return
    lang, text = parts[1], parts[2].strip()
    if len(text) > 3500:
        await update.message.reply_text("Текст слишком длинный (максимум 3500 символов).")
        return
    n = count_recipients(lang)
    store.data["draft"] = {"lang": lang, "text": text}
    store.save()
    markup = InlineKeyboardMarkup([[btn(f"✅ Отправить ({n})", "nl:ok"), btn("✖ Отмена", "nl:no")]])
    await update.message.reply_text(f"Предпросмотр. Адресаты: {lang}, {n} чел.\n\n{text}", reply_markup=markup)


async def on_newsletter_button(update: Update, ctx: ContextTypes.DEFAULT_TYPE, action: str) -> None:
    query = update.callback_query
    if query.from_user.id not in ADMIN_IDS:
        return
    draft = store.data.get("draft")
    if not draft:
        await query.edit_message_text("Черновика нет.")
        return
    store.data["draft"] = None  # сбрасываем до отправки, чтобы повторный клик не задвоил рассылку
    store.save()
    if action == "no":
        await query.edit_message_text("Черновик отменён.")
        return
    await query.edit_message_text("Отправляю…")
    ok, failed = await send_newsletter(ctx, draft["lang"], draft["text"])
    await query.edit_message_text(f"Готово: доставлено {ok}, не доставлено {failed}.")


async def _set_sponsor(update: Update, ctx: ContextTypes.DEFAULT_TYPE, approve: bool) -> None:
    tool = BY_ID.get(ctx.args[0]) if ctx.args else None
    if tool is None or not tool.get("sponsor"):
        sponsors = [x["id"] for x in CATALOG if x.get("sponsor")]
        await update.message.reply_text("Укажите id спонсорской записи. Доступны: " + (", ".join(sponsors) or "нет"))
        return
    approved = store.data["approved_sponsors"]
    if approve and tool["id"] not in approved:
        approved.append(tool["id"])
    if not approve and tool["id"] in approved:
        approved.remove(tool["id"])
    store.save()
    await update.message.reply_text(f"{tool['name']}: {'показывается' if approve else 'скрыт'}.")


@admin_only
async def cmd_approve_sponsor(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_sponsor(update, ctx, True)


@admin_only
async def cmd_revoke_sponsor(update: Update, ctx: ContextTypes.DEFAULT_TYPE) -> None:
    await _set_sponsor(update, ctx, False)


# ------------------------------------------------------------------- routines
async def notify_admins(ctx: ContextTypes.DEFAULT_TYPE, text: str) -> None:
    for admin in ADMIN_IDS:
        try:
            await ctx.bot.send_message(admin, text)
        except TelegramError:
            log.warning("cannot notify admin %s", admin)


async def daily_routine(ctx: ContextTypes.DEFAULT_TYPE) -> None:
    """Ежедневно: проверка ссылок. По понедельникам: недельный отчёт."""
    problems = await check_links()
    if problems:
        await notify_admins(ctx, "⚠️ Проверка ссылок каталога:\n" + "\n".join(problems))
    if now().weekday() == 0:
        await notify_admins(ctx, build_report())
        store.data["views_week"] = {}
        store.save()


# ----------------------------------------------------------------------- main
def main() -> None:
    token = os.getenv("BOT_TOKEN")
    if not token:
        raise SystemExit("Задайте BOT_TOKEN (токен от @BotFather), см. README.md")
    logging.basicConfig(format="%(asctime)s %(levelname)s %(name)s: %(message)s", level=logging.INFO)

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("menu", cmd_menu))
    app.add_handler(CommandHandler("guides", cmd_guides))
    app.add_handler(CommandHandler("stop", cmd_stop))
    app.add_handler(CommandHandler("stats", cmd_stats))
    app.add_handler(CommandHandler("check", cmd_check))
    app.add_handler(CommandHandler("draft", cmd_draft))
    app.add_handler(CommandHandler("approve_sponsor", cmd_approve_sponsor))
    app.add_handler(CommandHandler("revoke_sponsor", cmd_revoke_sponsor))
    app.add_handler(CallbackQueryHandler(on_button))

    hour, minute = (int(x) for x in ROUTINE_TIME.split(":"))
    app.job_queue.run_daily(daily_routine, time=dt.time(hour, minute, tzinfo=UTC), name="daily_routine")

    if not ADMIN_IDS:
        log.warning("ADMIN_IDS не задан: админ-команды и отчёты отключены")
    app.run_polling()


if __name__ == "__main__":
    main()
