"""
Generate placeholder poster images for the MAD project.
Requires: Pillow (PIL)
Install: pixi add pillow  OR  pip install pillow
"""

from PIL import Image, ImageDraw, ImageFont
import json
from pathlib import Path


def create_poster_image(poster_data: dict, output_path: Path, size=(1200, 1600)):
    """Create a simple poster image with title, authors, and abstract."""

    # Create image with white background
    img = Image.new('RGB', size, color='white')
    draw = ImageDraw.Draw(img)

    # Try to use a nice font, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 60)
        author_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        body_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 30)
        tag_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 25)
    except:
        # Fallback to default font
        title_font = ImageFont.load_default()
        author_font = ImageFont.load_default()
        body_font = ImageFont.load_default()
        tag_font = ImageFont.load_default()

    # Define margins and positions
    margin = 80
    y_pos = margin

    # Draw colored header bar
    draw.rectangle([(0, 0), (size[0], 200)], fill='#2E86AB')

    # Draw title (white on blue)
    title = poster_data['title']
    y_pos = 50
    # Word wrap title
    words = title.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=title_font)
        if bbox[2] - bbox[0] > size[0] - 2 * margin:
            current_line.pop()
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    for line in lines:
        draw.text((margin, y_pos), line, fill='white', font=title_font)
        y_pos += 70

    # Draw authors
    y_pos = 220
    authors = ', '.join(poster_data['authors'])
    draw.text((margin, y_pos), authors, fill='#555555', font=author_font)
    y_pos += 80

    # Draw tags
    tags_text = ' • '.join(poster_data['tags'])
    draw.text((margin, y_pos), tags_text, fill='#2E86AB', font=tag_font)
    y_pos += 60

    # Draw separator line
    draw.line([(margin, y_pos), (size[0] - margin, y_pos)], fill='#CCCCCC', width=2)
    y_pos += 40

    # Draw abstract
    abstract = poster_data['abstract']
    # Word wrap abstract
    words = abstract.split()
    lines = []
    current_line = []
    for word in words:
        current_line.append(word)
        test_line = ' '.join(current_line)
        bbox = draw.textbbox((0, 0), test_line, font=body_font)
        if bbox[2] - bbox[0] > size[0] - 2 * margin:
            current_line.pop()
            if current_line:
                lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))

    for line in lines:
        if y_pos > size[1] - 200:  # Stop if we're near the bottom
            break
        draw.text((margin, y_pos), line, fill='#333333', font=body_font)
        y_pos += 40

    # Draw footer with booth info
    y_pos = size[1] - 100
    draw.rectangle([(0, y_pos), (size[0], size[1])], fill='#F0F0F0')
    footer_text = f"Location: {poster_data.get('room', 'TBD')} - {poster_data.get('booth_id', 'TBD')}"
    draw.text((margin, y_pos + 30), footer_text, fill='#666666', font=tag_font)

    # Save image
    img.save(output_path, 'PNG')
    print(f"Created: {output_path}")


def main():
    # Load poster data
    data_file = Path(__file__).parent.parent / "backend" / "data" / "posters.json"
    output_dir = Path(__file__).parent.parent / "client-godot" / "assets" / "posters"

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load posters
    with open(data_file, 'r') as f:
        posters = json.load(f)

    # Generate images for each poster
    for poster in posters:
        poster_id = poster['id']
        output_path = output_dir / f"{poster_id}.png"
        create_poster_image(poster, output_path)

    print(f"\n✓ Generated {len(posters)} poster images in {output_dir}")
    print("\nNext steps:")
    print("1. Open Godot project")
    print("2. Images will auto-import in res://assets/posters/")
    print("3. Apply them to poster booths (see instructions)")


if __name__ == "__main__":
    main()
