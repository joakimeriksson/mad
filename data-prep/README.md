# Data Preparation Tools

Tools for generating and preparing content for the MAD project.

## Generate Poster Images

Creates placeholder poster images from the poster metadata.

### Requirements

```bash
# Install Pillow (PIL) for image generation
pip install pillow

# Or add to your environment
pixi add pillow
```

### Usage

```bash
# Run from the data-prep directory
cd data-prep
python generate_poster_images.py
```

This will:
1. Read poster data from `backend/data/posters.json`
2. Generate PNG images for each poster
3. Save them to `client-godot/assets/posters/`

### What Gets Generated

Each poster image includes:
- **Header** with title (white on blue background)
- **Authors** list
- **Tags** as bullet points
- **Abstract** text (word-wrapped)
- **Footer** with room and booth location

### Customization

Edit `generate_poster_images.py` to change:
- Image size (default: 1200x1600)
- Colors and fonts
- Layout and spacing
- Content sections

### After Generation

1. Open your Godot project
2. Images will auto-import in `res://assets/posters/`
3. Apply them to poster booths:
   - Select booth → PosterMesh
   - Create StandardMaterial3D
   - Load the poster image as Albedo texture

## Future Tools

- `extract_posters.py` - Extract poster metadata from PDFs
- `generate_faqs.py` - Generate FAQs using LLM
- `validate_data.py` - Validate poster JSON schema
