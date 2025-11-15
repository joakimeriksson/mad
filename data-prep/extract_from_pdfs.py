"""
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
except ImportError:
    print("Error: Missing required packages")
    print("Install with: pip install pdf2image pypdf pillow")
    print("\nAlso install poppler:")
    print("  macOS: brew install poppler")
    print("  Linux: sudo apt-get install poppler-utils")
    exit(1)


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


def parse_poster_content(text: str, poster_id: str) -> Dict:
    """
    Parse extracted text to find title, authors, abstract, etc.
    This is a basic heuristic parser - you may need to customize for your PDFs.
    """
    lines = [line.strip() for line in text.split('\n') if line.strip()]

    # Try to identify components (this is heuristic and may need adjustment)
    title = lines[0] if lines else f"Research Poster {poster_id}"

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
    start_id: int = 1
) -> List[Dict]:
    """Process all PDFs in a directory."""

    pdf_files = sorted(pdf_dir.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return []

    print(f"Found {len(pdf_files)} PDF files")
    print("=" * 60)

    posters = []

    for idx, pdf_path in enumerate(pdf_files, start=start_id):
        poster_id = f"poster_{idx:03d}"
        print(f"\nProcessing {pdf_path.name} → {poster_id}")

        # Extract text
        text = extract_text_from_pdf(pdf_path)
        if not text:
            print(f"  Warning: No text extracted, using defaults")

        # Parse content
        content = parse_poster_content(text, poster_id)

        # Convert to PNG
        png_path = output_images_dir / f"{poster_id}.png"
        success = pdf_to_png(pdf_path, png_path)

        if not success:
            print(f"  Warning: PNG conversion failed")

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

    args = parser.parse_args()

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

    # Process PDFs
    new_posters = process_poster_pdfs(pdf_dir, output_json, output_images_dir, args.start_id)

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
