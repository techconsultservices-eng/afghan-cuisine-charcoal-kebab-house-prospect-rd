#!/usr/bin/env python3
"""Generate the static, crawlable menu fallback from the unchanged menu.json."""

from __future__ import annotations

import argparse
import json
import re
import textwrap
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MENU_JSON = ROOT / "menu.json"
MENU_HTML = ROOT / "menu.html"
START_MARKER = "<!-- STATIC_MENU_START -->"
END_MARKER = "<!-- STATIC_MENU_END -->"

CATEGORY_DESCRIPTIONS = {
    "Featured": "Our most-loved dishes — signature charcoal-grilled kebabs and traditional Afghan mains.",
    "Desserts": "A sweet finish to your Afghan dining experience.",
    "Mains": "Heartier dishes from the Afghan table.",
    "Combos": "Great value combination meals for every appetite.",
    "Beverages": "Drinks to accompany your meal.",
}


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]", "", re.sub(r"\s+", "-", value.lower()))


def render_card(item: dict[str, str]) -> str:
    name = escape(item["name"])
    image = item.get("image", "").strip()
    if image:
        image_markup = (
            f'<img src="{escape(image)}" '
            f'alt="{escape(item["name"] + " — Afghan Cuisine and Charcoal Kebab House")}" '
            'loading="lazy">'
        )
    else:
        image_markup = (
            '<div class="dish-card-placeholder">'
            '<span>Photo coming soon</span>'
            '</div>'
        )

    return f'''<article class="dish-card">
  <div class="dish-card-img">{image_markup}</div>
  <div class="dish-card-body">
    <p class="dish-card-name">{name}</p>
    <p class="dish-card-desc">{escape(item["description"])}</p>
    <p class="dish-card-price">{escape(item["price"])}</p>
  </div>
</article>'''


def render_static_menu(menu_data: dict) -> str:
    items = menu_data["items"]
    by_name = {item["name"]: item for item in items}
    sections = []

    for category in menu_data["categories"]:
        if category == "Featured":
            category_items = [by_name[name] for name in menu_data.get("featured", []) if name in by_name]
        else:
            category_items = [item for item in items if item["category"] == category]

        description = CATEGORY_DESCRIPTIONS.get(category, "")
        description_markup = f"      <p>{escape(description)}</p>\n" if description else ""
        if category_items:
            cards_markup = "\n".join(render_card(item) for item in category_items)
            items_markup = f'<div class="menu-grid">\n{cards_markup}\n</div>'
        else:
            items_markup = (
                '<p style="color: var(--parchment-dim); font-style: italic; padding: 20px 0;">'
                "More dishes coming soon — ask our team about today's specials."
                "</p>"
            )

        sections.append(
            f'''<section class="menu-category section active" id="cat-{slugify(category)}">
  <div class="container">
    <div class="menu-category-header">
      <h2>{escape(category)}</h2>
{description_markup}    </div>
    {items_markup}
  </div>
</section>'''
        )

    return "\n\n".join(sections)


def update_menu_html(markup: str, check_only: bool) -> bool:
    source = MENU_HTML.read_text(encoding="utf-8")
    start = source.index(START_MARKER) + len(START_MARKER)
    end = source.index(END_MARKER, start)
    current = textwrap.dedent(source[start:end]).strip()
    expected = textwrap.dedent(markup).strip()

    if check_only:
        if current != expected:
            print("Static menu is out of sync with menu.json; run scripts/render_static_menu.py --write.")
            return False
        print("Static menu is synchronized with menu.json.")
        return True

    replacement = "\n" + textwrap.indent(markup, "      ") + "\n    "
    MENU_HTML.write_text(source[:start] + replacement + source[end:], encoding="utf-8")
    print("Generated static menu from menu.json without changing menu data.")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="fail if menu.html is out of sync")
    mode.add_argument("--write", action="store_true", help="write the generated fallback into menu.html")
    args = parser.parse_args()

    menu_data = json.loads(MENU_JSON.read_text(encoding="utf-8"))
    markup = render_static_menu(menu_data)
    return 0 if update_menu_html(markup, check_only=args.check) else 1


if __name__ == "__main__":
    raise SystemExit(main())
