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


if __name__ == "__main__":
    unittest.main()
