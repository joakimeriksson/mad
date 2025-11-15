# Poster Data Preparation for MAD

This directory contains tools for extracting, managing, and updating poster metadata for the Multi-Agent Dungeon (MAD) backend.

## Overview

The poster import system is designed to:
- **Import** poster data from multiple sources (CSV, JSON, PDF)
- **Merge** new data with existing metadata intelligently
- **Preserve** manually curated fields (FAQs, booth assignments, etc.)
- **Track** metadata updates with timestamps and source information
- **Validate** data integrity before updating the backend

## Key Improvements

The import script addresses common metadata update issues:

1. **Smart Merging**: When updating existing posters, manually added fields (FAQs, booth_id, room assignments) are preserved
2. **Update Tracking**: Every poster tracks when it was created and last updated, plus the data source
3. **Validation**: Required fields are validated before import
4. **Flexible Sources**: Support for CSV, JSON, and (future) PDF extraction
5. **Atomic Updates**: Backend is only updated after successful validation

## Files

- `extract_posters.py` - Main import script
- `example_posters.csv` - Example CSV format for bulk import
- `README.md` - This file

## Usage

### 1. Import from CSV

```bash
cd data-prep
python extract_posters.py --source csv --input example_posters.csv --merge
```

This will:
- Read posters from the CSV file
- Merge with existing `backend/posters.json` (preserving FAQs, booth assignments, etc.)
- Update timestamps
- Validate the result

### 2. Import from JSON

```bash
python extract_posters.py --source json --input new_posters.json --merge
```

The JSON file can be either:
- An array of poster objects: `[{...}, {...}]`
- A full posters.json structure: `{"posters": [{...}], ...}`

### 3. Replace All Data (Use with Caution)

```bash
python extract_posters.py --source csv --input posters.csv --replace
```

This will completely replace `backend/posters.json` with new data. **Warning**: This will lose all manually curated FAQs and booth assignments!

### 4. Validate Existing Data

```bash
python extract_posters.py --validate
```

This validates the current `backend/posters.json` against required fields.

## CSV Format

The CSV file should have the following columns:

| Column | Required | Description | Example |
|--------|----------|-------------|---------|
| `id` | Yes | Unique poster ID | `poster_001` |
| `title` | Yes | Poster title | `Edge AI for Robotics` |
| `authors` | Yes | Semicolon-separated authors | `Alice Johnson;Bob Smith` |
| `tags` | Yes | Semicolon-separated tags | `edge-ai;robotics;ml` |
| `abstract` | Yes | Poster description | `This poster presents...` |
| `poster_image` | Yes | Godot resource path | `res://assets/posters/image.png` |
| `keywords` | No | Semicolon-separated keywords | `cv;embedded;tensorflow` |
| `contact_email` | No | Contact email | `alice@rise.se` |

See `example_posters.csv` for a complete example.

## Metadata Fields

Each poster in `backend/posters.json` has the following structure:

### Required Fields
- `id`: Unique identifier
- `title`: Full poster title
- `authors`: Array of author names
- `tags`: Array of topic tags (used by guide agent)
- `abstract`: Full description
- `poster_image`: Path to image file (Godot resource format)

### Optional Fields (Preserved During Updates)
- `faq`: Array of Q&A objects (manually curated)
- `room`: Room identifier (e.g., "corridor_1", "room_2")
- `booth_id`: Booth identifier (e.g., "booth_001")
- `keywords`: Additional searchable keywords
- `contact_email`: Author contact
- `related_links`: Array of related resources

### Metadata Tracking
- `metadata.created_at`: When this entry was first created
- `metadata.updated_at`: When last modified
- `metadata.source`: Data source (e.g., "csv_import", "manual", "pdf_extract")
- `metadata.version`: Version string

## How Merging Works

When you import data with `--merge` (default):

1. **Load** existing `backend/posters.json`
2. **For each imported poster**:
   - If poster ID exists:
     - **Update** basic fields (title, abstract, authors, tags, image)
     - **Preserve** FAQs, booth_id, room assignments from existing data
     - **Update** `metadata.updated_at` timestamp
   - If poster ID is new:
     - **Add** as new poster with `metadata.created_at` timestamp
3. **Keep** existing posters not in import file (no deletions)
4. **Validate** all posters
5. **Save** to `backend/posters.json`

### Example Merge Scenario

Existing data (manually curated):
```json
{
  "id": "poster_001",
  "title": "Edge AI for Robotics",
  "abstract": "Old abstract...",
  "faq": [{"question": "Q1?", "answer": "A1"}],
  "booth_id": "booth_001"
}
```

Import data (from CSV):
```json
{
  "id": "poster_001",
  "title": "Edge AI for Robotics (Updated)",
  "abstract": "New abstract with more details..."
}
```

Result after merge:
```json
{
  "id": "poster_001",
  "title": "Edge AI for Robotics (Updated)",
  "abstract": "New abstract with more details...",
  "faq": [{"question": "Q1?", "answer": "A1"}],  // Preserved!
  "booth_id": "booth_001",  // Preserved!
  "metadata": {
    "updated_at": "2025-11-15T12:30:00"
  }
}
```

## Best Practices

### Regular Updates
1. Export data from source (conference system, spreadsheet, etc.)
2. Convert to CSV or JSON format
3. Run import with `--merge`
4. Validate with `--validate`
5. Test backend functionality

### Adding FAQs
FAQs should be added manually to `backend/posters.json`:
```json
{
  "id": "poster_001",
  "faq": [
    {
      "question": "What hardware did you use?",
      "answer": "We used Raspberry Pi 4 and Jetson Nano."
    }
  ]
}
```

These will be preserved during subsequent imports.

### Room and Booth Assignments
Similarly, room and booth assignments can be added manually and will be preserved:
```json
{
  "id": "poster_001",
  "room": "corridor_1",
  "booth_id": "booth_001"
}
```

## Troubleshooting

### "Missing required fields" error
Ensure your CSV/JSON has all required fields: id, title, authors, tags, abstract, poster_image

### FAQs disappearing after import
Make sure you're using `--merge` (default) and not `--replace`

### Validation fails after import
Check the log output for specific validation errors. Common issues:
- Missing required fields
- Invalid JSON structure
- Duplicate poster IDs

### Import seems to ignore my updates
Check that the poster IDs match exactly. The merge is based on ID matching.

## Future Enhancements

- **PDF extraction**: Automatically extract metadata from poster PDFs
- **Image validation**: Verify poster image files exist
- **Duplicate detection**: Find and warn about similar posters
- **Batch operations**: Update multiple fields across all posters
- **Data enrichment**: Auto-generate tags and keywords using LLM
