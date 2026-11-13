"""Import named shot markers from a CSV into the active Blender scene."""
import argparse
import csv
import sys
from pathlib import Path


def read_markers(path):
    markers = {}
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != ["frame", "name"]:
            raise ValueError("CSV header must be frame,name")
        for row in reader:
            if None in row or row["name"] is None:
                raise ValueError(f"Line {reader.line_num}: expected two columns")
            try:
                frame = int(row["frame"])
            except ValueError as error:
                raise ValueError(f"Line {reader.line_num}: frame must be an integer") from error
            name = row["name"].strip()
            if not name or len(name.encode("utf-8")) > 63 or "\x00" in name:
                raise ValueError(f"Line {reader.line_num}: invalid marker name")
            if name in markers:
                raise ValueError(f"Line {reader.line_num}: duplicate marker {name!r}")
            markers[name] = frame
    return markers


def import_markers(scene, markers):
    existing = {}
    for marker in scene.timeline_markers:
        existing.setdefault(marker.name, []).append(marker)
    for name in markers:
        if len(existing.get(name, [])) > 1:
            raise ValueError(f"Scene contains multiple markers named {name!r}")
    for name, frame in markers.items():
        if name in existing:
            existing[name][0].frame = frame
        else:
            scene.timeline_markers.new(name, frame=frame)


def main():
    import bpy

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("csv", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
    output = args.output.resolve()
    if output.suffix.lower() != ".blend" or not output.parent.is_dir():
        parser.error("--output must be a .blend path in an existing directory")
    if output.exists():
        parser.error("--output must be a new file")
    markers = read_markers(args.csv)
    limits = bpy.types.TimelineMarker.bl_rna.properties["frame"]
    for name, frame in markers.items():
        if not limits.hard_min <= frame <= limits.hard_max:
            parser.error(f"Frame {frame} for {name!r} is outside Blender's supported range")
    import_markers(bpy.context.scene, markers)
    bpy.ops.wm.save_as_mainfile(filepath=str(output), copy=True)
    print(f"Imported {len(markers)} markers to {output}")


if __name__ == "__main__":
    main()
