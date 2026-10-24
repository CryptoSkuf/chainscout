#!/usr/bin/env python3
"""Проверка собранного сайта: python3 check_site.py [папка_dist]

Проверяет парность тегов, ссылки между страницами, якоря, sitemap, hreflang, JSON-LD
и то, что на каждом языке показаны все инструменты. Код выхода 1, если что-то не так.
"""
import json
import sys
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

HERE = Path(__file__).resolve().parent
DIST = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "dist"
sys.path[:0] = [str(HERE), str(HERE.parent)]
from guides import GUIDE_UI, GUIDES  # noqa: E402
from locales import LANGS  # noqa: E402

VOID = {"meta", "link", "input", "br", "hr", "img", "circle", "path", "rect"}
errors: list[str] = []


def fail(msg: str) -> None:
    errors.append(msg)


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack, self.ids, self.hrefs = [], set(), []
        self.tools = 0
        self.h1 = 0
        self.jsonld, self._in_ld = [], False
        self.title = ""
        self._in_title = False
        self.meta = {}
        self.img_without_alt = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "id" in a:
            if a["id"] in self.ids:
                fail(f"дубликат id={a['id']}")
            self.ids.add(a["id"])
        if tag == "a" and "href" in a:
            self.hrefs.append(a["href"])
        if tag == "link" and a.get("rel") == "canonical":
            self.meta["canonical"] = a.get("href")
        if tag == "meta" and a.get("name") == "description":
            self.meta["description"] = a.get("content", "")
        if tag == "h1":
            self.h1 += 1
        if "data-tool" in a:
            self.tools += 1
        if tag == "script" and a.get("type") == "application/ld+json":
            self._in_ld = True
        if tag == "title":
            self._in_title = True
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        pass

    def handle_endtag(self, tag):
        if tag in VOID:
            return
        if tag == "title":
            self._in_title = False
        if tag == "script":
            self._in_ld = False
        if not self.stack or self.stack[-1] != tag:
            fail(f"неправильная вложенность: </{tag}>, ожидалось {self.stack[-1] if self.stack else 'ничего'}")
            if tag in self.stack:
                while self.stack and self.stack.pop() != tag:
                    pass
        else:
            self.stack.pop()

    def handle_data(self, data):
        if self._in_ld:
            self.jsonld.append(data)
        if self._in_title:
            self.title += data


def parse(path: Path) -> Page:
    p = Page()
    p.feed(path.read_text("utf-8"))
    p.close()
    if p.stack:
        fail(f"{path.relative_to(DIST)}: не закрыты теги {p.stack}")
    return p


def main() -> None:
    if not DIST.exists():
        sys.exit(f"нет папки {DIST}, сначала python3 build_site.py")

    catalog_path = next(p for p in (HERE / "catalog.json", HERE.parent / "catalog.json") if p.exists())
    catalog = json.loads(catalog_path.read_text("utf-8"))
    expected = len([x for x in catalog if not x.get("sponsor")])

    pages = {"index.html": parse(DIST / "index.html"), "404.html": parse(DIST / "404.html")}
    for lang in LANGS:
        pages[f"{lang}/index.html"] = parse(DIST / lang / "index.html")
        for slug in GUIDES:
            pages[f"{lang}/guides/{slug}/index.html"] = parse(DIST / lang / "guides" / slug / "index.html")

    for rel, page in pages.items():
        here = (DIST / rel).parent
        for href in page.hrefs:
            if href.startswith(("http://", "https://", "mailto:", "tel:")):
                continue
            if href.startswith("#"):
                if href[1:] not in page.ids:
                    fail(f"{rel}: нет якоря {href}")
                continue
            target = (DIST / href.lstrip("/")) if href.startswith("/") else (here / href)
            target = target.resolve()
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                fail(f"{rel}: битая ссылка {href}")

    for lang in LANGS:
        rel = f"{lang}/index.html"
        page = pages[rel]
        if page.tools != expected:
            fail(f"{rel}: инструментов {page.tools}, ожидалось {expected}")
        if page.h1 != 1:
            fail(f"{rel}: h1 должно быть одно, найдено {page.h1}")
        if not page.title.strip():
            fail(f"{rel}: пустой title")
        desc = page.meta.get("description", "")
        if not 60 <= len(desc) <= 200:
            fail(f"{rel}: длина description {len(desc)}")
        if not page.meta.get("canonical", "").endswith(f"/{lang}/"):
            fail(f"{rel}: canonical {page.meta.get('canonical')}")
        try:
            data = json.loads("".join(page.jsonld))
            if len(data["itemListElement"]) != expected:
                fail(f"{rel}: в JSON-LD {len(data['itemListElement'])} элементов")
        except Exception as exc:  # noqa: BLE001
            fail(f"{rel}: JSON-LD не читается ({exc})")
        text = (DIST / rel).read_text("utf-8")
        for code in LANGS:
            if f'hreflang="{code}"' not in text:
                fail(f"{rel}: нет hreflang={code}")
        if 'hreflang="x-default"' not in text:
            fail(f"{rel}: нет hreflang=x-default")

    # ---- данные гидов: одинаковая структура на всех языках, существующие инструменты
    ids = {x["id"] for x in catalog}
    assert set(GUIDE_UI) == set(LANGS), "GUIDE_UI: языки не совпадают"
    for slug, guide in GUIDES.items():
        if set(guide["lang"]) != set(LANGS):
            fail(f"гид {slug}: языки {sorted(guide['lang'])}")
            continue
        for tool_id in guide["tools"]:
            if tool_id not in ids:
                fail(f"гид {slug}: нет инструмента {tool_id} в catalog.json")
        shape = [(k, len(v) if isinstance(v, list) else 0) for k, v in guide["lang"]["en"]["blocks"]]
        for lang, g in guide["lang"].items():
            if [(k, len(v) if isinstance(v, list) else 0) for k, v in g["blocks"]] != shape:
                fail(f"гид {slug}/{lang}: структура блоков не совпадает с английской")
            texts = [g["title"], g["description"], g["intro"]]
            for kind, value in g["blocks"]:
                texts += value if isinstance(value, list) else [value]
            for text in texts:
                if not text.strip():
                    fail(f"гид {slug}/{lang}: пустой текст")
                if text.count("**") % 2:
                    fail(f"гид {slug}/{lang}: непарное ** в «{text[:40]}…»")

    # ---- страницы гидов
    for slug in GUIDES:
        for lang in LANGS:
            rel = f"{lang}/guides/{slug}/index.html"
            page = pages[rel]
            text = (DIST / rel).read_text("utf-8")
            if page.h1 != 1:
                fail(f"{rel}: h1 должно быть одно, найдено {page.h1}")
            if not page.title.strip():
                fail(f"{rel}: пустой title")
            desc = page.meta.get("description", "")
            if not 60 <= len(desc) <= 200:
                fail(f"{rel}: длина description {len(desc)}")
            if not page.meta.get("canonical", "").endswith(f"/{lang}/guides/{slug}/"):
                fail(f"{rel}: canonical {page.meta.get('canonical')}")
            for code in LANGS:
                if f'hreflang="{code}" href="' not in text:
                    fail(f"{rel}: нет hreflang={code}")
            if 'hreflang="x-default"' not in text:
                fail(f"{rel}: нет hreflang=x-default")
            try:
                if json.loads("".join(page.jsonld))["@type"] != "Article":
                    fail(f"{rel}: JSON-LD не Article")
            except Exception as exc:  # noqa: BLE001
                fail(f"{rel}: JSON-LD не читается ({exc})")
            if page.tools != len(GUIDES[slug]["tools"]):
                fail(f"{rel}: карточек инструментов {page.tools}, ожидалось {len(GUIDES[slug]['tools'])}")
            if "**" in text:
                fail(f"{rel}: в HTML остались символы **")
        # каждая языковая главная ссылается на гид
    for lang in LANGS:
        if "guides/check-token-scams/" not in (DIST / lang / "index.html").read_text("utf-8"):
            fail(f"{lang}/index.html: нет ссылки на гид о скаме")

    expected_urls = len(LANGS) + 1 + len(GUIDES) * len(LANGS)
    ns = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
    urls = ET.parse(DIST / "sitemap.xml").getroot().findall("s:url", ns)
    if len(urls) != expected_urls:
        fail(f"sitemap: {len(urls)} адресов, ожидалось {expected_urls}")
    robots = (DIST / "robots.txt").read_text("utf-8")
    if "Sitemap:" not in robots:
        fail("robots.txt без Sitemap")

    if errors:
        print("ОШИБКИ:")
        for e in dict.fromkeys(errors):
            print(" -", e)
        sys.exit(1)
    print(
        f"OK: {len(pages)} страниц, {expected} инструментов и {len(GUIDES)} гидов на каждом из {len(LANGS)} языков, "
        "sitemap и ссылки в порядке"
    )


if __name__ == "__main__":
    main()
