# Spatial and control review

## Metadata before geometry

A horizontal CRS label alone does not define vertical heights. Distinguish ellipsoidal height, orthometric height, a named geoid realization and a local benchmark datum. Record units and epoch where applicable. Do not apply a generic geoid offset.

CRS authority axis order can differ from the Easting/Northing convention of a point file. Verify the actual file order and transformation pipeline. Assigning a CRS label does not transform coordinates. Never silently swap E/N merely to make a drawing look plausible.

For linear coordinates, international feet and historical US survey feet differ. Keep the declared definition through review; the latter's deprecation does not convert historical data automatically. Avoid treating degrees as metres.

## Control evidence

Use stable IDs or documented correspondences. For a point and its reference in the same coordinate basis:
- dE = observed E - reference E; dN = observed N - reference N.
- Horizontal residual = sqrt(dE squared + dN squared); vertical residual = observed Z - reference Z.
- Compare to the project's provided tolerances. Record whether a transform was fitted and whether independent check points were withheld.
- A common offset is a diagnostic clue, not permission to translate observations.
- Traverse/level closure requires the observation sequence and proper network context. An unordered XYZ list cannot establish instrument accuracy or closure.

These formulas are diagnostic definitions, not a national acceptance standard.

## Surface readiness

Plot labeled points and codes; inspect density, gaps, duplicate XY with differing Z, isolated groups and abrupt levels against known features. Review breakline connectivity and boundaries before triangulation. Genuine steps/retaining walls can resemble outliers; retain evidence until reviewed.

LandXML and large point clouds need format-aware inspection; do not feed them into the CSV helper. CRS transformations, geoid corrections and network adjustment are separate scoped operations using suitable free tools such as PROJ/QGIS.

## Sources

Checked 2026-10-15:
- [PROJ axis-order FAQ](https://proj.org/en/stable/faq.html): authority axis conventions.
- [PROJ axis swap](https://proj.org/en/stable/operations/conversions/axisswap.html): explicit pipeline ordering.
- [NOAA NGS conversion definitions, Appendix D](https://www.ngs.noaa.gov/DATASHEET/dsdata.pdf): international ft = 0.3048 m; US survey ft = 1200/3937 m.
- [NIST US survey foot](https://www.nist.gov/pml/us-surveyfoot): historical data considerations.

No project standard, Malaysian tolerance, coordinate system or national-annex value is supplied by this skill.
