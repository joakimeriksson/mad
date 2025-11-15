# Data Preparation Tools

Tools for generating and preparing content for the MAD project.

## 🚀 Unified Poster Import (RECOMMENDED) ⭐

**NEW:** Use `import_posters.py` for a complete, streamlined workflow that handles PDF conversion, metadata extraction, and backend updates in one command.

### Quick Start

```bash
# With vision-based extraction (most accurate, requires Ollama)
python import_posters.py /path/to/pdfs --use-vision --merge

# Without vision (text parsing fallback)
python import_posters.py /path/to/pdfs --merge

# Validate existing data
python import_posters.py --validate
```

### Features

✅ **PDF → PNG conversion** for Godot display
✅ **Smart metadata extraction** using vision models or text parsing
✅ **Manual overrides** via `poster_overrides.yaml`
✅ **Intelligent merging** preserves FAQs, booth assignments, etc.
✅ **Dual backend sync** keeps both JSON files consistent
✅ **Full validation** ensures Godot assets match backend metadata
✅ **Metadata tracking** records source files and timestamps

### Installation

```bash
# Install Python dependencies
pip install pdf2image pypdf pillow pyyaml requests

# Install system dependencies
# macOS:
brew install poppler

# Linux:
sudo apt-get install poppler-utils

# Optional: Install Ollama for vision-based extraction
# Download from https://ollama.ai, then:
ollama pull gemma3
```

### Usage Examples

```bash
# Import new posters with vision extraction
python import_posters.py ~/Downloads/posters --use-vision --merge

# Import starting from a specific ID
python import_posters.py ~/posters --start-id 10 --merge

# Replace all existing posters
python import_posters.py ~/posters --replace --use-vision

# Check everything is consistent
python import_posters.py --validate
```

### Manual Overrides

Create/edit `poster_overrides.yaml` to correct auto-extracted data:

```yaml
# Simple title correction
my-poster-filename: "Correct Title Here"

# Full metadata override
another-poster:
  title: "Complete Title"
  authors: ["Author One", "Author Two"]
  tags: ["ai", "robotics", "research"]
  abstract: "Custom abstract text..."
```

**Key:** Use the PDF filename (without `.pdf` extension)

### What It Does

1. **Converts** each PDF to `client-godot/assets/posters/poster_XXX.png`
2. **Extracts** metadata (title, authors, abstract, tags) using:
   - Vision models (gemma3/llava) for accurate OCR
   - Text parsing as fallback
3. **Applies** manual overrides from YAML file
4. **Merges** with existing data, preserving:
   - FAQ entries
   - Booth assignments (`booth_id`, `room`)
   - Related links
   - Contact info
5. **Updates** both backend JSON files:
   - `backend/posters.json` (structured with metadata)
   - `backend/data/posters.json` (simple array)
6. **Validates** consistency between Godot assets and backend

### Next Steps After Import

1. Review generated metadata in `backend/posters.json`
2. Add FAQ entries, booth assignments, contact info
3. Restart backend: `pixi run dev`
4. In Godot: File → Run Script → `scripts/apply_poster_materials.gd`
5. Test in game!

---

## Legacy: Extract from PDFs (Deprecated)

Automatically extract content from research poster PDFs and generate both agent data and display images.

### Requirements

**Using Pixi (Recommended)**

```bash
cd data-prep

# Install dependencies
pixi install

# Install poppler (system dependency, can't be managed by pixi)
# macOS:
brew install poppler

# Linux:
sudo apt-get install poppler-utils

# Windows:
# Download from: https://github.com/oschwartz10612/poppler-windows/releases
```

**Or using pip**

```bash
pip install pdf2image pypdf pillow

# Plus install poppler (see above)
```

### Usage

**Using Pixi (Recommended)**

```bash
cd data-prep

# Basic usage - process all PDFs in a directory
pixi run python extract_from_pdfs.py /path/to/poster/pdfs/

# Or use the task shortcut
pixi run extract /path/to/poster/pdfs/

# Merge with existing posters (doesn't replace them)
pixi run python extract_from_pdfs.py /path/to/pdfs/ --merge

# Start numbering from a specific ID
pixi run python extract_from_pdfs.py /path/to/pdfs/ --start-id 6
```

**Or directly with Python**

```bash
python extract_from_pdfs.py /path/to/poster/pdfs/
python extract_from_pdfs.py /path/to/pdfs/ --merge
python extract_from_pdfs.py /path/to/pdfs/ --start-id 6
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

# 2. Install dependencies (one time)
cd data-prep
pixi install
brew install poppler  # macOS, or apt-get on Linux

# 3. Extract content
pixi run python extract_from_pdfs.py ~/posters/

# 4. Review and edit the generated posters.json
nano ../backend/data/posters.json

# 5. Restart backend
cd ../backend
pixi run dev

# 6. Apply to Godot (in Godot editor)
# File → Run Script → apply_poster_materials.gd
```

---

## Generate Placeholder Poster Images

Creates simple poster images from the poster metadata (useful for testing).

### Requirements

```bash
cd data-prep

# Install dependencies (includes Pillow)
pixi install
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

## Script Reference

### Current Scripts

- **`import_posters.py`** ⭐ - Unified import workflow (RECOMMENDED)
- **`generate_poster_images.py`** - Generate placeholder images from JSON
- **`update_godot_scene.py`** - Update Godot scene with poster titles
- **`poster_overrides.yaml`** - Manual metadata corrections

### Legacy Scripts (Deprecated)

These scripts are superseded by `import_posters.py` but remain for compatibility:

- `extract_from_pdfs.py` - Use `import_posters.py` instead
- `extract_posters.py` - Merged into `import_posters.py`

### Future Enhancements

- `generate_faqs.py` - Auto-generate FAQs using LLM
- Enhanced vision extraction with multiple models
- Batch processing optimizations
