# OpenSpoofen Pi 3 Case

This folder contains a simple Raspberry Pi 3 printable case in OpenSCAD with an embossed OpenSpoofen ghost lid.

## Files

- `extract_ghost_logo.py`: removes the white background from the existing repo logo and generates a silhouette SVG for embossing.
- `assets/ghost_isolated.png`: transparent ghost-only export generated from the repo logo.
- `assets/ghost_silhouette.svg`: silhouette used by OpenSCAD for the raised lid badge.
- `assets/ghost_logo_layers_generated.scad`: generated OpenSCAD include containing the colored logo layer imports.
- `assets/ghost_layer_*.svg`: generated non-white color layers used for the shallow raised logo details.
- `openspoofen_pi3_case.scad`: parametric case model for preview and STL export.

## Rebuild the logo assets

```powershell
c:/openspoofen/.venv/Scripts/python.exe .\designs\pi3-case\extract_ghost_logo.py
```

## Open the model locally

```powershell
openscad .\designs\pi3-case\openspoofen_pi3_case.scad
```

## Export printable parts

```powershell
openscad -o .\designs\pi3-case\openspoofen_pi3_case_base.stl -D 'mode="base"' .\designs\pi3-case\openspoofen_pi3_case.scad
openscad -o .\designs\pi3-case\openspoofen_pi3_case_lid.stl -D 'mode="lid"' .\designs\pi3-case\openspoofen_pi3_case.scad
```

The geometry is intentionally simple and should be treated as a first printable prototype rather than a production enclosure.