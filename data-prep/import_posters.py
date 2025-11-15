#!/usr/bin/env python3
"""
Unified Poster Import Script for MAD Project
=============================================

This script provides a complete workflow for importing poster PDFs into the MAD project,
ensuring consistency between Godot assets and backend metadata.

Features:
- Converts PDF posters to PNG images for Godot display
- Extracts metadata using vision models (Ollama) or text parsing
- Updates both backend JSON files with consistent metadata
- Smart merging preserves manually curated fields (FAQ, booth assignments, etc.)
- Supports manual overrides via YAML file
- Tracks metadata history and sources

Usage:
    # Import new PDFs with vision extraction (recommended)
    python import_posters.py /path/to/pdfs --use-vision --merge

    # Import without vision (text parsing only)
    python import_posters.py /path/to/pdfs --merge

    # Replace all existing posters
    python import_posters.py /path/to/pdfs --replace

    # Validate existing metadata
    python import_posters.py --validate

Requirements:
    pip install pdf2image pypdf pillow pyyaml requests

    System dependencies:
    - macOS: brew install poppler
    - Linux: sudo apt-get install poppler-utils
    - Ollama (optional, for vision extraction): https://ollama.ai
"""

import json
import re
import argparse
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

try:
    from pdf2image import convert_from_path
    from PIL import Image
    import PyPDF2
    import yaml
except ImportError:
    print("Error: Missing required packages")
    print("Install with: pip install pdf2image pypdf pillow pyyaml")
    print("\nAlso install poppler:")
    print("  macOS: brew install poppler")
    print("  Linux: sudo apt-get install poppler-utils")
    exit(1)

try:
    import requests
    import base64
    VISION_AVAILABLE = True
except ImportError:
    VISION_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PosterImporter:
    """Handles unified poster import workflow."""

    # Fields preserved during updates (manually curated)
    PRESERVE_FIELDS = {'faq', 'booth_id', 'room', 'related_links', 'keywords', 'contact_email'}

    # Required fields for valid poster
    REQUIRED_FIELDS = {'id', 'title', 'authors', 'tags', 'abstract', 'poster_image'}

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.data_prep_dir = project_root / 'data-prep'
        self.backend_dir = project_root / 'backend'
        self.godot_assets_dir = project_root / 'client-godot' / 'assets' / 'posters'

        # Backend JSON files (we maintain both for compatibility)
        self.posters_json = self.backend_dir / 'posters.json'
        self.data_posters_json = self.backend_dir / 'data' / 'posters.json'

        # Override file
        self.overrides_file = self.data_prep_dir / 'poster_overrides.yaml'

    def check_ollama_available(self) -> bool:
        """Check if Ollama is running."""
        if not VISION_AVAILABLE:
            return False
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False

    def extract_metadata_with_vision(self, image_path: Path, model: str = "gemma3:latest") -> Optional[Dict]:
        """Use Ollama vision model to extract metadata from poster image."""
        if not VISION_AVAILABLE:
            return None

        try:
            with open(image_path, "rb") as image_file:
                image_base64 = base64.b64encode(image_file.read()).decode("utf-8")

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
- For tags: Identify 3-5 key research topics/technologies
- For abstract: Summarize the main contribution in 2-3 sentences
- Return ONLY valid JSON

Analyze this poster:"""

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
            return json.loads(response_text)

        except Exception as e:
            logger.warning(f"Vision extraction error: {e}")
            return None

    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract all text from a PDF file."""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except Exception as e:
            logger.error(f"Error extracting text from {pdf_path}: {e}")
            return ""

    def extract_title_from_text(self, lines: List[str], poster_id: str) -> str:
        """Smart title extraction from text lines."""
        if not lines:
            return f"Research Poster {poster_id}"

        skip_patterns = [
            r'rise.*research.*institute',
            r'university',
            r'department',
            r'page \d+',
            r'^\d+$',
        ]

        for line in lines[:10]:
            if any(re.search(pattern, line, re.IGNORECASE) for pattern in skip_patterns):
                continue
            if len(line) < 10 or '@' in line or 'http' in line.lower():
                continue
            if 10 <= len(line) <= 150 and any(c.isupper() for c in line):
                return line

        for line in lines[:5]:
            if len(line) > 10:
                return line[:150] + "..." if len(line) > 150 else line

        return f"Research Poster {poster_id}"

    def parse_poster_content(self, text: str, poster_id: str) -> Dict:
        """Parse extracted text to find metadata (fallback method)."""
        lines = [line.strip() for line in text.split('\n') if line.strip()]

        title = self.extract_title_from_text(lines, poster_id)
        authors = []
        abstract = ""
        tags = []

        # Simple author extraction
        for line in lines[1:5]:
            if re.search(r'[A-Z][a-z]+.*[A-Z][a-z]+', line) and len(line) < 100:
                author_candidates = re.split(r',|and|\s{2,}', line)
                authors.extend([a.strip() for a in author_candidates if a.strip()])

        if not authors:
            authors = ["Unknown Author"]

        # Abstract extraction
        abstract_keywords = ['abstract', 'summary', 'introduction']
        for i, line in enumerate(lines):
            if any(keyword in line.lower() for keyword in abstract_keywords):
                abstract_lines = []
                for j in range(i+1, min(i+10, len(lines))):
                    if len(lines[j]) > 20:
                        abstract_lines.append(lines[j])
                    if len(' '.join(abstract_lines)) > 300:
                        break
                abstract = ' '.join(abstract_lines)
                break

        if not abstract:
            for line in lines[2:]:
                if len(line) > 100:
                    abstract = line[:400] + "..." if len(line) > 400 else line
                    break

        if not abstract:
            abstract = "Research poster content extracted from PDF."

        # Infer tags from keywords
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
            'sustainable': 'sustainability',
            'quantum': 'quantum-computing',
            'federated': 'federated-learning',
            'computer vision': 'computer-vision',
            'nlp': 'nlp',
        }

        text_lower = text.lower()
        for keyword, tag in tech_keywords.items():
            if keyword in text_lower and tag not in tags:
                tags.append(tag)

        if not tags:
            tags = ['research', 'computer-science']

        return {
            'title': title,
            'authors': authors[:3],
            'abstract': abstract,
            'tags': tags[:5]
        }

    def pdf_to_png(self, pdf_path: Path, output_path: Path, dpi: int = 150) -> bool:
        """Convert PDF poster to PNG image."""
        try:
            logger.info(f"Converting {pdf_path.name} to PNG...")
            images = convert_from_path(str(pdf_path), dpi=dpi, first_page=1, last_page=1)

            if not images:
                logger.error(f"No images generated from {pdf_path}")
                return False

            image = images[0]

            # Resize if needed
            max_width = 1200
            if image.width > max_width:
                ratio = max_width / image.width
                new_size = (max_width, int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

            image.save(output_path, 'PNG', optimize=True)
            logger.info(f"✓ Saved PNG to {output_path.name}")
            return True

        except Exception as e:
            logger.error(f"Error converting {pdf_path}: {e}")
            return False

    def load_overrides(self) -> Dict:
        """Load manual overrides from YAML file."""
        if not self.overrides_file.exists():
            return {}

        try:
            with open(self.overrides_file, 'r') as f:
                overrides = yaml.safe_load(f) or {}
            logger.info(f"Loaded {len(overrides)} overrides from {self.overrides_file.name}")
            return overrides
        except Exception as e:
            logger.warning(f"Could not load overrides: {e}")
            return {}

    def apply_overrides(self, content: Dict, pdf_basename: str, overrides: Dict) -> Dict:
        """Apply manual overrides to extracted content."""
        if pdf_basename not in overrides:
            return content

        override = overrides[pdf_basename]

        if isinstance(override, str):
            content['title'] = override
            logger.info(f"✓ Applied title override: {override}")
        elif isinstance(override, dict):
            for field in ['title', 'authors', 'tags', 'abstract']:
                if field in override:
                    content[field] = override[field]
                    logger.info(f"✓ Applied {field} override")

        return content

    def process_pdfs(
        self,
        pdf_dir: Path,
        start_id: int = 1,
        use_vision: bool = False,
        vision_model: str = "gemma3:latest"
    ) -> List[Dict]:
        """Process all PDFs in directory and extract metadata."""

        pdf_files = sorted(pdf_dir.glob("*.pdf"))

        if not pdf_files:
            logger.warning(f"No PDF files found in {pdf_dir}")
            return []

        logger.info(f"Found {len(pdf_files)} PDF files")
        if use_vision:
            logger.info(f"Using vision model: {vision_model}")

        overrides = self.load_overrides()
        posters = []

        for idx, pdf_path in enumerate(pdf_files, start=start_id):
            poster_id = f"poster_{idx:03d}"
            pdf_basename = pdf_path.stem
            logger.info(f"\n{'='*60}")
            logger.info(f"Processing {pdf_path.name} → {poster_id}")

            # Convert to PNG
            png_path = self.godot_assets_dir / f"{poster_id}.png"
            success = self.pdf_to_png(pdf_path, png_path)

            if not success:
                logger.warning(f"PNG conversion failed for {pdf_path.name}")
                continue

            # Extract metadata
            content = None

            if use_vision and success:
                logger.info("Using vision model for metadata extraction...")
                content = self.extract_metadata_with_vision(png_path, vision_model)

                if content:
                    logger.info(f"✓ Vision extraction successful")
                    logger.info(f"  Title: {content.get('title', 'N/A')[:60]}")
                else:
                    logger.warning("Vision extraction failed, falling back to text parsing")

            if not content:
                text = self.extract_text_from_pdf(pdf_path)
                content = self.parse_poster_content(text, poster_id)

            # Apply manual overrides
            content = self.apply_overrides(content, pdf_basename, overrides)

            # Create poster metadata
            poster = {
                'id': poster_id,
                'title': content['title'],
                'authors': content['authors'],
                'tags': content['tags'],
                'abstract': content['abstract'],
                'poster_image': f'res://assets/posters/{poster_id}.png',
                'metadata': {
                    'source': 'pdf_import',
                    'source_file': pdf_path.name,
                    'created_at': datetime.now().isoformat(),
                    'updated_at': datetime.now().isoformat()
                }
            }

            posters.append(poster)
            logger.info(f"✓ Metadata extracted:")
            logger.info(f"  Title: {content['title'][:60]}...")
            logger.info(f"  Authors: {', '.join(content['authors'])}")
            logger.info(f"  Tags: {', '.join(content['tags'])}")

        logger.info(f"\n{'='*60}")
        logger.info(f"✓ Processed {len(posters)} posters")
        return posters

    def load_existing_backend(self, json_path: Path) -> Dict:
        """Load existing backend JSON."""
        if not json_path.exists():
            logger.info(f"No existing file at {json_path}, starting fresh")
            return {
                "schema_version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "posters": []
            }

        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                # Normalize to structured format
                if isinstance(data, list):
                    data = {
                        "schema_version": "1.0",
                        "last_updated": datetime.now().isoformat(),
                        "posters": data
                    }

                logger.info(f"Loaded {len(data.get('posters', []))} existing posters from {json_path.name}")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing {json_path}: {e}")
            raise

    def merge_poster(self, existing: Dict, new: Dict) -> Dict:
        """
        Merge new poster data with existing, preserving manually curated fields.
        """
        merged = existing.copy()

        # Update basic fields from new data
        for field in ['title', 'abstract', 'authors', 'tags', 'poster_image']:
            if field in new:
                merged[field] = new[field]

        # Preserve manually curated fields
        for field in self.PRESERVE_FIELDS:
            if field in existing and field not in new:
                merged[field] = existing[field]
            elif field in new:
                logger.warning(f"Updating manually curated field '{field}' for {existing.get('id')}")
                merged[field] = new[field]

        # Update metadata tracking
        if 'metadata' not in merged:
            merged['metadata'] = {}

        merged['metadata']['updated_at'] = datetime.now().isoformat()

        # Preserve creation time
        if 'metadata' in existing and 'created_at' in existing['metadata']:
            merged['metadata']['created_at'] = existing['metadata']['created_at']
        else:
            merged['metadata']['created_at'] = datetime.now().isoformat()

        if 'metadata' in new:
            for key in ['source', 'source_file']:
                if key in new['metadata']:
                    merged['metadata'][key] = new['metadata'][key]

        logger.info(f"Merged poster: {merged.get('title', merged.get('id'))}")
        return merged

    def validate_poster(self, poster: Dict) -> bool:
        """Validate poster has required fields."""
        missing = self.REQUIRED_FIELDS - set(poster.keys())
        if missing:
            logger.error(f"Poster {poster.get('id', 'unknown')} missing: {missing}")
            return False
        return True

    def update_backend(self, new_posters: List[Dict], merge: bool = True) -> None:
        """
        Update both backend JSON files with new poster data.

        Maintains two files for compatibility:
        - backend/posters.json (structured format with metadata)
        - backend/data/posters.json (simple array format)
        """

        # Update backend/posters.json (structured format)
        data = self.load_existing_backend(self.posters_json)

        if merge:
            existing_map = {p['id']: p for p in data['posters']}
            updated_posters = []

            for new_poster in new_posters:
                poster_id = new_poster['id']
                if poster_id in existing_map:
                    merged = self.merge_poster(existing_map[poster_id], new_poster)
                    updated_posters.append(merged)
                    del existing_map[poster_id]
                else:
                    updated_posters.append(new_poster)
                    logger.info(f"Added new poster: {new_poster.get('title')}")

            # Keep existing posters not in update
            updated_posters.extend(existing_map.values())
            data['posters'] = updated_posters
        else:
            data['posters'] = new_posters

        # Update timestamp
        data['last_updated'] = datetime.now().isoformat()

        # Save structured format
        self.posters_json.parent.mkdir(parents=True, exist_ok=True)
        with open(self.posters_json, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Updated {self.posters_json}")

        # Save simple array format for compatibility
        self.data_posters_json.parent.mkdir(parents=True, exist_ok=True)
        with open(self.data_posters_json, 'w', encoding='utf-8') as f:
            json.dump(data['posters'], f, indent=2, ensure_ascii=False)
        logger.info(f"✓ Updated {self.data_posters_json}")

        logger.info(f"\n✓ Backend updated with {len(data['posters'])} posters")

    def validate_backend(self) -> bool:
        """Validate existing backend metadata."""
        logger.info("Validating backend metadata...")

        valid = True

        # Check both files exist and are consistent
        for json_path in [self.posters_json, self.data_posters_json]:
            if not json_path.exists():
                logger.error(f"Missing: {json_path}")
                valid = False
                continue

            try:
                data = self.load_existing_backend(json_path)
                posters = data.get('posters', [])

                for poster in posters:
                    if not self.validate_poster(poster):
                        valid = False

                    # Check Godot asset exists
                    poster_id = poster.get('id')
                    if poster_id:
                        png_path = self.godot_assets_dir / f"{poster_id}.png"
                        if not png_path.exists():
                            logger.warning(f"Missing Godot asset: {png_path}")
                            valid = False

                if valid:
                    logger.info(f"✓ {json_path.name}: {len(posters)} posters validated")

            except Exception as e:
                logger.error(f"Validation error for {json_path}: {e}")
                valid = False

        return valid


def main():
    parser = argparse.ArgumentParser(
        description='Unified poster import script for MAD project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        'pdf_directory',
        nargs='?',
        type=Path,
        help='Directory containing poster PDFs'
    )

    parser.add_argument(
        '--merge',
        action='store_true',
        default=True,
        help='Merge with existing metadata (default: True)'
    )

    parser.add_argument(
        '--replace',
        action='store_true',
        help='Replace all existing metadata'
    )

    parser.add_argument(
        '--start-id',
        type=int,
        default=1,
        help='Starting poster ID number (default: 1)'
    )

    parser.add_argument(
        '--use-vision',
        action='store_true',
        help='Use Ollama vision model for metadata extraction'
    )

    parser.add_argument(
        '--vision-model',
        type=str,
        default='gemma3:latest',
        help='Vision model to use (default: gemma3:latest)'
    )

    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing backend metadata'
    )

    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='Project root directory (default: parent of script)'
    )

    args = parser.parse_args()

    # Initialize importer
    importer = PosterImporter(args.project_root)

    # Validate mode
    if args.validate:
        success = importer.validate_backend()
        exit(0 if success else 1)

    # Import mode
    if not args.pdf_directory:
        parser.error("pdf_directory required (or use --validate)")

    if not args.pdf_directory.exists():
        logger.error(f"PDF directory not found: {args.pdf_directory}")
        exit(1)

    # Check vision requirements
    if args.use_vision:
        if not VISION_AVAILABLE:
            logger.error("--use-vision requires 'requests' package")
            logger.error("Install with: pip install requests")
            exit(1)

        if not importer.check_ollama_available():
            logger.error("--use-vision requires Ollama to be running")
            logger.error("\nPlease start Ollama:")
            logger.error("  1. Install from https://ollama.ai")
            logger.error("  2. Run: ollama serve")
            logger.error("  3. Pull a vision model: ollama pull gemma3")
            exit(1)

        logger.info(f"✓ Vision mode enabled with model: {args.vision_model}")

    # Create output directories
    importer.godot_assets_dir.mkdir(parents=True, exist_ok=True)

    # Process PDFs
    new_posters = importer.process_pdfs(
        args.pdf_directory,
        start_id=args.start_id,
        use_vision=args.use_vision,
        vision_model=args.vision_model
    )

    if not new_posters:
        logger.error("No posters imported")
        exit(1)

    # Update backend
    merge_mode = not args.replace
    importer.update_backend(new_posters, merge=merge_mode)

    # Validate
    if importer.validate_backend():
        logger.info("\n" + "="*60)
        logger.info("✓ Import completed successfully!")
        logger.info("="*60)
        logger.info(f"\nImported {len(new_posters)} posters")
        logger.info(f"Godot assets: {importer.godot_assets_dir}")
        logger.info(f"Backend JSON: {importer.posters_json}")
        logger.info(f"             {importer.data_posters_json}")
        logger.info("\nNext steps:")
        logger.info("1. Review metadata in backend/posters.json")
        logger.info("2. Add FAQs and booth assignments as needed")
        logger.info("3. Restart backend: pixi run dev")
        logger.info("4. In Godot: Run scripts/apply_poster_materials.gd")
        logger.info("5. Test in game!")
    else:
        logger.error("\n✗ Import completed but validation failed")
        exit(1)


if __name__ == "__main__":
    main()
