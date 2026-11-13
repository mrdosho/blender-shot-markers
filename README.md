# Blender Shot Markers

Import shot timing from a CSV into the timeline of the active scene. Run with Blender 4.x or 5.x. The script uses Blender's bundled Python.

```sh
blender -b scene.blend --python-exit-code 1 --python import_markers.py -- example.csv --output scene-with-markers.blend
```

Use an output path that does not already exist. The source scene stays on disk and the script saves a separate .blend file. CSV columns are `frame,name`. A unique existing marker with the same name moves to the supplied frame. Other markers stay in place. Distinct names can share a frame.

MIT licensed.
