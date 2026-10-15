# Comparison contract

## Matched point helper

The standard-library helper takes JSON:
~~~json
{
  "design": {
    "frame": "Project grid A / benchmark BM1 / agreed epoch",
    "units": "m",
    "points": [{"id": "001", "e": 100, "n": 200, "z": 3}]
  },
  "observed": {
    "frame": "Project grid A / benchmark BM1 / agreed epoch",
    "units": "m",
    "points": [{"id": "001", "e": 100.01, "n": 200, "z": 3.002}]
  },
  "tolerances_m": {"horizontal": 0.02, "vertical": 0.01}
}
~~~
~~~text
python scripts/compare_points.py comparison.json
~~~
Output is JSON on stdout. Units m/mm/ft/us-ft are explicit; one unit applies to all three axes per dataset. frame labels must be equal and nonempty, but matching labels do not independently establish geodetic correctness. No coordinate transformation or registration occurs.

IDs must be unique strings; leading zeros are retained. Numeric input must be finite. Deltas are observed minus design; horizontal magnitude uses E/N, vertical uses signed Z. Supplied horizontal and vertical tolerances are inclusive and separately applied. Without both criteria the result remains not-assessed even if some checks are within tolerance; any exceeded supplied criterion is flagged.

The report retains missing/unexpected IDs and never nearest-matches them. stdout output is read-only; save reports to a new destination, not an input.

## Scan/surface route

CloudCompare cloud-to-mesh signed distance depends on mesh normals. It is not automatically vertical cut/fill or the separate E/N/Z components. Its maximum-distance setting can cap returned distances; capped observations must not be represented as exact measurements. Approximate preview distances are not final results.

Review target-surface selection, coverage, occluded regions, residual registration, reference mesh quality and edge effects. A uniform apparent shift can be a datum/control issue; investigate rather than automatically moving the survey.

## Sources

Reviewed 2026-10-15:
- [CloudCompare cloud-to-mesh](https://www.cloudcompare.org/doc/wiki/index.php/Cloud-to-Mesh_Distance).
- [PROJ axis order](https://proj.org/en/stable/faq.html): coordinate contracts.
- [NOAA unit definitions](https://www.ngs.noaa.gov/DATASHEET/dsdata.pdf): international versus US survey feet.

The helper compares explicit point pairs only. It does not execute CloudCompare, prove measurement accuracy or derive contractual tolerances.
