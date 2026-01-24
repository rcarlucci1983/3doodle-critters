"""
3Doodle Critters Inventory Manager - GUI Version
=================================================
A kid-friendly app to manage shop inventory.
"""

import json
import os
import uuid
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from PIL import Image, ImageTk
import shutil
import subprocess

# Paths
SCRIPT_DIR = Path(__file__).parent
INVENTORY_FILE = SCRIPT_DIR / "inventory.json"
IMAGES_DIR = SCRIPT_DIR / "images"
WEBSITE_FILE = SCRIPT_DIR / "index.html"

# Ensure directories exist
IMAGES_DIR.mkdir(exist_ok=True)

# Colors matching the brand
COLORS = {
    'purple': '#9B59B6',
    'purple_dark': '#7D3C98',
    'teal': '#1ABC9C',
    'teal_dark': '#16A085',
    'pink': '#FF6B9D',
    'pink_light': '#FFB8D0',
    'yellow': '#FFDC50',
    'cream': '#FFF9F0',
    'white': '#FFFFFF',
    'text_dark': '#2C3E50'
}


class InventoryApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎨 3Doodle Critters Inventory Manager")
        self.root.geometry("900x700")
        self.root.configure(bg=COLORS['cream'])

        # Set app icon (optional)
        try:
            self.root.iconbitmap(default='')
        except:
            pass

        self.inventory = self.load_inventory()
        self.selected_item = None
        self.photo_refs = []  # Keep references to prevent garbage collection

        self.create_widgets()
        self.refresh_item_list()

    def load_inventory(self):
        """Load inventory from JSON file."""
        if INVENTORY_FILE.exists():
            with open(INVENTORY_FILE, 'r') as f:
                return json.load(f)
        return {"items": [], "google_drive_folder_id": ""}

    def save_inventory(self):
        """Save inventory to JSON file and regenerate website."""
        with open(INVENTORY_FILE, 'w') as f:
            json.dump(self.inventory, f, indent=2)
        self.generate_website()

    def generate_item_id(self):
        """Generate a unique item ID."""
        return str(uuid.uuid4())[:8]

    def create_widgets(self):
        """Create all GUI widgets."""
        # Header
        header = tk.Frame(self.root, bg=COLORS['purple'], height=80)
        header.pack(fill='x')
        header.pack_propagate(False)

        title = tk.Label(
            header,
            text="🎨 3Doodle Critters Inventory 🎨",
            font=('Arial Rounded MT Bold', 24, 'bold'),
            bg=COLORS['purple'],
            fg=COLORS['white']
        )
        title.pack(pady=20)

        # Main container
        main_frame = tk.Frame(self.root, bg=COLORS['cream'])
        main_frame.pack(fill='both', expand=True, padx=20, pady=20)

        # Left panel - Item list
        left_panel = tk.Frame(main_frame, bg=COLORS['white'], relief='raised', bd=2)
        left_panel.pack(side='left', fill='both', expand=True, padx=(0, 10))

        list_header = tk.Label(
            left_panel,
            text="My Items",
            font=('Arial', 16, 'bold'),
            bg=COLORS['teal'],
            fg=COLORS['white'],
            pady=10
        )
        list_header.pack(fill='x')

        # Item listbox with scrollbar
        list_frame = tk.Frame(left_panel, bg=COLORS['white'])
        list_frame.pack(fill='both', expand=True, padx=10, pady=10)

        scrollbar = tk.Scrollbar(list_frame)
        scrollbar.pack(side='right', fill='y')

        self.item_listbox = tk.Listbox(
            list_frame,
            font=('Arial', 14),
            bg=COLORS['white'],
            fg=COLORS['text_dark'],
            selectbackground=COLORS['pink'],
            selectforeground=COLORS['white'],
            height=15,
            yscrollcommand=scrollbar.set
        )
        self.item_listbox.pack(fill='both', expand=True)
        scrollbar.config(command=self.item_listbox.yview)

        self.item_listbox.bind('<<ListboxSelect>>', self.on_item_select)

        # Right panel - Item details / Add form
        right_panel = tk.Frame(main_frame, bg=COLORS['white'], relief='raised', bd=2, width=350)
        right_panel.pack(side='right', fill='both', padx=(10, 0))
        right_panel.pack_propagate(False)

        details_header = tk.Label(
            right_panel,
            text="Item Details",
            font=('Arial', 16, 'bold'),
            bg=COLORS['pink'],
            fg=COLORS['white'],
            pady=10
        )
        details_header.pack(fill='x')

        # Form fields
        form_frame = tk.Frame(right_panel, bg=COLORS['white'], padx=15, pady=15)
        form_frame.pack(fill='both', expand=True)

        # Title
        tk.Label(form_frame, text="Title:", font=('Arial', 12, 'bold'),
                bg=COLORS['white'], fg=COLORS['purple_dark']).pack(anchor='w')
        self.title_entry = tk.Entry(form_frame, font=('Arial', 14), width=25)
        self.title_entry.pack(fill='x', pady=(0, 10))

        # Description
        tk.Label(form_frame, text="Description:", font=('Arial', 12, 'bold'),
                bg=COLORS['white'], fg=COLORS['purple_dark']).pack(anchor='w')
        self.desc_entry = tk.Text(form_frame, font=('Arial', 12), height=3, width=25)
        self.desc_entry.pack(fill='x', pady=(0, 10))

        # Price
        tk.Label(form_frame, text="Price ($):", font=('Arial', 12, 'bold'),
                bg=COLORS['white'], fg=COLORS['purple_dark']).pack(anchor='w')
        self.price_entry = tk.Entry(form_frame, font=('Arial', 14), width=10)
        self.price_entry.pack(anchor='w', pady=(0, 10))

        # Image
        tk.Label(form_frame, text="Image:", font=('Arial', 12, 'bold'),
                bg=COLORS['white'], fg=COLORS['purple_dark']).pack(anchor='w')

        image_frame = tk.Frame(form_frame, bg=COLORS['white'])
        image_frame.pack(fill='x', pady=(0, 10))

        self.image_label = tk.Label(image_frame, text="No image", font=('Arial', 10),
                                   bg=COLORS['pink_light'], width=20, height=2)
        self.image_label.pack(side='left')

        choose_btn = tk.Button(
            image_frame, text="Choose...", font=('Arial', 10),
            bg=COLORS['teal'], fg=COLORS['white'],
            command=self.choose_image
        )
        choose_btn.pack(side='left', padx=5)

        self.current_image = None

        # Sold checkbox
        self.sold_var = tk.BooleanVar()
        sold_check = tk.Checkbutton(
            form_frame, text="SOLD", font=('Arial', 12, 'bold'),
            variable=self.sold_var, bg=COLORS['white'],
            fg=COLORS['pink'], selectcolor=COLORS['white']
        )
        sold_check.pack(anchor='w', pady=(0, 15))

        # Image preview
        self.preview_frame = tk.Frame(form_frame, bg=COLORS['pink_light'], width=150, height=150)
        self.preview_frame.pack(pady=10)
        self.preview_frame.pack_propagate(False)

        self.preview_label = tk.Label(self.preview_frame, bg=COLORS['pink_light'])
        self.preview_label.pack(expand=True)

        # Buttons panel
        btn_frame = tk.Frame(self.root, bg=COLORS['cream'], pady=15)
        btn_frame.pack(fill='x', padx=20)

        # Big colorful buttons
        btn_style = {'font': ('Arial', 14, 'bold'), 'width': 12, 'height': 2, 'relief': 'raised', 'bd': 3}

        add_btn = tk.Button(
            btn_frame, text="➕ ADD NEW",
            bg=COLORS['yellow'], fg=COLORS['text_dark'],
            command=self.add_item, **btn_style
        )
        add_btn.pack(side='left', padx=5)

        save_btn = tk.Button(
            btn_frame, text="💾 SAVE",
            bg='#3498DB', fg=COLORS['white'],
            command=self.save_item, **btn_style
        )
        save_btn.pack(side='left', padx=5)

        delete_btn = tk.Button(
            btn_frame, text="🗑️ DELETE",
            bg='#3498DB', fg=COLORS['white'],
            command=self.delete_item, **btn_style
        )
        delete_btn.pack(side='left', padx=5)

        clear_btn = tk.Button(
            btn_frame, text="🔄 CLEAR",
            bg='#3498DB', fg=COLORS['white'],
            command=self.clear_form, **btn_style
        )
        clear_btn.pack(side='left', padx=5)

        view_btn = tk.Button(
            btn_frame, text="🌐 VIEW SITE",
            bg=COLORS['purple'], fg=COLORS['white'],
            command=self.view_website, **btn_style
        )
        view_btn.pack(side='right', padx=5)

        publish_btn = tk.Button(
            btn_frame, text="🚀 PUBLISH",
            bg=COLORS['purple'], fg=COLORS['white'],
            command=self.publish_to_github, **btn_style
        )
        publish_btn.pack(side='right', padx=5)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready! Add items to your shop.")
        status_bar = tk.Label(
            self.root, textvariable=self.status_var,
            font=('Arial', 11), bg=COLORS['purple_dark'],
            fg=COLORS['white'], anchor='w', padx=10, pady=5
        )
        status_bar.pack(fill='x', side='bottom')

    def refresh_item_list(self):
        """Refresh the item listbox."""
        self.item_listbox.delete(0, tk.END)
        for item in self.inventory.get("items", []):
            status = " [SOLD]" if item.get('sold', False) else ""
            display = f"{item['title']} - ${item['price']:.2f}{status}"
            self.item_listbox.insert(tk.END, display)

        count = len(self.inventory.get("items", []))
        self.status_var.set(f"Total items: {count}")

    def on_item_select(self, event):
        """Handle item selection from list."""
        selection = self.item_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        items = self.inventory.get("items", [])
        if index < len(items):
            self.selected_item = items[index]
            self.populate_form(self.selected_item)

    def populate_form(self, item):
        """Fill the form with item data."""
        self.clear_form(keep_selection=True)

        self.title_entry.insert(0, item.get('title', ''))
        self.desc_entry.insert('1.0', item.get('description', ''))
        self.price_entry.insert(0, str(item.get('price', '')))
        self.sold_var.set(item.get('sold', False))

        self.current_image = item.get('image')
        if self.current_image:
            self.image_label.config(text=self.current_image[:20] + "..." if len(self.current_image) > 20 else self.current_image)
            self.show_preview(IMAGES_DIR / self.current_image)
        else:
            self.image_label.config(text="No image")
            self.preview_label.config(image='', text="No preview")

    def clear_form(self, keep_selection=False):
        """Clear all form fields."""
        self.title_entry.delete(0, tk.END)
        self.desc_entry.delete('1.0', tk.END)
        self.price_entry.delete(0, tk.END)
        self.sold_var.set(False)
        self.current_image = None
        self.image_label.config(text="No image")
        self.preview_label.config(image='', text="")

        if not keep_selection:
            self.selected_item = None
            self.item_listbox.selection_clear(0, tk.END)

    def choose_image(self):
        """Open file dialog to choose an image."""
        filetypes = [
            ('Image files', '*.png *.jpg *.jpeg *.gif *.bmp'),
            ('All files', '*.*')
        ]
        filepath = filedialog.askopenfilename(
            title="Choose an image",
            initialdir=IMAGES_DIR,
            filetypes=filetypes
        )

        if filepath:
            filepath = Path(filepath)
            # If not already in images folder, copy it
            if filepath.parent != IMAGES_DIR:
                new_filename = f"{self.generate_item_id()}{filepath.suffix}"
                new_path = IMAGES_DIR / new_filename
                shutil.copy(filepath, new_path)
                self.current_image = new_filename
            else:
                self.current_image = filepath.name

            self.image_label.config(text=self.current_image[:20] + "..." if len(self.current_image) > 20 else self.current_image)
            self.show_preview(IMAGES_DIR / self.current_image)

    def show_preview(self, image_path):
        """Show image preview."""
        try:
            img = Image.open(image_path)
            img.thumbnail((140, 140))
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.photo_refs.append(photo)  # Keep reference
        except Exception as e:
            self.preview_label.config(image='', text="Preview\nunavailable")

    def add_item(self):
        """Prepare to add a new item."""
        self.clear_form()
        self.title_entry.focus()
        self.status_var.set("Enter details for new item...")

    def save_item(self):
        """Save the current item (add new or update existing)."""
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Oops!", "Please enter a title for your item!")
            return

        try:
            price = float(self.price_entry.get().strip() or 0)
        except ValueError:
            messagebox.showwarning("Oops!", "Please enter a valid price (like 5.00)")
            return

        description = self.desc_entry.get('1.0', tk.END).strip()

        if self.selected_item:
            # Update existing
            self.selected_item['title'] = title
            self.selected_item['description'] = description
            self.selected_item['price'] = price
            self.selected_item['sold'] = self.sold_var.get()
            if self.current_image:
                self.selected_item['image'] = self.current_image
            self.status_var.set(f"Updated: {title}")
        else:
            # Add new
            new_item = {
                'id': self.generate_item_id(),
                'title': title,
                'description': description,
                'price': price,
                'image': self.current_image,
                'sold': self.sold_var.get()
            }
            self.inventory.setdefault("items", []).append(new_item)
            self.status_var.set(f"Added: {title}")

        self.save_inventory()
        self.refresh_item_list()
        self.clear_form()

        messagebox.showinfo("Saved!", f"'{title}' has been saved!\nThe website has been updated too!")

    def delete_item(self):
        """Delete the selected item."""
        if not self.selected_item:
            messagebox.showwarning("Oops!", "Please select an item to delete first!")
            return

        title = self.selected_item.get('title', 'this item')
        if messagebox.askyesno("Delete?", f"Are you sure you want to delete '{title}'?"):
            self.inventory["items"].remove(self.selected_item)
            self.save_inventory()
            self.refresh_item_list()
            self.clear_form()
            self.status_var.set(f"Deleted: {title}")

    def view_website(self):
        """Open the website in browser."""
        import webbrowser
        webbrowser.open(str(WEBSITE_FILE))

    def publish_to_github(self):
        """Push all changes to GitHub to update the live website."""
        self.status_var.set("Publishing to website...")
        self.root.update()

        try:
            # Change to the project directory
            os.chdir(SCRIPT_DIR)

            # Stage all changes (including new images)
            result = subprocess.run(
                ['git', 'add', '.'],
                capture_output=True, text=True, cwd=SCRIPT_DIR
            )
            if result.returncode != 0:
                raise Exception(f"Git add failed: {result.stderr}")

            # Check if there are changes to commit
            status_result = subprocess.run(
                ['git', 'status', '--porcelain'],
                capture_output=True, text=True, cwd=SCRIPT_DIR
            )

            if not status_result.stdout.strip():
                messagebox.showinfo("All Good!", "No changes to publish!\nYour website is already up to date.")
                self.status_var.set("Ready! No changes to publish.")
                return

            # Commit the changes
            result = subprocess.run(
                ['git', 'commit', '-m', 'Update inventory and website'],
                capture_output=True, text=True, cwd=SCRIPT_DIR
            )
            if result.returncode != 0:
                raise Exception(f"Git commit failed: {result.stderr}")

            # Push to GitHub
            result = subprocess.run(
                ['git', 'push'],
                capture_output=True, text=True, cwd=SCRIPT_DIR
            )
            if result.returncode != 0:
                raise Exception(f"Git push failed: {result.stderr}")

            self.status_var.set("Published! Website updated!")
            messagebox.showinfo(
                "Published!",
                "Your website has been updated!\n\n"
                "Visit: https://3doodlecritters.com\n\n"
                "(It may take a minute to show the changes)"
            )

        except Exception as e:
            self.status_var.set("Error publishing. Ask for help!")
            messagebox.showerror(
                "Oops!",
                f"Something went wrong while publishing:\n\n{str(e)}\n\n"
                "Ask a grown-up for help!"
            )

    def generate_website(self):
        """Generate the website HTML from inventory."""
        items = self.inventory.get("items", [])

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
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Nunito', sans-serif; background: var(--cream); color: var(--text-dark); line-height: 1.6; }}
        .bg-decoration {{ position: fixed; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; z-index: -1; overflow: hidden; }}
        .bg-decoration::before, .bg-decoration::after {{ content: ''; position: absolute; border-radius: 50%; opacity: 0.1; }}
        .bg-decoration::before {{ width: 400px; height: 400px; background: var(--purple); top: -100px; right: -100px; }}
        .bg-decoration::after {{ width: 300px; height: 300px; background: var(--teal); bottom: -50px; left: -50px; }}
        header {{ background: linear-gradient(135deg, var(--yellow) 0%, #3498DB 50%, var(--purple) 100%); padding: 2rem 1rem; text-align: center; }}
        h1 {{ font-family: 'Fredoka One', cursive; font-size: 3rem; color: white; text-shadow: 3px 3px 0 rgba(0,0,0,0.2); margin-bottom: 0.5rem; }}
        .tagline {{ font-size: 1.3rem; color: white; opacity: 0.95; font-weight: 600; }}
        nav {{ background: white; padding: 1rem; box-shadow: 0 2px 10px rgba(0,0,0,0.1); position: sticky; top: 0; z-index: 100; }}
        nav ul {{ list-style: none; display: flex; justify-content: center; flex-wrap: wrap; gap: 1rem; }}
        nav a {{ text-decoration: none; color: var(--purple-dark); font-weight: 700; padding: 0.5rem 1.5rem; border-radius: 25px; transition: all 0.3s ease; }}
        nav a:hover {{ background: var(--purple); color: white; }}
        main {{ max-width: 1200px; margin: 0 auto; padding: 2rem 1rem; }}
        section {{ margin-bottom: 4rem; }}
        h2 {{ font-family: 'Fredoka One', cursive; font-size: 2.2rem; color: var(--purple); text-align: center; margin-bottom: 2rem; }}
        h2::after {{ content: ''; display: block; width: 80px; height: 4px; background: linear-gradient(90deg, var(--teal), var(--pink)); margin: 0.5rem auto 0; border-radius: 2px; }}
        .welcome {{ background: white; border-radius: 20px; padding: 2.5rem; text-align: center; box-shadow: 0 5px 20px rgba(155, 89, 182, 0.15); border: 3px solid var(--pink-light); }}
        .welcome p {{ font-size: 1.2rem; max-width: 700px; margin: 0 auto; }}
        .welcome .highlight {{ color: var(--purple); font-weight: 700; }}
        .products-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 2rem; }}
        .product-card {{ background: white; border-radius: 20px; overflow: hidden; box-shadow: 0 5px 20px rgba(0,0,0,0.1); transition: transform 0.3s ease, box-shadow 0.3s ease; }}
        .product-card:hover {{ transform: translateY(-5px); box-shadow: 0 10px 30px rgba(155, 89, 182, 0.2); }}
        .product-card.sold {{ opacity: 0.7; }}
        .product-image {{ width: 100%; height: 250px; background: linear-gradient(135deg, var(--pink-light) 0%, #E8DAEF 100%); display: flex; align-items: center; justify-content: center; position: relative; overflow: hidden; }}
        .product-image img {{ width: 100%; height: 100%; object-fit: cover; }}
        .product-image .no-image {{ color: var(--purple); font-weight: 600; }}
        .sold-badge {{ position: absolute; top: 15px; right: -35px; background: var(--pink); color: white; padding: 5px 40px; font-weight: 700; transform: rotate(45deg); font-size: 0.9rem; }}
        .product-info {{ padding: 1.5rem; }}
        .product-info h3 {{ font-family: 'Fredoka One', cursive; color: var(--teal-dark); font-size: 1.3rem; margin-bottom: 0.5rem; }}
        .product-info p {{ color: #666; margin-bottom: 1rem; min-height: 3rem; }}
        .price {{ font-family: 'Fredoka One', cursive; font-size: 1.5rem; color: var(--pink); }}
        .no-products {{ text-align: center; padding: 3rem; color: var(--purple); font-size: 1.2rem; }}
        .order-steps {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 2rem; }}
        .step {{ background: white; border-radius: 20px; padding: 2rem; text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border-top: 5px solid var(--teal); }}
        .step-number {{ width: 50px; height: 50px; background: linear-gradient(135deg, var(--purple), var(--pink)); color: white; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-family: 'Fredoka One', cursive; font-size: 1.5rem; margin: 0 auto 1rem; }}
        .step h3 {{ color: var(--purple-dark); margin-bottom: 0.5rem; }}
        .payment-options {{ display: flex; flex-wrap: wrap; justify-content: center; gap: 1.5rem; margin-top: 1.5rem; }}
        .payment-option {{ background: white; padding: 1.5rem 2rem; border-radius: 15px; box-shadow: 0 3px 15px rgba(0,0,0,0.08); text-align: center; min-width: 150px; }}
        .payment-option .icon {{ font-size: 2.5rem; margin-bottom: 0.5rem; }}
        .payment-option h4 {{ color: var(--teal-dark); font-weight: 700; }}
        .delivery-options {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 2rem; margin-top: 1.5rem; }}
        .delivery-card {{ background: white; border-radius: 20px; padding: 2rem; text-align: center; box-shadow: 0 5px 20px rgba(0,0,0,0.08); border-left: 5px solid var(--pink); }}
        .delivery-card .icon {{ font-size: 3rem; margin-bottom: 1rem; }}
        .delivery-card h3 {{ color: var(--purple-dark); margin-bottom: 0.5rem; }}
        .contact-box {{ background: linear-gradient(135deg, var(--yellow) 0%, #3498DB 50%, var(--purple) 100%); border-radius: 20px; padding: 3rem; text-align: center; color: white; }}
        .contact-box h2 {{ color: white; }}
        .contact-box h2::after {{ background: white; }}
        .contact-box p {{ font-size: 1.2rem; margin-bottom: 1.5rem; }}
        .contact-email {{ display: inline-block; background: white; color: var(--purple-dark); font-family: 'Fredoka One', cursive; font-size: 1.3rem; padding: 1rem 2rem; border-radius: 30px; text-decoration: none; transition: transform 0.3s ease; }}
        .contact-email:hover {{ transform: scale(1.05); }}
        footer {{ background: var(--text-dark); color: white; text-align: center; padding: 2rem; margin-top: 2rem; }}
        footer p {{ opacity: 0.8; }}
        .footer-hearts {{ font-size: 1.5rem; margin-bottom: 0.5rem; }}
        @media (max-width: 768px) {{ h1 {{ font-size: 2rem; }} .tagline {{ font-size: 1rem; }} h2 {{ font-size: 1.8rem; }} nav ul {{ gap: 0.5rem; }} nav a {{ padding: 0.4rem 1rem; font-size: 0.9rem; }} }}
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
            <p>Hi! I'm <span class="highlight">Mira</span>, and I make cute animals and fun creations using a <span class="highlight">3D printing pen</span>! Each piece is carefully crafted by hand, making every 3Doodle unique and special. Check out my critters below and take one home today!</p>
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
                <div class="step"><div class="step-number">1</div><h3>Pick Your Critters</h3><p>Browse the shop and decide which 3Doodles you'd like!</p></div>
                <div class="step"><div class="step-number">2</div><h3>Send a Message</h3><p>Email us with what you want to order and how you'd like to receive it.</p></div>
                <div class="step"><div class="step-number">3</div><h3>Get Your Critters!</h3><p>Pick up locally or have them shipped to you!</p></div>
            </div>
        </section>
        <section id="delivery">
            <h2>Delivery Options</h2>
            <div class="delivery-options">
                <div class="delivery-card"><div class="icon">🏠</div><h3>Local Pickup</h3><p>Pick up your 3Doodles in person! Free for neighbors and local orders.</p></div>
                <div class="delivery-card"><div class="icon">📦</div><h3>Shipping</h3><p>We can ship your critters anywhere! Shipping cost depends on location.</p></div>
            </div>
        </section>
        <section id="payment">
            <h2>Payment Options</h2>
            <p style="text-align: center; margin-bottom: 1rem;">We accept several easy ways to pay:</p>
            <div class="payment-options">
                <div class="payment-option"><div class="icon">💵</div><h4>Cash</h4><p>For local pickup</p></div>
                <div class="payment-option"><div class="icon">🅿️</div><h4>PayPal</h4><p>Safe & easy online</p></div>
                <div class="payment-option"><div class="icon">💳</div><h4>Venmo</h4><p>Quick mobile payment</p></div>
                <div class="payment-option"><div class="icon">💳</div><h4>Card</h4><p>Via Stripe</p></div>
            </div>
        </section>
        <section id="contact">
            <div class="contact-box">
                <h2>Ready to Order?</h2>
                <p>Send us an email and we'll get back to you super fast!</p>
                <a href="mailto:Mira@3DoodleCritters.com" class="contact-email">Mira@3DoodleCritters.com</a>
                <p style="margin-top: 1.5rem; font-size: 1rem; opacity: 0.9;">Please include: which items you want, your name, and if you want pickup or shipping!</p>
            </div>
        </section>
    </main>
    <footer>
        <div class="footer-hearts">💛 💙 💜</div>
        <p>Made with love by Mira | 3Doodle Critters &copy; 2026</p>
    </footer>
</body>
</html>'''

        with open(WEBSITE_FILE, 'w', encoding='utf-8') as f:
            f.write(html)


def main():
    root = tk.Tk()
    app = InventoryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
