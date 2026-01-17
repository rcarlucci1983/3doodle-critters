"""
3Doodle Critters Inventory Manager
==================================
A utility to manage shop inventory - add items with pictures, prices, and descriptions.
"""

import json
import os
import sys
import uuid
from pathlib import Path

# Paths
SCRIPT_DIR = Path(__file__).parent
INVENTORY_FILE = SCRIPT_DIR / "inventory.json"
IMAGES_DIR = SCRIPT_DIR / "images"
WEBSITE_FILE = SCRIPT_DIR / "index.html"

# Ensure images directory exists
IMAGES_DIR.mkdir(exist_ok=True)

def load_inventory():
    """Load inventory from JSON file."""
    if INVENTORY_FILE.exists():
        with open(INVENTORY_FILE, 'r') as f:
            return json.load(f)
    return {"items": [], "google_drive_folder_id": ""}

def save_inventory(inventory, update_website=True):
    """Save inventory to JSON file and optionally regenerate website."""
    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=2)

    if update_website:
        # Auto-regenerate website
        generate_website_silent(inventory)

def generate_item_id():
    """Generate a unique item ID."""
    return str(uuid.uuid4())[:8]

def list_items(inventory):
    """Display all items in inventory."""
    items = inventory.get("items", [])
    if not items:
        print("\n  No items in inventory yet.\n")
        return

    print("\n" + "=" * 60)
    print("  CURRENT INVENTORY")
    print("=" * 60)
    for i, item in enumerate(items, 1):
        status = "SOLD" if item.get("sold", False) else "Available"
        print(f"\n  [{i}] {item['title']}")
        print(f"      ID: {item['id']}")
        print(f"      Price: ${item['price']:.2f}")
        print(f"      Status: {status}")
        print(f"      Description: {item['description'][:50]}..." if len(item.get('description', '')) > 50 else f"      Description: {item.get('description', 'N/A')}")
        print(f"      Image: {item.get('image', 'No image')}")
    print("\n" + "=" * 60 + "\n")

def add_item(inventory):
    """Add a new item to inventory."""
    print("\n" + "=" * 60)
    print("  ADD NEW ITEM")
    print("=" * 60)

    # Get item details
    title = input("\n  Enter item title: ").strip()
    if not title:
        print("  Title cannot be empty. Cancelled.")
        return

    description = input("  Enter description: ").strip()

    while True:
        try:
            price = float(input("  Enter price (e.g., 5.00): $").strip())
            if price < 0:
                print("  Price must be positive.")
                continue
            break
        except ValueError:
            print("  Invalid price. Please enter a number.")

    # Image options
    print("\n  Image options:")
    print("    [1] Enter local image path")
    print("    [2] Enter image filename (if already in images folder)")
    print("    [3] Skip image for now")

    image_choice = input("\n  Choose option (1-3): ").strip()
    image_filename = None

    if image_choice == "1":
        image_path = input("  Enter full path to image: ").strip().strip('"')
        if os.path.exists(image_path):
            # Copy image to images folder
            ext = Path(image_path).suffix.lower()
            if ext == '.heic':
                # Convert HEIC to JPG
                try:
                    from PIL import Image
                    import pillow_heif
                    pillow_heif.register_heif_opener()

                    img = Image.open(image_path)
                    image_filename = f"{generate_item_id()}.jpg"
                    output_path = IMAGES_DIR / image_filename
                    img.convert('RGB').save(output_path, 'JPEG', quality=85)
                    print(f"  Converted and saved as: {image_filename}")
                except Exception as e:
                    print(f"  Error converting HEIC: {e}")
                    image_filename = None
            else:
                # Copy as-is
                import shutil
                image_filename = f"{generate_item_id()}{ext}"
                shutil.copy(image_path, IMAGES_DIR / image_filename)
                print(f"  Copied as: {image_filename}")
        else:
            print("  File not found. Skipping image.")

    elif image_choice == "2":
        image_filename = input("  Enter filename: ").strip()
        if not (IMAGES_DIR / image_filename).exists():
            print(f"  Warning: {image_filename} not found in images folder.")
            confirm = input("  Continue anyway? (y/n): ").strip().lower()
            if confirm != 'y':
                image_filename = None

    # Create item
    item = {
        "id": generate_item_id(),
        "title": title,
        "description": description,
        "price": price,
        "image": image_filename,
        "sold": False
    }

    inventory["items"].append(item)
    save_inventory(inventory)

    print(f"\n  Item '{title}' added successfully!")
    print(f"  Item ID: {item['id']}\n")

def edit_item(inventory):
    """Edit an existing item."""
    items = inventory.get("items", [])
    if not items:
        print("\n  No items to edit.\n")
        return

    list_items(inventory)

    try:
        choice = int(input("  Enter item number to edit (0 to cancel): "))
        if choice == 0:
            return
        if choice < 1 or choice > len(items):
            print("  Invalid selection.")
            return
    except ValueError:
        print("  Invalid input.")
        return

    item = items[choice - 1]
    print(f"\n  Editing: {item['title']}")
    print("  (Press Enter to keep current value)\n")

    new_title = input(f"  Title [{item['title']}]: ").strip()
    if new_title:
        item['title'] = new_title

    new_desc = input(f"  Description [{item['description'][:30]}...]: ").strip()
    if new_desc:
        item['description'] = new_desc

    new_price = input(f"  Price [${item['price']:.2f}]: $").strip()
    if new_price:
        try:
            item['price'] = float(new_price)
        except ValueError:
            print("  Invalid price, keeping original.")

    new_image = input(f"  Image [{item.get('image', 'None')}]: ").strip()
    if new_image:
        item['image'] = new_image

    save_inventory(inventory)
    print(f"\n  Item updated successfully!\n")

def remove_item(inventory):
    """Remove an item from inventory."""
    items = inventory.get("items", [])
    if not items:
        print("\n  No items to remove.\n")
        return

    list_items(inventory)

    try:
        choice = int(input("  Enter item number to remove (0 to cancel): "))
        if choice == 0:
            return
        if choice < 1 or choice > len(items):
            print("  Invalid selection.")
            return
    except ValueError:
        print("  Invalid input.")
        return

    item = items[choice - 1]
    confirm = input(f"  Are you sure you want to remove '{item['title']}'? (y/n): ").strip().lower()

    if confirm == 'y':
        items.pop(choice - 1)
        save_inventory(inventory)
        print(f"\n  Item removed successfully!\n")
    else:
        print("  Cancelled.\n")

def toggle_sold(inventory):
    """Toggle sold status of an item."""
    items = inventory.get("items", [])
    if not items:
        print("\n  No items in inventory.\n")
        return

    list_items(inventory)

    try:
        choice = int(input("  Enter item number to toggle sold status (0 to cancel): "))
        if choice == 0:
            return
        if choice < 1 or choice > len(items):
            print("  Invalid selection.")
            return
    except ValueError:
        print("  Invalid input.")
        return

    item = items[choice - 1]
    item['sold'] = not item.get('sold', False)
    status = "SOLD" if item['sold'] else "Available"
    save_inventory(inventory)
    print(f"\n  '{item['title']}' marked as: {status}\n")

def generate_website_silent(inventory):
    """Generate the website HTML silently (no output)."""
    _generate_website_html(inventory)

def generate_website(inventory):
    """Generate the website HTML from inventory (with output)."""
    _generate_website_html(inventory)
    items = inventory.get("items", [])
    print(f"\n  Website updated: {WEBSITE_FILE}")
    print(f"  Total items: {len(items)}\n")

def _generate_website_html(inventory):
    """Internal function to generate the website HTML."""
    items = inventory.get("items", [])

    # Generate product cards HTML
    products_html = ""
    for item in items:
        sold_class = "sold" if item.get('sold', False) else ""
        sold_badge = '<span class="sold-badge">SOLD</span>' if item.get('sold', False) else ""

        if item.get('image'):
            image_html = f'<img src="images/{item["image"]}" alt="{item["title"]}">'
        else:
            image_html = '<div class="no-image">No Image</div>'

        products_html += f'''
                <div class="product-card {sold_class}">
                    <div class="product-image">
                        {image_html}
                        {sold_badge}
                    </div>
                    <div class="product-info">
                        <h3>{item["title"]}</h3>
                        <p>{item["description"]}</p>
                        <span class="price">${item["price"]:.2f}</span>
                    </div>
                </div>
'''

    if not products_html:
        products_html = '''
                <div class="no-products">
                    <p>New items coming soon! Check back later.</p>
                </div>
'''

    # Full HTML template
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>3Doodle Critters | Handmade 3D Pen Art</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Fredoka+One&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --purple: #9B59B6;
            --purple-dark: #7D3C98;
            --teal: #1ABC9C;
            --teal-dark: #16A085;
            --pink: #FF6B9D;
            --pink-light: #FFB8D0;
            --yellow: #FFDC50;
            --cream: #FFF9F0;
            --text-dark: #2C3E50;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: 'Nunito', sans-serif;
            background: var(--cream);
            color: var(--text-dark);
            line-height: 1.6;
        }}

        .bg-decoration {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: -1;
            overflow: hidden;
        }}

        .bg-decoration::before,
        .bg-decoration::after {{
            content: '';
            position: absolute;
            border-radius: 50%;
            opacity: 0.1;
        }}

        .bg-decoration::before {{
            width: 400px;
            height: 400px;
            background: var(--purple);
            top: -100px;
            right: -100px;
        }}

        .bg-decoration::after {{
            width: 300px;
            height: 300px;
            background: var(--teal);
            bottom: -50px;
            left: -50px;
        }}

        header {{
            background: linear-gradient(135deg, var(--pink) 0%, var(--purple) 50%, var(--teal) 100%);
            padding: 2rem 1rem;
            text-align: center;
            position: relative;
            overflow: hidden;
        }}

        header::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.1'%3E%3Ccircle cx='30' cy='30' r='4'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E");
        }}

        .logo {{
            position: relative;
            z-index: 1;
        }}

        h1 {{
            font-family: 'Fredoka One', cursive;
            font-size: 3rem;
            color: white;
            text-shadow: 3px 3px 0 rgba(0,0,0,0.2);
            margin-bottom: 0.5rem;
        }}

        .tagline {{
            font-size: 1.3rem;
            color: white;
            opacity: 0.95;
            font-weight: 600;
        }}

        nav {{
            background: white;
            padding: 1rem;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            position: sticky;
            top: 0;
            z-index: 100;
        }}

        nav ul {{
            list-style: none;
            display: flex;
            justify-content: center;
            flex-wrap: wrap;
            gap: 1rem;
        }}

        nav a {{
            text-decoration: none;
            color: var(--purple-dark);
            font-weight: 700;
            padding: 0.5rem 1.5rem;
            border-radius: 25px;
            transition: all 0.3s ease;
        }}

        nav a:hover {{
            background: var(--purple);
            color: white;
        }}

        main {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem 1rem;
        }}

        section {{
            margin-bottom: 4rem;
        }}

        h2 {{
            font-family: 'Fredoka One', cursive;
            font-size: 2.2rem;
            color: var(--purple);
            text-align: center;
            margin-bottom: 2rem;
            position: relative;
        }}

        h2::after {{
            content: '';
            display: block;
            width: 80px;
            height: 4px;
            background: linear-gradient(90deg, var(--teal), var(--pink));
            margin: 0.5rem auto 0;
            border-radius: 2px;
        }}

        .welcome {{
            background: white;
            border-radius: 20px;
            padding: 2.5rem;
            text-align: center;
            box-shadow: 0 5px 20px rgba(155, 89, 182, 0.15);
            border: 3px solid var(--pink-light);
        }}

        .welcome p {{
            font-size: 1.2rem;
            max-width: 700px;
            margin: 0 auto;
        }}

        .welcome .highlight {{
            color: var(--purple);
            font-weight: 700;
        }}

        .products-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 2rem;
        }}

        .product-card {{
            background: white;
            border-radius: 20px;
            overflow: hidden;
            box-shadow: 0 5px 20px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }}

        .product-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(155, 89, 182, 0.2);
        }}

        .product-card.sold {{
            opacity: 0.7;
        }}

        .product-image {{
            width: 100%;
            height: 250px;
            background: linear-gradient(135deg, var(--pink-light) 0%, #E8DAEF 100%);
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }}

        .product-image img {{
            width: 100%;
            height: 100%;
            object-fit: cover;
        }}

        .product-image .no-image {{
            color: var(--purple);
            font-weight: 600;
        }}

        .sold-badge {{
            position: absolute;
            top: 15px;
            right: -35px;
            background: var(--pink);
            color: white;
            padding: 5px 40px;
            font-weight: 700;
            transform: rotate(45deg);
            font-size: 0.9rem;
        }}

        .product-info {{
            padding: 1.5rem;
        }}

        .product-info h3 {{
            font-family: 'Fredoka One', cursive;
            color: var(--teal-dark);
            font-size: 1.3rem;
            margin-bottom: 0.5rem;
        }}

        .product-info p {{
            color: #666;
            margin-bottom: 1rem;
            min-height: 3rem;
        }}

        .price {{
            font-family: 'Fredoka One', cursive;
            font-size: 1.5rem;
            color: var(--pink);
        }}

        .no-products {{
            text-align: center;
            padding: 3rem;
            color: var(--purple);
            font-size: 1.2rem;
        }}

        .order-steps {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 2rem;
        }}

        .step {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            border-top: 5px solid var(--teal);
        }}

        .step-number {{
            width: 50px;
            height: 50px;
            background: linear-gradient(135deg, var(--purple), var(--pink));
            color: white;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-family: 'Fredoka One', cursive;
            font-size: 1.5rem;
            margin: 0 auto 1rem;
        }}

        .step h3 {{
            color: var(--purple-dark);
            margin-bottom: 0.5rem;
        }}

        .payment-options {{
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 1.5rem;
            margin-top: 1.5rem;
        }}

        .payment-option {{
            background: white;
            padding: 1.5rem 2rem;
            border-radius: 15px;
            box-shadow: 0 3px 15px rgba(0,0,0,0.08);
            text-align: center;
            min-width: 150px;
        }}

        .payment-option .icon {{
            font-size: 2.5rem;
            margin-bottom: 0.5rem;
        }}

        .payment-option h4 {{
            color: var(--teal-dark);
            font-weight: 700;
        }}

        .delivery-options {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
            gap: 2rem;
            margin-top: 1.5rem;
        }}

        .delivery-card {{
            background: white;
            border-radius: 20px;
            padding: 2rem;
            text-align: center;
            box-shadow: 0 5px 20px rgba(0,0,0,0.08);
            border-left: 5px solid var(--pink);
        }}

        .delivery-card .icon {{
            font-size: 3rem;
            margin-bottom: 1rem;
        }}

        .delivery-card h3 {{
            color: var(--purple-dark);
            margin-bottom: 0.5rem;
        }}

        .contact-box {{
            background: linear-gradient(135deg, var(--purple) 0%, var(--teal) 100%);
            border-radius: 20px;
            padding: 3rem;
            text-align: center;
            color: white;
        }}

        .contact-box h2 {{
            color: white;
        }}

        .contact-box h2::after {{
            background: white;
        }}

        .contact-box p {{
            font-size: 1.2rem;
            margin-bottom: 1.5rem;
        }}

        .contact-email {{
            display: inline-block;
            background: white;
            color: var(--purple-dark);
            font-family: 'Fredoka One', cursive;
            font-size: 1.3rem;
            padding: 1rem 2rem;
            border-radius: 30px;
            text-decoration: none;
            transition: transform 0.3s ease;
        }}

        .contact-email:hover {{
            transform: scale(1.05);
        }}

        footer {{
            background: var(--text-dark);
            color: white;
            text-align: center;
            padding: 2rem;
            margin-top: 2rem;
        }}

        footer p {{
            opacity: 0.8;
        }}

        .footer-hearts {{
            font-size: 1.5rem;
            margin-bottom: 0.5rem;
        }}

        @media (max-width: 768px) {{
            h1 {{
                font-size: 2rem;
            }}

            .tagline {{
                font-size: 1rem;
            }}

            h2 {{
                font-size: 1.8rem;
            }}

            nav ul {{
                gap: 0.5rem;
            }}

            nav a {{
                padding: 0.4rem 1rem;
                font-size: 0.9rem;
            }}
        }}
    </style>
</head>
<body>
    <div class="bg-decoration"></div>

    <header>
        <div class="logo">
            <h1>3Doodle Critters</h1>
            <p class="tagline">Handmade 3D Pen Art</p>
        </div>
    </header>

    <nav>
        <ul>
            <li><a href="#welcome">Home</a></li>
            <li><a href="#products">Shop</a></li>
            <li><a href="#how-to-order">How to Order</a></li>
            <li><a href="#payment">Payment</a></li>
            <li><a href="#contact">Contact</a></li>
        </ul>
    </nav>

    <main>
        <section id="welcome" class="welcome">
            <h2>Welcome!</h2>
            <p>
                Hi! I'm <span class="highlight">Mira</span>, and I make cute animals and fun creations using a <span class="highlight">3D printing pen</span>!
                Each piece is carefully crafted by hand, making every 3Doodle unique and special.
                Check out my critters below and take one home today!
            </p>
        </section>

        <section id="products">
            <h2>My Creations</h2>
            <div class="products-grid">
{products_html}
            </div>
        </section>

        <section id="how-to-order">
            <h2>How to Order</h2>
            <div class="order-steps">
                <div class="step">
                    <div class="step-number">1</div>
                    <h3>Pick Your Critters</h3>
                    <p>Browse the shop and decide which 3Doodles you'd like!</p>
                </div>
                <div class="step">
                    <div class="step-number">2</div>
                    <h3>Send a Message</h3>
                    <p>Email us with what you want to order and how you'd like to receive it.</p>
                </div>
                <div class="step">
                    <div class="step-number">3</div>
                    <h3>Get Your Critters!</h3>
                    <p>Pick up locally or have them shipped to you!</p>
                </div>
            </div>
        </section>

        <section id="delivery">
            <h2>Delivery Options</h2>
            <div class="delivery-options">
                <div class="delivery-card">
                    <div class="icon">🏠</div>
                    <h3>Local Pickup</h3>
                    <p>Pick up your 3Doodles in person! Free for neighbors and local orders. We'll arrange a time that works for you.</p>
                </div>
                <div class="delivery-card">
                    <div class="icon">📦</div>
                    <h3>Shipping</h3>
                    <p>We can ship your critters anywhere! Shipping cost depends on location. We'll let you know the price before you pay.</p>
                </div>
            </div>
        </section>

        <section id="payment">
            <h2>Payment Options</h2>
            <p style="text-align: center; margin-bottom: 1rem;">We accept several easy ways to pay:</p>
            <div class="payment-options">
                <div class="payment-option">
                    <div class="icon">💵</div>
                    <h4>Cash</h4>
                    <p>For local pickup</p>
                </div>
                <div class="payment-option">
                    <div class="icon">🅿️</div>
                    <h4>PayPal</h4>
                    <p>Safe & easy online</p>
                </div>
                <div class="payment-option">
                    <div class="icon">💳</div>
                    <h4>Venmo</h4>
                    <p>Quick mobile payment</p>
                </div>
                <div class="payment-option">
                    <div class="icon">💳</div>
                    <h4>Card</h4>
                    <p>Via Stripe</p>
                </div>
            </div>
        </section>

        <section id="contact">
            <div class="contact-box">
                <h2>Ready to Order?</h2>
                <p>Send us an email and we'll get back to you super fast!</p>
                <a href="mailto:Mira@3DoodleCritters.com" class="contact-email">
                    Mira@3DoodleCritters.com
                </a>
                <p style="margin-top: 1.5rem; font-size: 1rem; opacity: 0.9;">
                    Please include: which items you want, your name, and if you want pickup or shipping!
                </p>
            </div>
        </section>
    </main>

    <footer>
        <div class="footer-hearts">💜 💙 💖</div>
        <p>Made with love by Mira | 3Doodle Critters &copy; 2025</p>
    </footer>
</body>
</html>
'''

    with open(WEBSITE_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

def show_menu():
    """Display the main menu."""
    print("\n" + "=" * 60)
    print("  🎨 3DOODLE CRITTERS INVENTORY MANAGER 🎨")
    print("=" * 60)
    print("  (Website auto-updates when you make changes)")
    print("""
  [1] List all items
  [2] Add new item
  [3] Edit item
  [4] Remove item
  [5] Toggle sold status
  [6] Regenerate website manually
  [7] Exit
""")

def main():
    """Main function."""
    print("\n  Welcome to the 3Doodle Critters Inventory Manager!")

    inventory = load_inventory()

    while True:
        show_menu()
        choice = input("  Enter choice (1-7): ").strip()

        if choice == "1":
            list_items(inventory)
        elif choice == "2":
            add_item(inventory)
            inventory = load_inventory()  # Reload
        elif choice == "3":
            edit_item(inventory)
            inventory = load_inventory()
        elif choice == "4":
            remove_item(inventory)
            inventory = load_inventory()
        elif choice == "5":
            toggle_sold(inventory)
            inventory = load_inventory()
        elif choice == "6":
            generate_website(inventory)
        elif choice == "7":
            print("\n  Goodbye! 👋\n")
            break
        else:
            print("\n  Invalid choice. Please try again.\n")

if __name__ == "__main__":
    main()
