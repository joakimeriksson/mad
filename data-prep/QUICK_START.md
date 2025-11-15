# Quick Start: Adding Posters to MAD

Two ways to add posters to your virtual open house:

## Method 1: From PDF Files (Real Research Posters) ⭐

**Use this when:** You have actual research poster PDFs

**Pros:**
- Uses real poster images (looks professional)
- Auto-extracts metadata (less manual work)
- Agents get actual research content

**Steps:**

```bash
# 1. Install dependencies
cd data-prep
pixi install

# Install poppler (system dependency)
# macOS:
brew install poppler
# Linux:
sudo apt-get install poppler-utils

# 2. Put your PDFs in a folder
mkdir ~/my-posters
# Copy your PDF files there

# 3. Run extraction
pixi run python extract_from_pdfs.py ~/my-posters/

# 4. (Optional) Edit the generated metadata
nano ../backend/data/posters.json

# 5. Restart backend
cd ../backend
pixi run dev
```

**Then in Godot:**
1. Open `scenes/environment/main.tscn`
2. File → Run Script → `scripts/apply_poster_materials.gd`
3. Save and run (F5)

---

## Method 2: Generate Placeholder Images

**Use this when:**
- Testing the system
- You don't have PDFs yet
- You want custom-designed posters

**Pros:**
- Quick and simple
- Full control over content
- Good for demos

**Steps:**

```bash
# 1. Install dependencies
cd data-prep
pixi install

# 2. Edit poster data
nano ../backend/data/posters.json
# Add/edit your poster metadata

# 3. Generate images
pixi run python generate_poster_images.py
# Or use the task shortcut:
pixi run generate

# 4. Restart backend
cd ../backend
pixi run dev
```

**Then in Godot:**
Same as Method 1 above

---

## Comparison

| Feature | PDF Extraction | Placeholder Generator |
|---------|---------------|----------------------|
| Input | PDF files | Manual JSON editing |
| Image quality | Professional (actual poster) | Simple generated design |
| Text extraction | Automatic | Manual entry |
| Setup complexity | More (needs poppler) | Minimal |
| Customization | PDF-dependent | Full control |
| Best for | Production | Testing/demos |

---

## Troubleshooting

### PDF extraction fails

```bash
# Check poppler is installed
which pdftoppm  # Should return a path

# macOS
brew install poppler

# Linux
sudo apt-get install poppler-utils
```

### Poor text extraction

PDFs vary widely in structure. You may need to:
1. Edit `extract_from_pdfs.py` to customize parsing
2. Manually fix the generated `posters.json`
3. Use OCR for image-based PDFs (add pytesseract)

### Images not showing in Godot

1. Check files exist in `client-godot/assets/posters/`
2. Reimport in Godot: Right-click folder → Reimport
3. Run the material script again

---

## Tips

- **Start with 1-2 PDFs** to test before processing many
- **Review generated metadata** - auto-extraction isn't perfect
- **Use `--merge` flag** to add posters without replacing existing ones
- **Customize room/booth** assignments in posters.json
- **Add FAQs manually** for better agent responses

---

## Example: Adding 3 New Posters

```bash
# You have 3 PDF files: poster_a.pdf, poster_b.pdf, poster_c.pdf

cd data-prep

# Install dependencies (first time only)
pixi install
brew install poppler  # macOS

# Process them (will create poster_001, poster_002, poster_003)
pixi run python extract_from_pdfs.py ~/Downloads/

# Verify images were created
ls ../client-godot/assets/posters/
# Should show: poster_001.png, poster_002.png, poster_003.png

# Check the data
cat ../backend/data/posters.json
# Verify titles, authors look correct

# Restart backend
cd ../backend
pixi run dev

# In Godot: apply materials and run!
```

That's it! 🎉
