#!/usr/bin/env python3
"""
DEPRECATED: This script's functionality is now integrated into import_posters.py

Please use import_posters.py for new imports. It provides:
- Unified PDF import workflow
- Smart merging (same as this script)
- Vision-based extraction
- Automatic Godot asset management

For validation:
    python import_posters.py --validate

For CSV/JSON import, use the unified script or integrate your data manually.

This script remains for backward compatibility only.

---

Poster metadata extraction and update script for MAD backend.

This script handles importing poster data from various sources and properly
updating the backend metadata (posters.json) while preserving manually added
fields and tracking update history.

Usage:
    python extract_posters.py --source <csv|json|pdf> --input <file> [--merge]
    python extract_posters.py --validate  # Validate existing posters.json
"""

import argparse
import csv
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PosterMetadataManager:
    """Manages poster metadata extraction, merging, and validation."""

    # Fields that should be preserved during updates (manually curated)
    PRESERVE_FIELDS = {'faq', 'booth_id', 'room', 'related_links'}

    # Required fields for minimal poster entry
    REQUIRED_FIELDS = {'id', 'title', 'authors', 'tags', 'abstract', 'poster_image'}

    def __init__(self, backend_dir: Path):
        self.backend_dir = backend_dir
        self.posters_file = backend_dir / 'posters.json'
        self.schema_file = backend_dir / 'poster_schema.json'

    def load_existing_posters(self) -> Dict[str, Any]:
        """Load existing posters.json or return empty structure."""
        if not self.posters_file.exists():
            logger.info("No existing posters.json found, starting fresh")
            return {
                "schema_version": "1.0",
                "last_updated": datetime.now().isoformat(),
                "posters": []
            }

        try:
            with open(self.posters_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                logger.info(f"Loaded {len(data.get('posters', []))} existing posters")
                return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing existing posters.json: {e}")
            raise

    def save_posters(self, data: Dict[str, Any]) -> None:
        """Save posters data to posters.json with proper formatting."""
        data['last_updated'] = datetime.now().isoformat()

        with open(self.posters_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        logger.info(f"Saved {len(data['posters'])} posters to {self.posters_file}")

    def merge_poster(self, existing: Dict[str, Any], new: Dict[str, Any]) -> Dict[str, Any]:
        """
        Merge new poster data with existing, preserving manually curated fields.

        Strategy:
        - Update basic fields (title, abstract, authors, tags) from new data
        - Preserve manually added fields (faq, booth_id, etc.)
        - Track update timestamp in metadata
        """
        merged = existing.copy()

        # Update basic fields from new data
        for field in ['title', 'abstract', 'authors', 'tags', 'poster_image',
                      'keywords', 'contact_email']:
            if field in new:
                merged[field] = new[field]

        # Preserve manually curated fields from existing
        for field in self.PRESERVE_FIELDS:
            if field in existing and field not in new:
                merged[field] = existing[field]
            elif field in new:
                # If new data has these fields, log a warning but use new data
                logger.warning(f"Updating manually curated field '{field}' for poster {existing.get('id')}")
                merged[field] = new[field]

        # Update metadata tracking
        if 'metadata' not in merged:
            merged['metadata'] = {}

        merged['metadata']['updated_at'] = datetime.now().isoformat()

        # Preserve original creation time
        if 'metadata' in existing and 'created_at' in existing['metadata']:
            merged['metadata']['created_at'] = existing['metadata']['created_at']

        if 'source' in new.get('metadata', {}):
            merged['metadata']['source'] = new['metadata']['source']

        logger.info(f"Merged poster '{merged.get('title', merged.get('id'))}'")
        return merged

    def add_poster(self, poster: Dict[str, Any]) -> Dict[str, Any]:
        """Add metadata tracking to a new poster."""
        if 'metadata' not in poster:
            poster['metadata'] = {}

        now = datetime.now().isoformat()
        poster['metadata']['created_at'] = now
        poster['metadata']['updated_at'] = now

        if 'source' not in poster['metadata']:
            poster['metadata']['source'] = 'unknown'

        logger.info(f"Added new poster '{poster.get('title', poster.get('id'))}'")
        return poster

    def validate_poster(self, poster: Dict[str, Any]) -> bool:
        """Validate that a poster has all required fields."""
        missing = self.REQUIRED_FIELDS - set(poster.keys())
        if missing:
            logger.error(f"Poster {poster.get('id', 'unknown')} missing required fields: {missing}")
            return False
        return True

    def import_from_csv(self, csv_file: Path, merge: bool = True) -> List[Dict[str, Any]]:
        """
        Import posters from CSV file.

        Expected CSV columns:
        - id, title, authors (semicolon-separated), tags (semicolon-separated),
          abstract, poster_image, keywords (semicolon-separated), contact_email
        """
        posters = []

        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            for row in reader:
                # Parse semicolon-separated lists
                authors = [a.strip() for a in row.get('authors', '').split(';') if a.strip()]
                tags = [t.strip() for t in row.get('tags', '').split(';') if t.strip()]
                keywords = [k.strip() for k in row.get('keywords', '').split(';') if k.strip()]

                poster = {
                    'id': row['id'],
                    'title': row['title'],
                    'authors': authors,
                    'tags': tags,
                    'abstract': row['abstract'],
                    'poster_image': row['poster_image'],
                    'metadata': {
                        'source': 'csv_import'
                    }
                }

                if keywords:
                    poster['keywords'] = keywords
                if row.get('contact_email'):
                    poster['contact_email'] = row['contact_email']

                if self.validate_poster(poster):
                    posters.append(poster)
                else:
                    logger.warning(f"Skipping invalid poster from CSV: {row.get('id')}")

        logger.info(f"Imported {len(posters)} posters from CSV")
        return posters

    def import_from_json(self, json_file: Path, merge: bool = True) -> List[Dict[str, Any]]:
        """Import posters from JSON file (array of poster objects)."""
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Handle both array of posters and full posters.json structure
        if isinstance(data, list):
            posters = data
        elif isinstance(data, dict) and 'posters' in data:
            posters = data['posters']
        else:
            logger.error("Invalid JSON format")
            return []

        valid_posters = []
        for poster in posters:
            if 'metadata' not in poster:
                poster['metadata'] = {}
            poster['metadata']['source'] = 'json_import'

            if self.validate_poster(poster):
                valid_posters.append(poster)
            else:
                logger.warning(f"Skipping invalid poster: {poster.get('id')}")

        logger.info(f"Imported {len(valid_posters)} posters from JSON")
        return valid_posters

    def update_backend(self, new_posters: List[Dict[str, Any]], merge: bool = True) -> None:
        """
        Update backend posters.json with new poster data.

        Args:
            new_posters: List of new/updated poster dictionaries
            merge: If True, merge with existing data. If False, replace entirely.
        """
        if merge:
            # Load existing data
            data = self.load_existing_posters()
            existing_map = {p['id']: p for p in data['posters']}

            # Merge or add posters
            updated_posters = []
            for new_poster in new_posters:
                poster_id = new_poster['id']
                if poster_id in existing_map:
                    # Merge with existing
                    merged = self.merge_poster(existing_map[poster_id], new_poster)
                    updated_posters.append(merged)
                    del existing_map[poster_id]
                else:
                    # Add new poster
                    updated_posters.append(self.add_poster(new_poster))

            # Add remaining existing posters that weren't updated
            updated_posters.extend(existing_map.values())

            data['posters'] = updated_posters
        else:
            # Replace entirely
            data = {
                "schema_version": "1.0",
                "posters": [self.add_poster(p) for p in new_posters]
            }

        # Save to backend
        self.save_posters(data)

        logger.info(f"Backend updated successfully with {len(data['posters'])} posters")

    def validate_backend(self) -> bool:
        """Validate the current posters.json file."""
        if not self.posters_file.exists():
            logger.error(f"posters.json not found at {self.posters_file}")
            return False

        try:
            data = self.load_existing_posters()

            if 'posters' not in data:
                logger.error("Missing 'posters' field in posters.json")
                return False

            valid = True
            for idx, poster in enumerate(data['posters']):
                if not self.validate_poster(poster):
                    logger.error(f"Poster at index {idx} failed validation")
                    valid = False

            if valid:
                logger.info(f"✓ Validation passed for {len(data['posters'])} posters")
            else:
                logger.error("✗ Validation failed")

            return valid
        except Exception as e:
            logger.error(f"Validation error: {e}")
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Extract and manage poster metadata for MAD backend'
    )
    parser.add_argument(
        '--source',
        choices=['csv', 'json', 'pdf'],
        help='Source format for import'
    )
    parser.add_argument(
        '--input',
        type=Path,
        help='Input file path'
    )
    parser.add_argument(
        '--merge',
        action='store_true',
        default=True,
        help='Merge with existing posters.json (default: True)'
    )
    parser.add_argument(
        '--replace',
        action='store_true',
        help='Replace existing posters.json entirely'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate existing posters.json'
    )
    parser.add_argument(
        '--backend-dir',
        type=Path,
        default=Path(__file__).parent.parent / 'backend',
        help='Path to backend directory (default: ../backend)'
    )

    args = parser.parse_args()

    # Initialize manager
    manager = PosterMetadataManager(args.backend_dir)

    # Validate mode
    if args.validate:
        success = manager.validate_backend()
        sys.exit(0 if success else 1)

    # Import mode
    if not args.source or not args.input:
        parser.error("--source and --input required for import (or use --validate)")

    if not args.input.exists():
        logger.error(f"Input file not found: {args.input}")
        sys.exit(1)

    # Import based on source type
    if args.source == 'csv':
        posters = manager.import_from_csv(args.input)
    elif args.source == 'json':
        posters = manager.import_from_json(args.input)
    elif args.source == 'pdf':
        logger.error("PDF extraction not yet implemented")
        sys.exit(1)
    else:
        logger.error(f"Unknown source: {args.source}")
        sys.exit(1)

    if not posters:
        logger.error("No valid posters imported")
        sys.exit(1)

    # Update backend
    merge = not args.replace
    manager.update_backend(posters, merge=merge)

    # Validate result
    if manager.validate_backend():
        logger.info("✓ Import completed successfully")
    else:
        logger.error("✗ Import completed but validation failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
