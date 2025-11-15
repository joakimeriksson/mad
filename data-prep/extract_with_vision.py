#!/usr/bin/env python3
"""
Extract poster metadata using Ollama vision models.

This script uses a vision-capable LLM (like llama3.2-vision) to read poster
images and extract metadata like title, authors, abstract, and tags.

Much more accurate than text-based extraction!

Usage:
    python extract_with_vision.py ~/my-posters/
    python extract_with_vision.py ~/my-posters/ --model llama3.2-vision:latest
"""

import json
import base64
import requests
from pathlib import Path
from typing import Dict, List, Optional
import argparse
import sys

try:
    from PIL import Image
    import yaml
except ImportError:
    print("Error: Missing required packages")
    print("Install with: pixi install")
    exit(1)


def check_ollama_available() -> bool:
    """Check if Ollama is running and accessible."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        return response.status_code == 200
    except:
        return False


def get_available_vision_models() -> List[str]:
    """Get list of available vision models from Ollama."""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            # Filter for vision-capable models
            vision_keywords = ["vision", "llava", "bakllava", "minicpm"]
            vision_models = [
                m["name"] for m in models
                if any(keyword in m["name"].lower() for keyword in vision_keywords)
            ]
            return vision_models
        return []
    except:
        return []


def encode_image_base64(image_path: Path) -> str:
    """Encode image to base64 string."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def extract_metadata_from_image(image_path: Path, model: str = "llama3.2-vision:latest") -> Dict:
    """
    Use Ollama vision model to extract metadata from poster image.

    Args:
        image_path: Path to poster PNG image
        model: Ollama vision model to use

    Returns:
        Dictionary with title, authors, tags, abstract
    """

    # Encode image
    image_base64 = encode_image_base64(image_path)

    # Craft prompt for structured extraction
    prompt = """You are analyzing a research poster image. Extract the following information in JSON format:

{
  "title": "The main title of the poster",
  "authors": ["Author 1", "Author 2", "..."],
  "tags": ["topic1", "topic2", "topic3"],
  "abstract": "A brief summary of what the poster is about (2-3 sentences)"
}

Rules:
- For title: Extract ONLY the main title, not institution names or headers
- For authors: List all author names you can clearly read
- For tags: Identify 3-5 key research topics or keywords
- For abstract: Summarize the main research contribution in 2-3 sentences
- Return ONLY valid JSON, no additional text

Analyze the poster and extract the metadata:"""

    # Call Ollama API
    try:
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": model,
                "prompt": prompt,
                "images": [image_base64],
                "stream": False,
                "format": "json"  # Request JSON response
            },
            timeout=60  # Vision models can be slow
        )

        if response.status_code != 200:
            print(f"  Error: Ollama API returned {response.status_code}")
            return None

        result = response.json()
        response_text = result.get("response", "")

        # Parse JSON response
        try:
            metadata = json.loads(response_text)
            return metadata
        except json.JSONDecodeError:
            print(f"  Warning: Model didn't return valid JSON")
            print(f"  Response: {response_text[:200]}")
            return None

    except requests.exceptions.Timeout:
        print(f"  Error: Request timed out (vision models can be slow)")
        return None
    except Exception as e:
        print(f"  Error calling Ollama: {e}")
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


def process_poster_images(
    images_dir: Path,
    output_json: Path,
    model: str,
    start_id: int = 1,
    overrides: Optional[Dict] = None
) -> List[Dict]:
    """Process all poster images in a directory using vision model."""

    image_files = sorted(images_dir.glob("*.png")) + sorted(images_dir.glob("*.jpg"))

    if not image_files:
        print(f"No image files found in {images_dir}")
        return []

    print(f"Found {len(image_files)} poster images")
    if overrides:
        print(f"Using {len(overrides)} manual overrides")
    print(f"Using vision model: {model}")
    print("=" * 60)

    posters = []

    for idx, image_path in enumerate(image_files, start=start_id):
        poster_id = f"poster_{idx:03d}"
        image_basename = image_path.stem
        print(f"\nProcessing {image_path.name} → {poster_id}")

        # Extract metadata using vision model
        metadata = extract_metadata_from_image(image_path, model)

        if not metadata:
            print(f"  ⚠ Vision extraction failed, using defaults")
            metadata = {
                "title": f"Research Poster {poster_id}",
                "authors": [],
                "tags": [],
                "abstract": ""
            }
        else:
            print(f"  ✓ Extracted title: {metadata.get('title', 'N/A')}")
            print(f"  ✓ Authors: {len(metadata.get('authors', []))} found")
            print(f"  ✓ Tags: {', '.join(metadata.get('tags', [])[:3])}")

        # Apply manual overrides if available
        if overrides and image_basename in overrides:
            override = overrides[image_basename]
            if isinstance(override, str):
                metadata['title'] = override
                print(f"  ✓ Applied title override: {override}")
            elif isinstance(override, dict):
                if 'title' in override:
                    metadata['title'] = override['title']
                    print(f"  ✓ Applied title override: {override['title']}")
                if 'authors' in override:
                    metadata['authors'] = override['authors']
                if 'tags' in override:
                    metadata['tags'] = override['tags']
                if 'abstract' in override:
                    metadata['abstract'] = override['abstract']

        # Create poster entry
        poster = {
            "id": poster_id,
            "title": metadata.get("title", f"Research Poster {poster_id}"),
            "authors": metadata.get("authors", []),
            "tags": metadata.get("tags", []),
            "room": "corridor",
            "booth_id": f"booth_{idx}",
            "abstract": metadata.get("abstract", ""),
            "poster_image": f"res://assets/posters/{poster_id}.png",
            "faq": []
        }

        posters.append(poster)

    return posters


def main():
    parser = argparse.ArgumentParser(
        description="Extract poster metadata using Ollama vision models"
    )
    parser.add_argument(
        "images_dir",
        type=Path,
        help="Directory containing poster images (PNG/JPG)"
    )
    parser.add_argument(
        "--model",
        default="llama3.2-vision:latest",
        help="Ollama vision model to use (default: llama3.2-vision:latest)"
    )
    parser.add_argument(
        "--start-id",
        type=int,
        default=1,
        help="Starting poster ID number (default: 1)"
    )
    parser.add_argument(
        "--merge",
        action="store_true",
        help="Merge with existing posters.json instead of replacing"
    )

    args = parser.parse_args()

    # Setup paths
    script_dir = Path(__file__).parent
    backend_data = script_dir.parent / "backend" / "data"
    output_json = backend_data / "posters.json"

    # Check Ollama
    if not check_ollama_available():
        print("❌ Error: Ollama is not running!")
        print("\nPlease start Ollama first:")
        print("  1. Install Ollama from https://ollama.ai")
        print("  2. Run: ollama serve")
        print("  3. Pull a vision model: ollama pull llama3.2-vision")
        sys.exit(1)

    # Check for vision models
    available_models = get_available_vision_models()
    if not available_models:
        print("⚠ Warning: No vision models found in Ollama")
        print("\nPlease pull a vision model:")
        print("  ollama pull llama3.2-vision")
        print("  # or")
        print("  ollama pull llava")
        print("\nAvailable vision models:")
        print("  - llama3.2-vision (recommended, 11B)")
        print("  - llama3.2-vision:90b (more accurate, slower)")
        print("  - llava (alternative)")
        sys.exit(1)

    print(f"✓ Ollama is running")
    print(f"✓ Available vision models: {', '.join(available_models)}")

    # Validate input
    images_dir = args.images_dir
    if not images_dir.exists():
        print(f"Error: Images directory not found: {images_dir}")
        sys.exit(1)

    # Load overrides
    overrides_file = script_dir / "poster_overrides.yaml"
    overrides = load_overrides(overrides_file)

    # Process images
    new_posters = process_poster_images(
        images_dir,
        output_json,
        args.model,
        args.start_id,
        overrides
    )

    if not new_posters:
        print("No posters to save")
        return

    # Load existing posters if merging
    existing_posters = []
    if args.merge and output_json.exists():
        with open(output_json, 'r') as f:
            existing_posters = json.load(f)
        print(f"\nMerging with {len(existing_posters)} existing posters")

    # Combine and save
    all_posters = existing_posters + new_posters

    # Create output directory
    output_json.parent.mkdir(parents=True, exist_ok=True)

    with open(output_json, 'w') as f:
        json.dump(all_posters, f, indent=2)

    print("\n" + "=" * 60)
    print(f"✓ Saved {len(new_posters)} posters to {output_json}")
    print(f"✓ Total posters: {len(all_posters)}")
    print("\nNext steps:")
    print("1. Review the extracted data (titles especially)")
    print("2. Add manual overrides if needed in poster_overrides.yaml")
    print("3. Restart backend: cd ../backend && pixi run dev")
    print("4. In Godot: File → Run Script → apply_poster_materials.gd")


if __name__ == "__main__":
    main()
