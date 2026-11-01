# Flashforge Adventurer 5M Workflow

This package is organized for a single-color prototype print on a Flashforge Adventurer 5M.

## What to open in the slicer

- `openspoofen_pi3_case_base.stl`
- `openspoofen_pi3_case_lid.stl`

## Recommended first print setup

- Printer: Flashforge Adventurer 5M
- Slicer: Orca-Flashforge
- Nozzle: 0.4 mm
- Material: PLA
- Layer height: 0.20 mm
- Print the base flat on its bottom
- Print the lid with the exterior top face down on the plate for the cleanest visible surface

## Estimated print time on an Adventurer 5M

These estimates assume a normal PLA prototype setup on the 0.4 mm nozzle at 0.20 mm layer height.

- Base only: roughly 1 hour 15 minutes to 1 hour 45 minutes
- Lid only: roughly 50 minutes to 1 hour 20 minutes
- Both in one combined plate: roughly 2 hours 15 minutes to 3 hours

The exact time depends on your chosen speed profile, wall count, infill, first-layer speed, and whether the building printer operator has modified the default profile.

## Separate jobs or one combined job?

Both parts fit on the Adventurer 5M build plate in one session, so either approach works.

Preferred for a first prototype: separate jobs.

Why separate is safer:

- less material is wasted if one part fails
- easier for a first-time user to monitor and remove parts cleanly
- easier to reprint only the lid or only the base if fit needs tuning

Use one combined job only if you specifically want to minimize printer visits and are comfortable with the higher risk of losing both parts in one failed print.

## What to save to USB for the printer

Do not put the STL directly into the printer.

1. Open the STL files in Orca-Flashforge.
2. Choose the Adventurer 5M printer profile.
3. Slice the parts.
4. Save the sliced printer file into the `04_SLICED_OUTPUT_TO_USB` folder.
5. Copy that sliced file to the USB drive used with the printer.

## Important note about color

The printer is being used in single-color mode.
The colored ghost on the lid is only for model preview and design reference.
The actual print will come out in the single filament color loaded in the printer unless you manually redesign the logo as separate parts or do filament swaps.