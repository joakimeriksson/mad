# Vision-Based Poster Extraction

Extract poster metadata using Ollama vision models for **much more accurate** title, author, and abstract extraction!

## Why Vision Extraction?

Traditional text-based PDF extraction struggles with:
- Titles buried in headers/footers
- Multi-column layouts
- Formatted text that doesn't parse well
- Images containing important text

**Vision models** look at the poster image like a human would and extract the correct information.

## Recommended Vision Models

Use one of these vision-capable models with Ollama:

1. **gemma3** (Recommended)
   ```bash
   ollama pull gemma3
   ```
   - Fast and accurate

2. **llava**
   ```bash
   ollama pull llava
   ```
   - Alternative vision model
   - Good for detailed image analysis

3. **minicpm-v**
   ```bash
   ollama pull minicpm-v
   ```
   - Smaller, faster
   - Good for simpler posters

## Setup

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Windows
# Download from https://ollama.ai
```

### 2. Start Ollama

```bash
ollama serve
```

### 3. Pull a Vision Model

```bash
# Recommended
ollama pull gemma3

# Or try llava
ollama pull llava
```

### 4. Install Dependencies

```bash
cd data-prep
pixi install
```

## Usage

### Method 1: Extract from PDFs with Vision

Process PDFs and use vision models to extract metadata:

```bash
cd data-prep

# Basic usage with vision
pixi run python extract_from_pdfs.py ~/my-posters/ --use-vision

# Specify a different vision model
pixi run python extract_from_pdfs.py ~/my-posters/ --use-vision --vision-model llava

# Merge with existing posters
pixi run python extract_from_pdfs.py ~/my-posters/ --use-vision --merge
```

**What this does:**
1. Converts each PDF to PNG
2. Sends the PNG to Ollama vision model
3. Model extracts title, authors, tags, and abstract
4. Saves to `backend/data/posters.json`

### Method 2: Extract from Existing Images

If you already have poster images (PNG/JPG):

```bash
cd data-prep

# Process existing images
pixi run python extract_with_vision.py ~/poster-images/

# Use a specific model
pixi run python extract_with_vision.py ~/poster-images/ --model llava

# Merge with existing data
pixi run python extract_with_vision.py ~/poster-images/ --merge
```

## Example Output

```
Found 3 poster images
Using vision model: llama3.2-vision:latest
============================================================

Processing poster_001.png → poster_001
  Using vision model to extract metadata...
  ✓ Extracted title: Edge Computing for Real-Time IoT Applications
  ✓ Authors: 2 found
  ✓ Tags: edge-computing, iot, real-time

Processing poster_002.png → poster_002
  Using vision model to extract metadata...
  ✓ Extracted title: Federated Learning with Differential Privacy
  ✓ Authors: 3 found
  ✓ Tags: federated-learning, privacy, machine-learning

✓ Saved 3 posters to backend/data/posters.json
```

## Comparison: Text vs Vision Extraction

### Text Extraction (Traditional)
```python
# Often extracts wrong title
"RISE Research Institute of Sweden"  # ❌ This is a header!

# Or too much text
"Introduction to Edge Computing for Real-Time Applications in IoT..."  # ❌ Too long!
```

### Vision Extraction (Recommended)
```python
# Correctly identifies the main title
"Edge Computing for Real-Time IoT Applications"  # ✓ Perfect!

# Also gets authors and abstract accurately
```

## Manual Overrides

If vision extraction still gets something wrong, you can add manual overrides:

```yaml
# data-prep/poster_overrides.yaml
my-poster-filename:
  title: "The Correct Title"
  authors: ["Dr. Jane Smith", "Prof. John Doe"]
  tags: ["ai", "robotics"]
  abstract: "Custom abstract..."
```

Re-run extraction and overrides will be applied.

## Performance

Vision models are slower than text extraction:

- **Text extraction**: ~1-2 seconds per poster
- **Vision extraction**: ~10-30 seconds per poster (depending on model)

But the accuracy improvement is worth it!

## Troubleshooting

### "Ollama is not running"

```bash
# Start Ollama in a separate terminal
ollama serve
```

### "No vision models found"

```bash
# Pull a vision model first
ollama pull llama3.2-vision
```

### "Model didn't return valid JSON"

Some models need more specific prompts. Try a different model:

```bash
pixi run python extract_from_pdfs.py ~/posters/ --use-vision --vision-model gemma3
```

### Vision extraction failed

The script will automatically fall back to text extraction. Check:
1. Ollama is running
2. Model is pulled: `ollama list`
3. Image quality is good (not too blurry)

## Best Practices

1. **Use vision for initial extraction** - Get accurate titles from the start
2. **Review the output** - Check `backend/data/posters.json`
3. **Add overrides for edge cases** - Some posters may still need manual fixes
4. **Choose the right model**:
   - Recommended: `gemma3`
   - Alternatives: `llava`, `minicpm-v`

## Integration with Godot

After extraction with vision:

1. Backend already has correct metadata
2. In Godot: **File → Run Script → apply_poster_materials.gd**
3. Titles will be correct automatically!

No more manual title fixes! 🎉
