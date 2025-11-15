"""
DEPRECATED: This script is superseded by import_posters.py

Please use import_posters.py for new imports. It provides:
- Smart merging with existing metadata
- Vision-based extraction (optional)
- Better consistency between Godot and backend
- Preservation of manually curated fields

Usage:
    python import_posters.py /path/to/pdfs --use-vision --merge

This script remains for backward compatibility only.

---

Extract poster content from PDFs for MAD project.

This script:
1. Converts PDF posters to PNG images for Godot display
2. Extracts text content for agent knowledge (title, authors, abstract)
3. Updates posters.json with the extracted metadata

Requirements:
    pip install pdf2image pypdf pillow

    On macOS: brew install poppler
    On Linux: sudo apt-get install poppler-utils
    On Windows: Download poppler binaries
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional
import argparse

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import PyPDF2
    import yaml
except ImportError:
    print("Error: Missing required packages")
    print("Install with: pixi add pyyaml")
    print("Or: pip install pdf2image pypdf pillow pyyaml")
    print("\nAlso install poppler:")
    print("  macOS: brew install poppler")
    print("  Linux: sudo apt-get install poppler-utils")
    exit(1)

# Optional: vision-based extraction
try:
    import requests
    import base64
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False


def check_ollama_available() -> bool:
    """Check if Ollama is running."""
    if not VISION_AVAILABLE:
        return False
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def extract_metadata_with_vision(image_path: Path, model: str = "gemma3:latest") -> Optional[Dict]:
    """Use Ollama vision model to extract metadata from poster image."""
    if not VISION_AVAILABLE:
        return None

    try:
        # Encode image
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

        # Prompt for structured extraction
        prompt = """You are analyzing a research poster image. Extract the following information in JSON format:

{
  "title": "The main title of the poster",
  "authors": ["Author 1", "Author 2"],
  "tags": ["topic1", "topic2", "topic3"],
  "abstract": "A brief summary (2-3 sentences)"
}

Rules:
- For title: Extract ONLY the main title, not institution names
- For authors: List all author names you can clearly read
- For tags: Identify 3-5 key research topics
- For abstract: Summarize the main contribution in 2-3 sentences
- Return ONLY valid JSON

Analyze this poster:"""

        # Call Ollama API
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "format": "json"
            },
            timeout=60
        )

        if response.status_code != 200:
            return None

        result = response.json()
        response_text = result.get("response", "")

        # Parse JSON
        return json.loads(response_text)

    except Exception as e:
        print(f"  Vision extraction error: {e}")
        return None


def load_overrides(overrides_file: Path) -> Dict:
    """Load manual overrides from YAML file."""
    if not overrides_file.exists():
        return {}

    try:
        with open(overrides_file, 'r') as f:
            overrides = yaml.safe_load(f) or {}
        print(f"Loaded {len(overrides)} overrides from {overrides_file}")
        return overrides
    except Exception as e:
        print(f"Warning: Could not load overrides: {e}")
        return {}


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Extract all text from a PDF file."""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {e}")
        return ""


def extract_title_smartly(lines: List[str], poster_id: str) -> str:
    """
    Smarter title extraction with multiple strategies.
    """
    if not lines:
        return f"Research Poster {poster_id}"

    # Strategy 1: Skip common headers/footers
    skip_patterns = [
        r'rise.*research.*institute',
        r'university',
        r'department',
        r'page \d+',
        r'^\d+$',  # Just numbers
    ]

    for i, line in enumerate(lines[:10]):  # Check first 10 lines
        # Skip if matches skip patterns
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
            continue

        # Skip very short lines (likely not titles)
        if len(line) < 10:
            continue

        # Skip lines that look like URLs or emails
        if '@' in line or 'http' in line.lower():
            continue

        # Good title candidate:
        # - Not too short, not too long (10-150 chars)
        # - Has capital letters
        # - Doesn't match skip patterns
        if 10 <= len(line) <= 150 and any(c.isupper() for c in line):
            return line

    # Fallback: use first non-trivial line
    for line in lines[:5]:
        if len(line) > 10:
            # Truncate if too long
            if len(line) > 150:
                return line[:150] + "..."
            return line

    return f"Research Poster {poster_id}"


def parse_poster_content(text: str, poster_id: str, pdf_filename: str = "") -> Dict:
    """
    Parse extracted text to find title, authors, abstract, etc.
    This is a basic heuristic parser - you may need to customize for your PDFs.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Use smarter title extraction
    title = extract_title_smartly(lines, poster_id)
    print(f"  Extracted title: {title[:60]}..." if len(title) > 60 else f"  Extracted title: {title}")

    # Look for common patterns
    authors = []
    abstract = ""
    tags = []

    # Simple heuristic: authors often appear in first few lines
    # Look for names (capitalized words with possible middle initials)
    for i, line in enumerate(lines[1:5], 1):
        # Check if line looks like author names (has capitalized words, commas, etc.)
        if re.search(r'[A-Z][a-z]+.*[A-Z][a-z]+', line) and len(line) < 100:
            # Split by common separators
            author_candidates = re.split(r',|and|\s{2,}', line)
            authors.extend([a.strip() for a in author_candidates if a.strip()])

    if not authors:
        authors = ["Unknown Author"]

    # Look for abstract/summary section
    abstract_keywords = ['abstract', 'summary', 'introduction']
    for i, line in enumerate(lines):
        if any(keyword in line.lower() for keyword in abstract_keywords):
            # Take next few lines as abstract
            abstract_lines = []
            for j in range(i+1, min(i+10, len(lines))):
                if len(lines[j]) > 20:  # Skip short lines
                    abstract_lines.append(lines[j])
                if len(' '.join(abstract_lines)) > 300:  # Limit length
                    break
            abstract = ' '.join(abstract_lines)
            break

    if not abstract:
        # Fallback: use first substantial paragraph
        for line in lines[2:]:
            if len(line) > 100:
                abstract = line[:400] + "..." if len(line) > 400 else line
                break

    if not abstract:
        abstract = "Research poster content extracted from PDF."

    # Try to infer tags from text (very basic)
    tech_keywords = {
        'ai': 'artificial-intelligence',
        'machine learning': 'machine-learning',
        'deep learning': 'deep-learning',
        'neural network': 'neural-networks',
        'robot': 'robotics',
        'iot': 'iot',
        'edge': 'edge-computing',
        'security': 'security',
        'privacy': 'privacy',
        'healthcare': 'healthcare',
        'medical': 'healthcare',
        'sustainable': 'sustainability',
        'energy': 'energy',
        'quantum': 'quantum-computing',
        'federated': 'federated-learning',
        'computer vision': 'computer-vision',
        'nlp': 'nlp',
        'natural language': 'nlp',
    }

    text_lower = text.lower()
    for keyword, tag in tech_keywords.items():
        if keyword in text_lower and tag not in tags:
            tags.append(tag)

    if not tags:
        tags = ['research', 'computer-science']

    return {
        'title': title,
        'authors': authors[:3],  # Limit to 3 authors
        'abstract': abstract,
        'tags': tags[:5]  # Limit to 5 tags
    }


def pdf_to_png(pdf_path: Path, output_path: Path, dpi: int = 150) -> bool:
    """Convert PDF poster to PNG image."""
    try:
        print(f"Converting {pdf_path.name} to PNG...")

        # Convert PDF to images (usually just first page for posters)
        images = convert_from_path(str(pdf_path), dpi=dpi, first_page=1, last_page=1)

        if not images:
            print(f"  Error: No images generated from {pdf_path}")
            return False

        # Get the first (and usually only) page
        image = images[0]

        # Optionally resize to standard size
        max_width = 1200
        if image.width > max_width:
            ratio = max_width / image.width
            new_size = (max_width, int(image.height * ratio))
            image = image.resize(new_size, Image.Resampling.LANCZOS)

        # Save as PNG
        image.save(output_path, 'PNG', optimize=True)
        print(f"  ✓ Saved to {output_path}")
        return True

    except Exception as e:
        print(f"  Error converting {pdf_path}: {e}")
        return False


def process_poster_pdfs(
    pdf_dir: Path,
    output_json: Path,
    output_images_dir: Path,
    start_id: int = 1,
    overrides: Optional[Dict] = None,
    use_vision: bool = False,
    vision_model: str = "gemma3:latest"
) -> List[Dict]:
    """Process all PDFs in a directory."""

    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return []

    print(f"Found {len(pdf_files)} PDF files")
    if overrides:
        print(f"Using {len(overrides)} manual overrides")
    if use_vision:
        print(f"Using vision model: {vision_model}")
    print("=" * 60)

    posters = []

    for idx, pdf_path in enumerate(pdf_files, start=start_id):
        poster_id = f"poster_{idx:03d}"
        pdf_basename = pdf_path.stem  # filename without .pdf
        print(f"\nProcessing {pdf_path.name} → {poster_id}")

        # Convert to PNG first (needed for both modes)
        png_path = output_images_dir / f"{poster_id}.png"
        success = pdf_to_png(pdf_path, png_path)

        if not success:
            print(f"  Warning: PNG conversion failed")

        # Extract metadata - use vision if enabled, otherwise text parsing
        if use_vision and success:
            print(f"  Using vision model to extract metadata...")
            vision_metadata = extract_metadata_with_vision(png_path, vision_model)
            if vision_metadata:
                content = vision_metadata
                print(f"  ✓ Vision extraction successful")
                print(f"  Title: {content.get('title', 'N/A')[:60]}")
            else:
                print(f"  ⚠ Vision extraction failed, falling back to text parsing")
                text = extract_text_from_pdf(pdf_path)
                content = parse_poster_content(text, poster_id, pdf_basename)
        else:
            # Traditional text extraction
            text = extract_text_from_pdf(pdf_path)
            if not text:
                print(f"  Warning: No text extracted, using defaults")
            content = parse_poster_content(text, poster_id, pdf_basename)

        # Apply manual overrides if available
        if overrides and pdf_basename in overrides:
            override = overrides[pdf_basename]
            if isinstance(override, str):
                # Simple case: just a title override
                content['title'] = override
                print(f"  ✓ Applied title override: {override}")
            elif isinstance(override, dict):
                # Full override with multiple fields
                if 'title' in override:
                    content['title'] = override['title']
                    print(f"  ✓ Applied title override: {override['title']}")
                if 'authors' in override:
                    content['authors'] = override['authors']
                if 'tags' in override:
                    content['tags'] = override['tags']
                if 'abstract' in override:
                    content['abstract'] = override['abstract']

        # Create poster metadata
        poster = {
            'id': poster_id,
            'title': content['title'],
            'authors': content['authors'],
            'tags': content['tags'],
            'room': 'corridor',  # Default, can customize
            'booth_id': f'booth_{idx}',
            'abstract': content['abstract'],
            'poster_image': f'res://assets/posters/{poster_id}.png',
            'source_pdf': pdf_path.name,
            'faq': [
                {
                    'question': 'Where can I read more?',
                    'answer': 'Please refer to the full paper or contact the authors for more details.'
                }
            ]
        }

        posters.append(poster)

        print(f"  ✓ Metadata extracted:")
        print(f"    Title: {content['title'][:50]}...")
        print(f"    Authors: {', '.join(content['authors'])}")
        print(f"    Tags: {', '.join(content['tags'])}")

    print("\n" + "=" * 60)
    print(f"✓ Processed {len(posters)} posters")

    return posters


def main():
    parser = argparse.ArgumentParser(
        description='Extract poster content from PDFs for MAD project'
    )
    parser.add_argument(
        'pdf_directory',
        type=str,
        help='Directory containing poster PDFs'
    )
    parser.add_argument(
        '--output-json',
        type=str,
        default='../backend/data/posters.json',
        help='Output JSON file (default: ../backend/data/posters.json)'
    )
    parser.add_argument(
        '--output-images',
        type=str,
        default='../client-godot/assets/posters',
        help='Output directory for PNG images (default: ../client-godot/assets/posters)'
    )
    parser.add_argument(
        '--start-id',
        type=int,
        default=1,
        help='Starting ID number (default: 1)'
    )
    parser.add_argument(
        '--merge',
        action='store_true',
        help='Merge with existing posters.json instead of replacing'
    )
    parser.add_argument(
        '--use-vision',
        action='store_true',
        help='Use Ollama vision model for extraction (more accurate titles/metadata)'
    )
    parser.add_argument(
        '--vision-model',
        type=str,
        default='gemma3:latest',
        help='Vision model to use with Ollama (default: gemma3:latest)'
    )

    args = parser.parse_args()

    # Validate vision settings
    if args.use_vision:
        if not VISION_AVAILABLE:
            print("Error: --use-vision requires 'requests' package")
            print("Install with: pip install requests")
            return

        if not check_ollama_available():
            print("Error: --use-vision requires Ollama to be running")
            print("\nPlease start Ollama:")
            print("  1. Install from https://ollama.ai")
            print("  2. Run: ollama serve")
            print("  3. Pull a vision model:")
            print("     ollama pull gemma3    (recommended)")
            print("     ollama pull llava")
            return

        print(f"✓ Vision mode enabled with model: {args.vision_model}")

    # Setup paths
    script_dir = Path(__file__).parent
    pdf_dir = Path(args.pdf_directory)
    output_json = script_dir / args.output_json
    output_images_dir = script_dir / args.output_images

    if not pdf_dir.exists():
        print(f"Error: PDF directory not found: {pdf_dir}")
        return

    # Create output directories
    output_json.parent.mkdir(parents=True, exist_ok=True)
    output_images_dir.mkdir(parents=True, exist_ok=True)

    # Load manual overrides if file exists
    overrides_file = script_dir / "poster_overrides.yaml"
    overrides = load_overrides(overrides_file)

    # Process PDFs
    new_posters = process_poster_pdfs(
        pdf_dir,
        output_json,
        output_images_dir,
        args.start_id,
        overrides,
        use_vision=args.use_vision,
        vision_model=args.vision_model
    )

    if not new_posters:
        print("No posters to save")
        return

    # Load existing posters if merging
    existing_posters = []
    if args.merge and output_json.exists():
        try:
            with open(output_json, 'r') as f:
                existing_posters = json.load(f)
            print(f"\nMerging with {len(existing_posters)} existing posters")
        except Exception as e:
            print(f"Warning: Could not load existing posters: {e}")

    # Combine posters
    all_posters = existing_posters + new_posters

    # Save to JSON
    with open(output_json, 'w') as f:
        json.dump(all_posters, f, indent=2)

    print(f"\n✓ Saved {len(all_posters)} posters to {output_json}")
    print(f"✓ Saved {len(new_posters)} images to {output_images_dir}")

    print("\nNext steps:")
    print("1. Review and edit posters.json to refine metadata")
    print("2. Restart backend: pixi run dev")
    print("3. In Godot: Run scripts/apply_poster_materials.gd")
    print("4. Run the game to see your posters!")


if __name__ == "__main__":
    main()
