# How to Apply Poster Images in Godot

I've already generated placeholder poster images for you! Here's how to apply them.

## ✅ What's Already Done

- ✓ 5 poster images created in `client-godot/assets/posters/`
- ✓ Images include titles, authors, abstracts, and tags
- ✓ Each poster is 1200x1600 pixels (portrait orientation)

## Method 1: Automatic (EASIEST) ⭐

### Step 1: Open the Scene

In Godot:
1. Open your project
2. Open `scenes/environment/main.tscn`

### Step 2: Run the Helper Script

1. Go to **File** → **Run Script** (or press **Ctrl+Shift+X**)
2. Navigate to `res://scripts/apply_poster_materials.gd`
3. Click **Open**
4. The script will automatically apply all poster textures!
5. You'll see output like:
   ```
   ✓ Applied res://assets/posters/poster_001.png to PosterBooth1
   ✓ Applied res://assets/posters/poster_002.png to PosterBooth2
   ...
   ✓ Applied materials to 5 poster booths
   ```

### Step 3: Save

- Press **Ctrl+S** to save the scene
- Done! Run the game (F5) to see the posters

---

## Method 2: Manual (If Automatic Fails)

### For Each Poster Booth:

1. **Select the booth** in the Scene tree (e.g., `PosterBooth1`)
2. **Expand it** and click on the **PosterMesh** child
3. In the **Inspector** (right panel):
   - Find **Material** section
   - Click **Surface Material Override** → **New StandardMaterial3D**
   - Click on the material you just created to edit it
4. In the material properties:
   - Expand **Albedo**
   - Click the dropdown next to **Texture**
   - Choose **Load**
   - Select `res://assets/posters/poster_001.png` (matching the booth's poster_id)
5. Optional: Set **Shading Mode** to **Unshaded** for flat, always-visible posters
6. Optional: Set **Cull Mode** to **Disabled** to see the poster from both sides

Repeat for all 5 booths!

---

## Customizing the Images

### Want to Regenerate with Different Settings?

Edit `data-prep/generate_poster_images.py`:

```python
# Change size
def create_poster_image(poster_data: dict, output_path: Path, size=(1920, 1080)):

# Change colors
draw.rectangle([(0, 0), (size[0], 200)], fill='#FF5733')  # Different header color
```

Then run:
```bash
cd data-prep
python generate_poster_images.py
```

### Using Your Own Poster PDFs/Images

1. Export your posters as PNG or JPG
2. Resize them to ~1200x1600 or similar
3. Name them `poster_001.png`, `poster_002.png`, etc.
4. Replace the files in `client-godot/assets/posters/`
5. Re-run the automatic script or manually update materials

---

## Adjusting in Godot

### Make Posters Bigger/Smaller

1. Select the **PosterMesh** node
2. In the Inspector, adjust the **Mesh → Size** property
   - Current: 1.5 x 2.0 x 0.05
   - Try: 2.0 x 3.0 x 0.05 for bigger posters

### Adjust Poster Position

1. Select the **PosterMesh** node
2. Use the **Transform** gizmo in the viewport
3. Or edit **Transform → Position** in the Inspector

### Change Title Position

1. Select the **Label3D** node
2. Adjust **Transform → Position** (Y-axis)
3. Edit **Text** property to change the title

---

## Troubleshooting

### Images not showing in FileSystem

- Reimport: Right-click `assets/posters/` → **Reimport**
- Restart Godot

### Black/missing textures

- Check the texture path is correct
- Make sure **Albedo Color** is white (1, 1, 1, 1)
- Try different **Filter** settings in the texture import

### Posters too dark

- Set **Shading Mode** to **Unshaded**
- Or add more lights to the scene

### Script fails with errors

- Make sure `scenes/environment/main.tscn` is open
- Check that booth nodes have `poster_id` property set
- Verify images exist in `res://assets/posters/`

---

## Next Steps

- **Add lighting** to make posters more visible
- **Add frames** around posters (duplicate the Stand mesh)
- **Create custom poster designs** in design software
- **Add interactive highlights** when player looks at posters

Enjoy your virtual open house! 🎨
