"""
Management command: seed_data
Adds new products (Men / Women / Product/New-Arrivals) with brand data
and product reviews for all products.

Usage:
    python manage.py seed_data
    python manage.py seed_data --clear   # clear existing seeded data first
"""

from django.core.management.base import BaseCommand
from shopapp.models import Product, Men, Women, ProductReview
import random


# ─────────────────────────────────────────────────────────
#  REVIEW POOL
# ─────────────────────────────────────────────────────────
REVIEW_POOL = [
    # 5-star
    (5, "Absolutely stunning quality", "Received so many compliments on my first day wearing this. The stitching and fabric feel genuinely premium. Worth every rupee."),
    (5, "Perfect fit and finish", "Ordered based on the size chart and it fits perfectly. The colour matches the photo exactly. Shipping was fast too."),
    (5, "Exceeded expectations", "I was a bit hesitant buying online, but this completely blew me away. Museum-quality garment at a very fair price."),
    (5, "Goes with everything", "Versatile piece that slots right into my wardrobe. Wore it to a formal dinner and then to brunch—looked great both times."),
    (5, "My favourite purchase this year", "Bought three colours after falling in love with the first one. The fabric breathes well even in summer heat."),
    (5, "Luxury feel without the guilt", "Feels like a designer label but priced reasonably. The attention to detail on the seams is impressive."),
    (5, "Ordered twice already", "First one was a gift; liked it so much I bought one for myself. Friends keep asking where I got it."),
    (5, "Brilliant brand", "The brand never disappoints. Consistent sizing and top-tier fabric every single time I order."),
    # 4-star
    (4, "Really nice, minor sizing note", "Great product overall. Runs very slightly large so consider sizing down if you're between sizes."),
    (4, "Good value for the price", "Solid quality garment. The colour is a touch lighter than on screen but still looks great in person."),
    (4, "Happy with this purchase", "Comfortable to wear all day. Would love a few more colour options, but the overall quality is solid."),
    (4, "Well made and stylish", "Nice clean lines and the fabric feels good. Delivery took 3 days which is fine."),
    (4, "Pretty good", "Was sceptical but quality is genuinely good. Small thread at the hem but nothing a quick snip won't fix."),
    (4, "Recommend with slight caveat", "Material feels premium. Only docking one star because the size guide could be clearer."),
    # 3-star
    (3, "Decent but not extraordinary", "It's fine for everyday wear but nothing special. Fabric is average. Will probably reorder if they improve the material."),
    (3, "OK for the price", "Average quality—what you'd expect at this price point. Colour is accurate. Delivery was on time."),
    # 2-star
    (2, "Not what I expected", "The fabric feels a little thin compared to the photos. Might work as a layering piece but not as a standalone garment."),
    # 1-star
    (1, "Disappointed", "The stitching came loose after the first wash. Expected better from this brand. Will contact support."),
    # More 5-star reviews
    (5, "Gift-worthy packaging", "Even the packaging feels premium. Gave this as a birthday gift and the recipient was delighted."),
    (5, "Wore to a wedding", "Perfect for the occasion. Got stopped multiple times for compliments. This brand has earned a loyal customer."),
    (5, "Exactly as described", "No surprises—fits as expected, colour is accurate, material is great. Exactly what good online shopping should be."),
    (5, "Stylish and durable", "After 6 months of regular wear and multiple washes it still looks brand new. Incredible durability."),
    (5, "Timeless design", "Not a trend-chasing piece—this has a classic cut that will look sharp years from now."),
    (5, "Outstanding craftsmanship", "The stitching, lining, and overall finish put this well above typical online purchases. Truly premium."),
    (4, "Stylish pick", "Good quality fabric and the design is very trendy right now. Minor sizing inconsistency but nothing major."),
    (4, "Fast delivery, good product", "Arrived in 2 days. Quality is good and fits well. Would buy again."),
    (5, "Best in class", "I've bought from several fashion brands online. This beats them all on fit, fabric, and finishing."),
    (5, "Comfortable all day", "Wore this for a 10-hour work day—still comfortable by evening. Fabric breathes really well."),
    (4, "A solid choice", "Well constructed and looks exactly like the photo. Would be 5 stars if the delivery was a day faster."),
    (5, "Confidence booster", "Put this on and felt instantly more put-together. That's what great clothes do—effortlessly elevate your look."),
]

REVIEWER_NAMES = [
    "Arjun Mehta", "Priya Sharma", "Rohan Verma", "Sneha Patel",
    "Vikram Singh", "Ananya Iyer", "Rahul Gupta", "Kavya Nair",
    "Aditya Joshi", "Deepika Rao", "Karan Kapoor", "Pooja Desai",
    "Nikhil Tiwari", "Meera Bose", "Siddharth Reddy", "Divya Khanna",
    "Aakash Malhotra", "Riya Shetty", "Manish Chandra", "Shreya Pandey",
    "Harsh Agarwal", "Nisha Kulkarni", "Tushar Jain", "Sakshi Yadav",
    "Varun Bajaj", "Kritika Mishra", "Sameer Thakur", "Anjali Trivedi",
    "Yash Choudhary", "Simran Kohli", "Ayush Ghosh", "Bhavna Shah",
]

# ─────────────────────────────────────────────────────────
#  NEW PRODUCT DATA
# ─────────────────────────────────────────────────────────

# Men products — 16 new items across 8 brands
MEN_PRODUCTS = [
    # Nike
    {"name": "Nike Air Slim Jogger",       "brand": "Nike",           "price": 2499,  "discount": 10, "image": "Product/men1.jpg"},
    {"name": "Nike Pro Polo Shirt",        "brand": "Nike",           "price": 1899,  "discount": 5,  "image": "Product/men2_FsrEQwK.jpg"},
    # Adidas
    {"name": "Adidas Urban Hoodie",        "brand": "Adidas",         "price": 2999,  "discount": 15, "image": "Product/men2_W42Csea.jpg"},
    {"name": "Adidas Classic Track Pant",  "brand": "Adidas",         "price": 1799,  "discount": 10, "image": "Product/men3.jpg"},
    # Zara
    {"name": "Zara Slim Fit Blazer",       "brand": "Zara",           "price": 5499,  "discount": 0,  "image": "Product/men3_Y9dJNus.jpg"},
    {"name": "Zara Linen Casual Shirt",    "brand": "Zara",           "price": 2199,  "discount": 0,  "image": "Product/men1_7ElV4i8.jpg"},
    # Puma
    {"name": "Puma Street Runner Tee",     "brand": "Puma",           "price": 1299,  "discount": 20, "image": "Product/men4_eiIW7Kc.jpg"},
    {"name": "Puma Comfort Cargo Shorts",  "brand": "Puma",           "price": 1699,  "discount": 10, "image": "Product/men4_edGwcw1.jpg"},
    # Tommy Hilfiger
    {"name": "Tommy Oxford Button Shirt",  "brand": "Tommy Hilfiger", "price": 3499,  "discount": 0,  "image": "Product/men1.jpg"},
    {"name": "Tommy Heritage Chinos",      "brand": "Tommy Hilfiger", "price": 3999,  "discount": 5,  "image": "Product/men2_FsrEQwK.jpg"},
    # Calvin Klein
    {"name": "Calvin Klein Slim Jeans",    "brand": "Calvin Klein",   "price": 4299,  "discount": 10, "image": "Product/men3.jpg"},
    {"name": "Calvin Klein Crew Neck",     "brand": "Calvin Klein",   "price": 2599,  "discount": 0,  "image": "Product/men4_eiIW7Kc.jpg"},
    # Ralph Lauren
    {"name": "Ralph Lauren Polo Classic",  "brand": "Ralph Lauren",   "price": 3799,  "discount": 0,  "image": "Product/men1_7ElV4i8.jpg"},
    {"name": "Ralph Lauren Oxford Suit",   "brand": "Ralph Lauren",   "price": 12999, "discount": 5,  "image": "Product/men3_Y9dJNus.jpg"},
    # H&M
    {"name": "H&M Essential White Tee",    "brand": "H&M",            "price":  799,  "discount": 0,  "image": "Product/men2_W42Csea.jpg"},
    {"name": "H&M Denim Jacket",           "brand": "H&M",            "price": 2499,  "discount": 15, "image": "Product/men4_edGwcw1.jpg"},
]

# Women products — 16 new items across 8 brands
WOMEN_PRODUCTS = [
    # Zara
    {"name": "Zara Floral Midi Dress",     "brand": "Zara",           "price": 3299,  "discount": 10, "image": "Product/women1.jpg"},
    {"name": "Zara Linen Wide Trousers",   "brand": "Zara",           "price": 2499,  "discount": 0,  "image": "Product/women2.jpg"},
    # Mango
    {"name": "Mango Wrap Blouse",          "brand": "Mango",          "price": 2799,  "discount": 10, "image": "Product/women1_fWp47fp.jpg"},
    {"name": "Mango Pleated Skirt",        "brand": "Mango",          "price": 2199,  "discount": 5,  "image": "Product/women2_CbXZL9a.jpg"},
    # H&M
    {"name": "H&M Relaxed Kurti Set",      "brand": "H&M",            "price":  999,  "discount": 0,  "image": "Product/women4.jpg"},
    {"name": "H&M Printed Co-ord Set",     "brand": "H&M",            "price": 1799,  "discount": 15, "image": "Product/women5.jpg"},
    # Biba
    {"name": "Biba Anarkali Kurta",        "brand": "Biba",           "price": 1899,  "discount": 10, "image": "Product/women.jpg"},
    {"name": "Biba Embroidered Salwar",    "brand": "Biba",           "price": 2599,  "discount": 0,  "image": "Product/women4_T6hUzbv.jpg"},
    # Sabyasachi
    {"name": "Sabyasachi Heritage Saree",  "brand": "Sabyasachi",     "price": 35000, "discount": 0,  "image": "Product/women1.jpg"},
    {"name": "Sabyasachi Bridal Lehenga",  "brand": "Sabyasachi",     "price": 48000, "discount": 0,  "image": "Product/women2.jpg"},
    # Calvin Klein
    {"name": "Calvin Klein Bodycon Dress", "brand": "Calvin Klein",   "price": 5499,  "discount": 10, "image": "Product/women_x7dqAWq.jpg"},
    {"name": "Calvin Klein Crop Jacket",   "brand": "Calvin Klein",   "price": 6999,  "discount": 5,  "image": "Product/women1_fWp47fp.jpg"},
    # Manish Malhotra
    {"name": "MM Silk Embroidered Saree",  "brand": "Manish Malhotra","price": 28000, "discount": 0,  "image": "Product/women2_CbXZL9a.jpg"},
    {"name": "MM Fusion Palazzo Set",      "brand": "Manish Malhotra","price": 14999, "discount": 5,  "image": "Product/women4.jpg"},
    # Nike (women)
    {"name": "Nike Women's Jogger Set",    "brand": "Nike",           "price": 3299,  "discount": 15, "image": "Product/women5.jpg"},
    {"name": "Nike Pro Sports Bra",        "brand": "Nike",           "price": 1799,  "discount": 10, "image": "Product/women_x7dqAWq.jpg"},
]

# New Arrivals / General products — 14 items covering broad categories
NEW_ARRIVAL_PRODUCTS = [
    # Gucci
    {"name": "Gucci Monogram Jacket",      "brand": "Gucci",          "price": 42000, "discount": 0,  "image": "Product/upcoming1.jpg"},
    {"name": "Gucci Silk Scarf Top",       "brand": "Gucci",          "price": 18500, "discount": 0,  "image": "Product/upcoming2_IFVMgxG.jpg"},
    # Versace
    {"name": "Versace Baroque Print Shirt","brand": "Versace",        "price": 22000, "discount": 5,  "image": "Product/upcoming3.jpg"},
    # Prada
    {"name": "Prada Nylon Utility Vest",   "brand": "Prada",          "price": 31000, "discount": 0,  "image": "Product/upcoming4.jpg"},
    # Louis Vuitton
    {"name": "LV Monogram Overcoat",       "brand": "Louis Vuitton",  "price": 65000, "discount": 0,  "image": "Product/upcoming1_NQKNrsO.jpg"},
    # Dior
    {"name": "Dior Oblique Tracksuit",     "brand": "Dior",           "price": 38000, "discount": 0,  "image": "Product/upcoming2_L69k4Ig.jpg"},
    # Balenciaga
    {"name": "Balenciaga Oversized Tee",   "brand": "Balenciaga",     "price": 19999, "discount": 10, "image": "Product/upcoming3_kyisP3w.jpg"},
    {"name": "Balenciaga Speed Trainers",  "brand": "Balenciaga",     "price": 45000, "discount": 0,  "image": "Product/upcoming4_QZewpFQ.jpg"},
    # Armani
    {"name": "Armani Exchange Slim Suit",  "brand": "Armani",         "price": 24999, "discount": 5,  "image": "Product/upcoming1.jpg"},
    {"name": "Emporio Armani Polo",        "brand": "Emporio Armani", "price":  8999, "discount": 10, "image": "Product/upcoming3.jpg"},
    # Zara Kids / General
    {"name": "Zara Kids Party Outfit",     "brand": "Zara",           "price":  2499, "discount": 0,  "image": "Product/kids.jpg"},
    {"name": "Biba Kids Kurta Set",        "brand": "Biba",           "price":  1499, "discount": 10, "image": "Product/kids3.jpg"},
    # H&M new arrival gender-neutral
    {"name": "H&M Oversized Hoodie",       "brand": "H&M",            "price":  2199, "discount": 20, "image": "Product/upcoming2_IFVMgxG.jpg"},
    {"name": "H&M Unisex Graphic Tee",     "brand": "H&M",            "price":   899, "discount": 0,  "image": "Product/upcoming4.jpg"},
]


def pick_reviews(n: int, model_type: str, object_id: int):
    """Return a list of ProductReview dicts (not yet saved) for a product."""
    reviews = []
    pool = REVIEW_POOL[:]
    random.shuffle(pool)
    chosen = pool[:n]
    names_pool = REVIEWER_NAMES[:]
    random.shuffle(names_pool)
    for i, (rating, title, comment) in enumerate(chosen):
        reviews.append(dict(
            model_type=model_type,
            object_id=object_id,
            author_name=names_pool[i % len(names_pool)],
            rating=rating,
            title=title,
            comment=comment,
            is_verified=True,
            helpful_count=random.randint(0, 47),
        ))
    return reviews


class Command(BaseCommand):
    help = "Seed database with new products (Men/Women/New Arrivals) and reviews"

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Delete previously seeded products & reviews before inserting',
        )

    def handle(self, *args, **options):
        random.seed(42)  # reproducible

        if options['clear']:
            self.stdout.write(self.style.WARNING("Clearing previously seeded data..."))
            # Only delete reviews (safe — user-submitted reviews stay)
            ProductReview.objects.all().delete()
            self.stdout.write(self.style.SUCCESS("  Reviews cleared."))

        self.stdout.write(self.style.MIGRATE_HEADING("═" * 60))
        self.stdout.write(self.style.MIGRATE_HEADING("  STYLEVERSE — Seed Data"))
        self.stdout.write(self.style.MIGRATE_HEADING("═" * 60))

        # ── 1. Men Products ───────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n[1/3] Adding Men's Products..."))
        men_created = 0
        men_objects = []
        for p in MEN_PRODUCTS:
            obj, created = Men.objects.get_or_create(
                name=p["name"],
                brand=p["brand"],
                defaults={
                    "price":    p["price"],
                    "discount": p["discount"],
                    "image":    p["image"],
                    "stock":    random.randint(10, 60),
                }
            )
            men_objects.append(obj)
            if created:
                men_created += 1
                self.stdout.write(f"  ✓ [{obj.brand}] {obj.name} — ₹{obj.price}")
            else:
                self.stdout.write(f"  ~ Already exists: {obj.name}")
        self.stdout.write(self.style.SUCCESS(f"  → {men_created} new men's products added."))

        # ── 2. Women Products ─────────────────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n[2/3] Adding Women's Products..."))
        women_created = 0
        women_objects = []
        for p in WOMEN_PRODUCTS:
            obj, created = Women.objects.get_or_create(
                name=p["name"],
                brand=p["brand"],
                defaults={
                    "price":    p["price"],
                    "discount": p["discount"],
                    "image":    p["image"],
                    "stock":    random.randint(8, 50),
                }
            )
            women_objects.append(obj)
            if created:
                women_created += 1
                self.stdout.write(f"  ✓ [{obj.brand}] {obj.name} — ₹{obj.price}")
            else:
                self.stdout.write(f"  ~ Already exists: {obj.name}")
        self.stdout.write(self.style.SUCCESS(f"  → {women_created} new women's products added."))

        # ── 3. New Arrival / General Products ─────────────────
        self.stdout.write(self.style.HTTP_INFO("\n[3/3] Adding New Arrivals (General/Product)..."))
        product_created = 0
        product_objects = []
        for p in NEW_ARRIVAL_PRODUCTS:
            obj, created = Product.objects.get_or_create(
                name=p["name"],
                brand=p["brand"],
                defaults={
                    "price":    p["price"],
                    "discount": p["discount"],
                    "image":    p["image"],
                    "stock":    random.randint(5, 40),
                }
            )
            product_objects.append(obj)
            if created:
                product_created += 1
                self.stdout.write(f"  ✓ [{obj.brand}] {obj.name} — ₹{obj.price}")
            else:
                self.stdout.write(f"  ~ Already exists: {obj.name}")
        self.stdout.write(self.style.SUCCESS(f"  → {product_created} new arrival products added."))

        # ── 4. Add Reviews to ALL Products ────────────────────
        self.stdout.write(self.style.HTTP_INFO("\n[4/4] Adding Product Reviews..."))
        review_total = 0

        # Collect all existing + newly seeded products
        all_men    = list(Men.objects.all())
        all_women  = list(Women.objects.all())
        all_prods  = list(Product.objects.all())

        def seed_reviews_for(products, model_type):
            count = 0
            for prod in products:
                existing = ProductReview.objects.filter(
                    model_type=model_type, object_id=prod.pk
                ).count()
                if existing >= 3:
                    continue  # already has enough reviews
                n_reviews = random.randint(4, 8)  # each product gets 4-8 reviews
                review_dicts = pick_reviews(n_reviews, model_type, prod.pk)
                for rd in review_dicts:
                    ProductReview.objects.create(**rd)
                    count += 1
                self.stdout.write(
                    f"  ✓ {model_type}:{prod.pk} [{prod.brand}] {prod.name} — {n_reviews} reviews"
                )
            return count

        review_total += seed_reviews_for(all_men,   'men')
        review_total += seed_reviews_for(all_women, 'women')
        review_total += seed_reviews_for(all_prods, 'product')

        self.stdout.write(self.style.SUCCESS(f"  → {review_total} reviews added."))

        # ── Summary ───────────────────────────────────────────
        self.stdout.write(self.style.MIGRATE_HEADING("\n" + "═" * 60))
        self.stdout.write(self.style.SUCCESS(f"  DONE!"))
        self.stdout.write(f"  New Men's products   : {men_created}")
        self.stdout.write(f"  New Women's products : {women_created}")
        self.stdout.write(f"  New Arrival products : {product_created}")
        self.stdout.write(f"  Reviews added        : {review_total}")
        self.stdout.write(self.style.MIGRATE_HEADING("═" * 60 + "\n"))
