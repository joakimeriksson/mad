# Data Preparation Tools

Tools for generating and preparing content for the MAD project.

## Extract from PDFs (Recommended for Real Posters) ⭐

Automatically extract content from research poster PDFs and generate both agent data and display images.

### Requirements

```bash
# Install required packages
pip install pdf2image pypdf pillow

# Install poppler (PDF rendering library)
# macOS:
brew install poppler

# Linux:
sudo apt-get install poppler-utils

# Windows:
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

### Usage

```bash
cd data-prep

# Basic usage - process all PDFs in a directory
python extract_from_pdfs.py /path/to/poster/pdfs/

# Merge with existing posters (doesn't replace them)
python extract_from_pdfs.py /path/to/pdfs/ --merge

# Start numbering from a specific ID
python extract_from_pdfs.py /path/to/pdfs/ --start-id 6

# Custom output locations
python extract_from_pdfs.py /path/to/pdfs/ \
    --output-json ../backend/data/posters.json \
    --output-images ../client-godot/assets/posters
```

### What It Does

1. **Converts PDFs to PNGs** - High-quality images for Godot display
2. **Extracts text content** - Pulls title, authors, abstract from PDF
3. **Generates metadata** - Creates posters.json entries
4. **Auto-detects topics** - Tags based on keywords (AI, robotics, etc.)
5. **Ready to use** - No manual data entry needed!

### Output

- **PNG images** in `client-godot/assets/posters/`
- **Updated posters.json** with extracted metadata
- **Agent knowledge** automatically populated

### Customization

Edit `extract_from_pdfs.py` to improve text extraction for your poster format:

```python
# Customize parsing rules
def parse_poster_content(text: str, poster_id: str) -> Dict:
    # Add your custom logic here
    # e.g., regex patterns for your specific poster template
```

### Example Workflow

```bash
# 1. Put all poster PDFs in a folder
mkdir ~/posters
cp my_poster1.pdf my_poster2.pdf ~/posters/

# 2. Extract content
cd data-prep
python extract_from_pdfs.py ~/posters/

# 3. Review and edit the generated posters.json
nano ../backend/data/posters.json

# 4. Restart backend
cd ../backend
pixi run dev

# 5. Apply to Godot (in Godot editor)
# File → Run Script → apply_poster_materials.gd
```

---

## Generate Placeholder Poster Images

Creates simple poster images from the poster metadata (useful for testing).

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
