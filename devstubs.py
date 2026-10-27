"""Заглушки telegram и httpx, чтобы проверять бота без установленных библиотек.

Если библиотеки есть (pip install -r requirements.txt), заглушки не включаются
и тесты работают с настоящими классами.
"""
import sys
import types


def install_if_needed() -> bool:
    try:
        import httpx  # noqa: F401
        import telegram  # noqa: F401

        return False
    except ImportError:
        pass

    class InlineKeyboardButton:
        def __init__(self, text, url=None, callback_data=None, **kwargs):
            self.text, self.url, self.callback_data = text, url, callback_data

    class InlineKeyboardMarkup:
        def __init__(self, inline_keyboard):
            self.inline_keyboard = inline_keyboard

    class LinkPreviewOptions:
        def __init__(self, **kwargs):
            pass

    class Update:
        pass

    class TelegramError(Exception):
        pass

    class BadRequest(TelegramError):
        pass

    class Forbidden(TelegramError):
        pass

    class Dummy:
        def __init__(self, *args, **kwargs):
            pass

    telegram = types.ModuleType("telegram")
    telegram.InlineKeyboardButton = InlineKeyboardButton
    telegram.InlineKeyboardMarkup = InlineKeyboardMarkup
    telegram.LinkPreviewOptions = LinkPreviewOptions
    telegram.Update = Update

    constants = types.ModuleType("telegram.constants")
    constants.ParseMode = types.SimpleNamespace(HTML="HTML")

    error = types.ModuleType("telegram.error")
    error.TelegramError, error.BadRequest, error.Forbidden = TelegramError, BadRequest, Forbidden

    ext = types.ModuleType("telegram.ext")
    ext.Application = ext.CallbackQueryHandler = ext.CommandHandler = Dummy
    ext.ContextTypes = types.SimpleNamespace(DEFAULT_TYPE=object)

    httpx = types.ModuleType("httpx")
    httpx.HTTPError = type("HTTPError", (Exception,), {})
    httpx.AsyncClient = Dummy

    for name, module in {
        "telegram": telegram,
        "telegram.constants": constants,
        "telegram.error": error,
        "telegram.ext": ext,
        "httpx": httpx,
    }.items():
        sys.modules[name] = module
    return True
