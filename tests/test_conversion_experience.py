import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]


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


if __name__ == "__main__":
    unittest.main()
