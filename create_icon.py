from PIL import Image, ImageDraw
import os

# Create an icon with yellow/blue/purple gradient
def create_icon():
    sizes = [16, 32, 48, 64, 128, 256]
    images = []

    for size in sizes:
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Colors matching the website
        YELLOW = (255, 220, 80)
        BLUE = (52, 152, 219)
        PURPLE = (125, 60, 152)

        # Draw a rounded square with gradient-like stripes
        padding = size // 8

        # Background - rounded rectangle
        draw.rounded_rectangle(
            [padding, padding, size - padding, size - padding],
            radius=size // 4,
            fill=BLUE
        )

        # Top section - yellow
        third = (size - 2 * padding) // 3
        draw.rounded_rectangle(
            [padding, padding, size - padding, padding + third],
            radius=size // 6,
            fill=YELLOW
        )

        # Bottom section - purple
        draw.rounded_rectangle(
            [padding, size - padding - third, size - padding, size - padding],
            radius=size // 6,
            fill=PURPLE
        )

        # Draw "3D" text if size is large enough
        if size >= 48:
            # Simple "3D" indicator with circles
            center_y = size // 2
            dot_size = size // 10

            # Three dots representing "3D"
            draw.ellipse([size//3 - dot_size, center_y - dot_size,
                         size//3 + dot_size, center_y + dot_size], fill=(255, 255, 255))
            draw.ellipse([size//2 - dot_size, center_y - dot_size,
                         size//2 + dot_size, center_y + dot_size], fill=(255, 255, 255))
            draw.ellipse([2*size//3 - dot_size, center_y - dot_size,
                         2*size//3 + dot_size, center_y + dot_size], fill=(255, 255, 255))

        images.append(img)

    # Save as ICO
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "3doodle-critters.ico")

    # Save with multiple sizes
    images[5].save(
        icon_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[:-1]
    )

    print(f"Icon saved to: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon()
