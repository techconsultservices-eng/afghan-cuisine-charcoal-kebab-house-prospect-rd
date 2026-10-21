import html as html_lib
import json
import pathlib
import re
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = pathlib.Path(__file__).resolve().parents[1]


def read_json_ld(source):
    marker = '<script type="application/ld+json">'
    blocks = []
    for section in source.split(marker)[1:]:
        block, closing, _ = section.partition("</script>")
        if closing:
            blocks.append(json.loads(block))
    return blocks


class RestaurantConversionExperienceTests(unittest.TestCase):
    def test_all_pages_show_a_labeled_call_for_pickup_in_the_header(self):
        for page in ("index.html", "menu.html", "about.html", "contact.html"):
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding="utf-8")
                self.assertIn('class="nav-phone"', html)
                self.assertIn("Call to order pickup", html)
                self.assertIn("(08) 8262 6574", html)

    def test_home_hero_offers_delivery_call_pickup_and_menu(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        hero = html.split('class="hero-actions"', 1)[1].split("</div>", 1)[0]
        self.assertIn("Order delivery on Uber Eats", hero)
        self.assertIn("Call to order pickup", hero)
        self.assertIn("View our menu", hero)

    def test_mobile_quick_order_bar_is_created_for_all_pages(self):
        js = (ROOT / "assets/js/main.js").read_text(encoding="utf-8")
        css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
        self.assertIn("initMobileOrderBar()", js)
        self.assertIn("mobile-order-bar", js)
        self.assertIn(".mobile-order-bar", css)
        self.assertIn("@media (max-width: 767px)", css)

    def test_contact_page_distinguishes_delivery_and_pickup(self):
        html = (ROOT / "contact.html").read_text(encoding="utf-8")
        self.assertIn("Delivery through Uber Eats", html)
        self.assertIn("Call to order pickup", html)
        self.assertIn('href="tel:+61882626574"', html)
        self.assertIn("Order delivery on Uber Eats", html)

    def test_warm_editorial_surfaces_and_subtle_geometric_detail_exist(self):
        css = (ROOT / "assets/css/style.css").read_text(encoding="utf-8")
        self.assertIn(".section-warm", css)
        self.assertIn(".section-warm h1", css)
        self.assertIn(".heritage-motif", css)
        self.assertIn("--sand:", css)

    def test_pages_dev_is_canonical_in_site_metadata_and_search_files(self):
        origin = "https://afghan-cuisine-charcoal-kebab-house-prospect-rd.pages.dev"
        legacy_host = "afghankebabhouse.com.au"
        for page in ("index.html", "menu.html", "about.html", "contact.html"):
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding="utf-8")
                self.assertIn(origin, html)
                self.assertNotIn(legacy_host, html)

        sitemap = (ROOT / "sitemap.xml").read_text(encoding="utf-8")
        for path in ("", "menu.html", "about.html", "contact.html"):
            self.assertIn(f"<loc>{origin}/{path}</loc>", sitemap)
        self.assertNotIn(legacy_host, sitemap)

        robots = (ROOT / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {origin}/sitemap.xml", robots)
        self.assertNotIn(legacy_host, robots)

        llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn(f"- Home: {origin}/", llms)
        self.assertNotIn(legacy_host, llms)

    def test_google_analytics_tag_is_installed_once_on_every_page(self):
        measurement_id = "G-53LRJNML03"
        script_url = f"https://www.googletagmanager.com/gtag/js?id={measurement_id}"
        for page in ("index.html", "menu.html", "about.html", "contact.html"):
            with self.subTest(page=page):
                html = (ROOT / page).read_text(encoding="utf-8")
                head = html.split("</head>", 1)[0]
                self.assertEqual(head.count(script_url), 1)
                self.assertEqual(head.count(f"gtag('config', '{measurement_id}')"), 1)
    def test_menu_items_are_available_in_the_initial_html(self):
        menu_html = (ROOT / "menu.html").read_text(encoding="utf-8")
        self.assertIn("<!-- STATIC_MENU_START -->", menu_html)
        self.assertIn("<!-- STATIC_MENU_END -->", menu_html)
        static_menu = menu_html.split("<!-- STATIC_MENU_START -->", 1)[1].split(
            "<!-- STATIC_MENU_END -->", 1
        )[0]
        menu_data = json.loads((ROOT / "menu.json").read_text(encoding="utf-8"))
        for item in menu_data["items"]:
            with self.subTest(item=item["name"]):
                self.assertIn(html_lib.escape(item["name"]), static_menu)
                self.assertIn(html_lib.escape(item["description"]), static_menu)

    def test_menu_html_has_no_trailing_whitespace(self):
        menu_html = (ROOT / "menu.html").read_text(encoding="utf-8")
        trailing = [line_number for line_number, line in enumerate(menu_html.splitlines(), 1) if line.rstrip() != line]
        self.assertEqual(trailing, [])

    def test_static_menu_can_be_checked_against_menu_json(self):
        renderer = ROOT / "scripts" / "render_static_menu.py"
        self.assertTrue(renderer.exists(), "static menu renderer is required to keep menu.html in sync")
        result = subprocess.run(
            [sys.executable, str(renderer), "--check"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_menu_javascript_preserves_server_rendered_fallback(self):
        js = (ROOT / "assets/js/menu.js").read_text(encoding="utf-8")
        lines = js.splitlines()
        self.assertIn("const hasStaticMenu = menuContent.querySelector('.menu-category') !== null;", js)
        for message in ("Loading menu…", "Unable to load menu."):
            index = next(i for i, line in enumerate(lines) if message in line)
            self.assertEqual(lines[index - 1].strip(), "if (!hasStaticMenu) {")

    def test_published_rating_matches_the_current_ubereats_listing(self):
        for page in ("index.html", "about.html"):
            with self.subTest(page=page):
                source = (ROOT / page).read_text(encoding="utf-8")
                for obsolete in ("4.6★", "4.6 rated", "rated 4.6 stars", "4.6 on uber eats"):
                    self.assertNotIn(obsolete, source.lower())
                self.assertIn("4.5", source)
                self.assertIn("1,500+", source)

    def test_menu_metadata_matches_pickup_and_delivery_channels(self):
        menu_html = (ROOT / "menu.html").read_text(encoding="utf-8")
        description = re.search(r'<meta name="description" content="([^"]+)"', menu_html)
        og_description = re.search(r'<meta property="og:description" content="([^"]+)"', menu_html)
        self.assertIsNotNone(description)
        self.assertIsNotNone(og_description)
        for content in (description.group(1).lower(), og_description.group(1).lower()):
            self.assertIn("uber eats", content)
            self.assertIn("pickup", content)
            self.assertNotIn("order in-store", content)

    def test_llms_file_matches_menu_and_pickup_ordering(self):
        llms = (ROOT / "llms.txt").read_text(encoding="utf-8").lower()
        self.assertIn("pickup orders are placed by phone", llms)
        self.assertNotIn("pickup via uber eats", llms)
        self.assertIn("tender lamb mince", llms)
        self.assertNotIn("minced beef", llms)

    def test_business_schema_is_consistent_and_does_not_claim_review_rich_results(self):
        origin = "https://afghan-cuisine-charcoal-kebab-house-prospect-rd.pages.dev/"
        for page in ("index.html", "menu.html", "about.html", "contact.html"):
            with self.subTest(page=page):
                source = (ROOT / page).read_text(encoding="utf-8")
                blocks = read_json_ld(source)
                restaurant = next(block for block in blocks if block.get("@type") == "Restaurant")
                self.assertEqual(restaurant.get("@id"), f"{origin}#restaurant")
                self.assertIn("geo", restaurant)
                self.assertTrue(restaurant.get("sameAs"))
                self.assertNotIn("aggregateRating", restaurant)
                self.assertIn('property="og:site_name"', source)

        homepage_blocks = read_json_ld((ROOT / "index.html").read_text(encoding="utf-8"))
        website = next((block for block in homepage_blocks if block.get("@type") == "WebSite"), None)
        self.assertIsNotNone(website)
        self.assertEqual(website.get("name"), "Afghan Cuisine & Charcoal Kebab House")
        self.assertEqual(website.get("url"), origin)

    def test_sitemap_has_canonical_pages_without_stale_crawl_hints(self):
        origin = "https://afghan-cuisine-charcoal-kebab-house-prospect-rd.pages.dev"
        root = ET.fromstring((ROOT / "sitemap.xml").read_text(encoding="utf-8"))
        namespace = {"sm": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        urls = [element.text for element in root.findall("sm:url/sm:loc", namespace)]
        self.assertEqual(
            set(urls),
            {f"{origin}/", f"{origin}/menu.html", f"{origin}/about.html", f"{origin}/contact.html"},
        )
        self.assertEqual(len(urls), 4)
        for tag in ("lastmod", "changefreq", "priority"):
            self.assertNotIn(f"<{tag}>", (ROOT / "sitemap.xml").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
